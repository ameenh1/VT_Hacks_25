from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging
import asyncio
from typing import Optional, Dict, Any
import uuid

# Import our custom modules
from agents.analysis_engine import AnalysisEngine
from agents.customer_agent import CustomerAgent
from agents.deal_finder import DealFinder
from agents.coordinator import get_agent_coordinator, analyze_property_quick
from models.data_models import (
    QuickAnalysisRequest, QuickAnalysisResponse, AnalysisAPIRequest, 
    AnalysisAPIResponse, SystemHealthStatus, AgentType
)
from integrations.attom_api import ATTOMDataBridge
from integrations.attom_bridge_service import get_attom_bridge_service, ATTOMBridgeService
from integrations.attom_bridge_service import (
    PropertySearchCriteria, PropertyValuationRequest, MarketAnalysisRequest,
    PropertyResponse, PropertyListResponse, ValuationResponse, MarketAnalysisResponse
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Real Estate Investment AI Platform", 
    version="1.0.0",
    description="3-Agent AI architecture for real estate investment analysis using Gemini models"
)

# Configure Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ATTOM_API_KEY = os.getenv("ATTOM_API_KEY")

if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables")
    raise ValueError("Please set GEMINI_API_KEY in your .env file")

genai.configure(api_key=GEMINI_API_KEY)

# Initialize AI agents
analysis_engine = None
customer_agent = None
deal_finder = None
attom_bridge = None
attom_bridge_service = None  # New ATTOM bridge service
coordinator = get_agent_coordinator()

@app.on_event("startup")
async def startup_event():
    """Initialize agents and services on startup"""
    global analysis_engine, customer_agent, deal_finder, attom_bridge, attom_bridge_service
    
    try:
        # Initialize ATTOM Data Bridge if API key is available
        if ATTOM_API_KEY:
            attom_bridge = ATTOMDataBridge(ATTOM_API_KEY)
            attom_bridge_service = get_attom_bridge_service(ATTOM_API_KEY)
            logger.info("ATTOM Data Bridge and Bridge Service initialized")
        else:
            logger.warning("ATTOM_API_KEY not found - using mock data for property analysis")
        
        # Initialize Analysis Engine (Agent 2) with ATTOM bridge service
        analysis_engine = AnalysisEngine(GEMINI_API_KEY, attom_bridge_service)
        
        # Initialize Customer Agent (Agent 1)
        customer_agent = CustomerAgent(GEMINI_API_KEY)
        
        # Initialize Deal Finder (Agent 3)
        deal_finder = DealFinder(attom_bridge, analysis_engine)
        
        # Register agents with coordinator
        coordinator.register_agent(AgentType.ANALYSIS_ENGINE, analysis_engine)
        coordinator.register_agent(AgentType.CUSTOMER_AGENT, customer_agent)
        coordinator.register_agent(AgentType.DEAL_FINDER, deal_finder)
        
        # Start Deal Finder background monitoring
        await deal_finder.start_monitoring()
        
        logger.info("Real Estate AI Platform initialized successfully")
        logger.info("All 3 agents are now active:")
        logger.info("  - Agent 1: Customer Agent (Gemini 2.5 Flash)")
        logger.info("  - Agent 2: Analysis Engine (Gemini 1.5 Pro)")
        logger.info("  - Agent 3: Deal Finder (Background Service)")
        
    except Exception as e:
        logger.error(f"Failed to initialize AI platform: {e}")
        raise

@app.on_event("shutdown") 
async def shutdown_event():
    """Graceful shutdown"""
    global coordinator, deal_finder
    
    if deal_finder:
        await deal_finder.stop_monitoring()
    
    await coordinator.shutdown()
    logger.info("Platform shutdown complete")

# Initialize the customer-facing model (Agent 1 - will be replaced by CustomerAgent)
try:
    customer_model = genai.GenerativeModel('gemini-2.5-flash')
    logger.info("Customer Agent model initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize customer model: {e}")
    raise

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    status: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main chat interface"""
    try:
        return FileResponse("static/index.html")
    except FileNotFoundError:
        return HTMLResponse("""
        <html>
            <head><title>Gemini Chatbot</title></head>
            <body>
                <h1>Gemini Chatbot</h1>
                <p>Frontend not found. Please create static/index.html</p>
            </body>
        </html>
        """)

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Handle chat messages using Customer Agent (Agent 1)"""
    try:
        if not message.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        logger.info(f"Received message: {message.message[:50]}...")
        
        # Use Customer Agent if available, otherwise fallback to direct model
        if customer_agent:
            response_text = await customer_agent.handle_general_query(message.message)
        else:
            # Fallback to direct Gemini model
            response = customer_model.generate_content(
                f"You are a friendly real estate investment assistant. "
                f"Help explain real estate concepts in simple terms. "
                f"User question: {message.message}"
            )
            response_text = response.text
        
        if not response_text:
            raise HTTPException(status_code=500, detail="No response generated")
        
        logger.info("Successfully generated response")
        return ChatResponse(response=response_text, status="success")
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check all agents
        customer_status = "not_initialized"
        analysis_status = "not_initialized" 
        deal_finder_status = "not_initialized"
        
        if customer_agent:
            customer_health = await customer_agent.health_check()
            customer_status = customer_health.get("status", "unknown")
        
        if analysis_engine:
            analysis_status = "connected"
        
        if deal_finder:
            deal_finder_health = await deal_finder.health_check()
            deal_finder_status = deal_finder_health.get("status", "unknown")
        
        # Check ATTOM API status
        attom_status = "not_configured"
        if attom_bridge:
            attom_health = await attom_bridge.health_check()
            attom_status = attom_health.get("status", "unknown")
        
        # Get coordinator metrics
        coordinator_metrics = coordinator.get_system_metrics()
        
        return {
            "status": "healthy",
            "agents": {
                "customer_agent": customer_status,
                "analysis_engine": analysis_status,
                "deal_finder": deal_finder_status
            },
            "integrations": {
                "gemini_api": customer_status,
                "attom_api": attom_status
            },
            "coordinator_metrics": coordinator_metrics
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

# === NEW REAL ESTATE ANALYSIS ENDPOINTS ===

@app.post("/api/analyze/quick", response_model=QuickAnalysisResponse)
async def quick_property_analysis(request: QuickAnalysisRequest):
    """Quick property analysis using Analysis Engine (Agent 2)"""
    try:
        if not analysis_engine:
            raise HTTPException(status_code=503, detail="Analysis Engine not available")
        
        logger.info(f"Quick analysis requested for: {request.address}")
        
        # Use the analysis engine directly for quick analysis
        result = await analysis_engine.quick_analysis(
            request.address, 
            request.listing_price
        )
        
        # Convert to response model
        response = QuickAnalysisResponse(
            address=result["address"],
            deal_score=result["deal_score"],
            investment_potential=result["investment_potential"],
            arv_estimate=result["arv_estimate"],
            recommended_strategy=result["recommended_strategy"],
            monthly_cash_flow=result["monthly_cash_flow"],
            key_insight=result["key_insight"],
            confidence_score=result.get("confidence_score", 0.8)
        )
        
        logger.info(f"Quick analysis completed for {request.address}")
        return response
        
    except Exception as e:
        logger.error(f"Quick analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/analyze/comprehensive", response_model=AnalysisAPIResponse)
async def comprehensive_property_analysis(request: AnalysisAPIRequest, background_tasks: BackgroundTasks):
    """Comprehensive property analysis using Analysis Engine"""
    try:
        if not analysis_engine:
            raise HTTPException(status_code=503, detail="Analysis Engine not available")
        
        analysis_id = str(uuid.uuid4())
        logger.info(f"Comprehensive analysis requested for: {request.property_address} (ID: {analysis_id})")
        
        # For now, return quick analysis - full comprehensive analysis would be implemented
        # as a background task with proper ATTOM data integration
        result = await analysis_engine.quick_analysis(
            request.property_address,
            request.listing_price
        )
        
        response = AnalysisAPIResponse(
            status="success",
            analysis_id=analysis_id,
            property_analysis=result,  # This would be a full PropertyAnalysis object
            processing_time_seconds=2.5
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Comprehensive analysis failed: {e}")
        return AnalysisAPIResponse(
            status="error",
            analysis_id=str(uuid.uuid4()),
            error_message=str(e)
        )

@app.get("/api/analyze/status/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """Get status of a running analysis"""
    # Placeholder for analysis status tracking
    return {
        "analysis_id": analysis_id,
        "status": "completed",
        "progress_percentage": 100,
        "estimated_completion_time": None
    }

@app.get("/api/agent/coordinator/metrics")
async def get_coordinator_metrics():
    """Get agent coordinator system metrics"""
    try:
        metrics = coordinator.get_system_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Failed to get coordinator metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system metrics")

@app.get("/api/agent/status/{agent_type}")
async def get_agent_status(agent_type: str):
    """Get status of a specific agent"""
    try:
        # Convert string to AgentType enum
        agent_enum = None
        if agent_type.lower() == "analysis_engine":
            agent_enum = AgentType.ANALYSIS_ENGINE
        elif agent_type.lower() == "customer_agent":
            agent_enum = AgentType.CUSTOMER_AGENT
        elif agent_type.lower() == "deal_finder":
            agent_enum = AgentType.DEAL_FINDER
        else:
            raise HTTPException(status_code=400, detail="Invalid agent type")
        
        status = coordinator.get_agent_status(agent_enum)
        return status
        
    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get agent status")

# === ATTOM DATA ENDPOINTS (when available) ===

@app.get("/api/property/details/{address}")
async def get_property_details(address: str):
    """Get detailed property information from ATTOM Data"""
    try:
        if not attom_bridge:
            raise HTTPException(status_code=503, detail="ATTOM Data API not configured")
        
        property_data = await attom_bridge.get_property_details(address)
        
        if not property_data:
            raise HTTPException(status_code=404, detail="Property not found")
        
        return property_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get property details: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve property data")

@app.get("/api/market/data")
async def get_market_data(county_fips: str, state: str):
    """Get market analytics for a specific area"""
    try:
        if not attom_bridge:
            raise HTTPException(status_code=503, detail="ATTOM Data API not configured")
        
        market_data = await attom_bridge.get_market_data(county_fips, state)
        
        if not market_data:
            raise HTTPException(status_code=404, detail="Market data not found")
        
        return market_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get market data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve market data")

# === DEAL FINDER ENDPOINTS (Agent 3) ===

@app.post("/api/deals/search")
async def search_deals(criteria: Dict[str, Any]):
    """Search for investment deals using Deal Finder (Agent 3)"""
    try:
        if not deal_finder:
            raise HTTPException(status_code=503, detail="Deal Finder not available")
        
        # Convert criteria dict to SearchCriteria object
        from agents.deal_finder import SearchCriteria, InvestmentStrategy
        
        search_criteria = SearchCriteria(
            max_price=criteria.get("max_price"),
            min_deal_score=criteria.get("min_deal_score", 70.0),
            target_locations=criteria.get("target_locations", []),
            property_types=criteria.get("property_types", ["SFR", "CON", "TWH"]),
            min_cash_flow=criteria.get("min_cash_flow")
        )
        
        max_results = criteria.get("max_results", 20)
        deals = await deal_finder.find_deals_now(search_criteria, max_results)
        
        # Convert deals to dict format for JSON response
        deals_data = []
        for deal in deals:
            deals_data.append({
                "alert_id": deal.alert_id,
                "property_address": deal.property_address,
                "alert_type": deal.alert_type.value,
                "priority": deal.priority.value,
                "title": deal.title,
                "description": deal.description,
                "key_metrics": deal.key_metrics,
                "estimated_value": deal.estimated_value,
                "listing_price": deal.listing_price,
                "potential_profit": deal.potential_profit,
                "confidence_score": deal.confidence_score,
                "created_at": deal.created_at.isoformat()
            })
        
        return {
            "status": "success",
            "deals_found": len(deals_data),
            "deals": deals_data,
            "search_criteria": criteria
        }
        
    except Exception as e:
        logger.error(f"Deal search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Deal search failed: {str(e)}")

@app.post("/api/deals/monitor")
async def add_property_monitoring(request: Dict[str, str]):
    """Add a property to monitoring list"""
    try:
        if not deal_finder:
            raise HTTPException(status_code=503, detail="Deal Finder not available")
        
        address = request.get("address")
        if not address:
            raise HTTPException(status_code=400, detail="Address is required")
        
        success = await deal_finder.monitor_specific_property(address)
        
        return {
            "status": "success" if success else "failed",
            "message": f"Property {'added to' if success else 'failed to add to'} monitoring list",
            "address": address
        }
        
    except Exception as e:
        logger.error(f"Failed to add property monitoring: {e}")
        raise HTTPException(status_code=500, detail="Failed to add property monitoring")

@app.get("/api/deals/alerts/{user_id}")
async def get_user_alerts(user_id: str):
    """Get active alerts for a specific user"""
    try:
        if not deal_finder:
            raise HTTPException(status_code=503, detail="Deal Finder not available")
        
        alerts = await deal_finder.get_alerts_for_user(user_id)
        
        # Convert alerts to dict format
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                "alert_id": alert.alert_id,
                "property_address": alert.property_address,
                "alert_type": alert.alert_type.value,
                "priority": alert.priority.value,
                "title": alert.title,
                "description": alert.description,
                "key_metrics": alert.key_metrics,
                "confidence_score": alert.confidence_score,
                "created_at": alert.created_at.isoformat(),
                "expires_at": alert.expires_at.isoformat() if alert.expires_at else None
            })
        
        return {
            "user_id": user_id,
            "active_alerts": len(alerts_data),
            "alerts": alerts_data
        }
        
    except Exception as e:
        logger.error(f"Failed to get user alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alerts")

@app.post("/api/deals/criteria/{user_id}")
async def set_user_criteria(user_id: str, criteria: Dict[str, Any]):
    """Set search criteria for a user"""
    try:
        if not deal_finder:
            raise HTTPException(status_code=503, detail="Deal Finder not available")
        
        from agents.deal_finder import SearchCriteria
        
        search_criteria = SearchCriteria(
            max_price=criteria.get("max_price"),
            min_deal_score=criteria.get("min_deal_score", 70.0),
            target_locations=criteria.get("target_locations", []),
            property_types=criteria.get("property_types", ["SFR", "CON", "TWH"]),
            min_cash_flow=criteria.get("min_cash_flow")
        )
        
        deal_finder.add_user_criteria(user_id, search_criteria)
        
        return {
            "status": "success",
            "message": f"Search criteria set for user {user_id}",
            "criteria": criteria
        }
        
    except Exception as e:
        logger.error(f"Failed to set user criteria: {e}")
        raise HTTPException(status_code=500, detail="Failed to set search criteria")

@app.get("/api/deals/status")
async def get_deal_finder_status():
    """Get Deal Finder monitoring status"""
    try:
        if not deal_finder:
            raise HTTPException(status_code=503, detail="Deal Finder not available")
        
        status = deal_finder.get_monitoring_status()
        return status
        
    except Exception as e:
        logger.error(f"Failed to get Deal Finder status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get status")

# === CUSTOMER AGENT ENDPOINTS (Agent 1) ===

@app.post("/api/chat/explain")
async def explain_analysis(request: Dict[str, Any]):
    """Use Customer Agent to explain analysis results"""
    try:
        if not customer_agent:
            raise HTTPException(status_code=503, detail="Customer Agent not available")
        
        analysis_data = request.get("analysis_data", {})
        explanation = await customer_agent.explain_analysis_results(analysis_data)
        
        return {
            "status": "success",
            "explanation": explanation
        }
        
    except Exception as e:
        logger.error(f"Failed to explain analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate explanation")

@app.post("/api/chat/followup")
async def answer_followup(request: Dict[str, Any]):
    """Answer follow-up questions about property analysis"""
    try:
        if not customer_agent:
            raise HTTPException(status_code=503, detail="Customer Agent not available")
        
        question = request.get("question", "")
        context = request.get("context", {})
        
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")
        
        answer = await customer_agent.answer_followup_question(question, context)
        
        return {
            "status": "success",
            "question": question,
            "answer": answer
        }
        
    except Exception as e:
        logger.error(f"Failed to answer follow-up question: {e}")
        raise HTTPException(status_code=500, detail="Failed to answer question")

@app.post("/api/chat/next-steps")
async def get_next_steps(analysis_data: Dict[str, Any]):
    """Get suggested next steps based on analysis"""
    try:
        if not customer_agent:
            raise HTTPException(status_code=503, detail="Customer Agent not available")
        
        steps = await customer_agent.provide_next_steps(analysis_data)
        
        return {
            "status": "success",
            "next_steps": steps
        }
        
    except Exception as e:
        logger.error(f"Failed to get next steps: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate next steps")

# === DEMO ENDPOINTS ===

@app.get("/api/demo/sample-analysis")
async def demo_sample_analysis():
    """Demo endpoint with sample property analysis"""
    sample_analysis = {
        "address": "123 Sample Street, Blacksburg, VA 24060",
        "deal_score": 78.5,
        "investment_potential": "Good",
        "arv_estimate": 285000,
        "recommended_strategy": "buy_and_hold",
        "monthly_cash_flow": 450.0,
        "key_insights": [
            "Property is undervalued by approximately 12%",
            "Strong rental market in the area",
            "Low maintenance property built in 2015",
            "Good school district increases long-term value"
        ],
        "risk_factors": [
            "Market inventory is slightly high",
            "Interest rate sensitivity"
        ],
        "confidence_score": 0.85
    }
    
    return sample_analysis

@app.get("/api/demo/sample-deals")
async def demo_sample_deals():
    """Demo endpoint showing sample deals from Deal Finder"""
    if deal_finder:
        from agents.deal_finder import SearchCriteria
        demo_criteria = SearchCriteria(max_price=300000, min_deal_score=70.0)
        deals = await deal_finder._generate_mock_deals(demo_criteria, 5)
        
        deals_data = []
        for deal in deals:
            deals_data.append({
                "alert_id": deal.alert_id,
                "property_address": deal.property_address,
                "alert_type": deal.alert_type.value,
                "priority": deal.priority.value,
                "title": deal.title,
                "description": deal.description,
                "key_metrics": deal.key_metrics,
                "confidence_score": deal.confidence_score
            })
        
        return {
            "status": "success",
            "sample_deals": deals_data,
            "note": "These are sample deals generated for demonstration"
        }
    else:
        return {
            "status": "service_unavailable",
            "message": "Deal Finder not initialized",
            "sample_deals": []
        }

@app.get("/api/demo/all-agents")
async def demo_all_agents():
    """Demo endpoint showing all three agents working together"""
    
    # Sample property for analysis
    sample_address = "456 Investment Ave, Blacksburg, VA 24060"
    
    results = {
        "demo_property": sample_address,
        "agent_responses": {}
    }
    
    # Agent 2: Analysis Engine
    if analysis_engine:
        try:
            analysis_result = await analysis_engine.quick_analysis(sample_address, 275000)
            results["agent_responses"]["analysis_engine"] = {
                "agent": "Agent 2: Analysis Engine",
                "model": "Gemini 1.5 Pro",
                "result": analysis_result,
                "status": "success"
            }
        except Exception as e:
            results["agent_responses"]["analysis_engine"] = {
                "agent": "Agent 2: Analysis Engine",
                "status": "error",
                "error": str(e)
            }
    
    # Agent 1: Customer Agent - Explain the analysis
    if customer_agent and "analysis_engine" in results["agent_responses"]:
        try:
            analysis_data = results["agent_responses"]["analysis_engine"].get("result", {})
            explanation = await customer_agent.explain_analysis_results(analysis_data)
            results["agent_responses"]["customer_agent"] = {
                "agent": "Agent 1: Customer Agent",
                "model": "Gemini 2.5 Flash",
                "explanation": explanation,
                "status": "success"
            }
        except Exception as e:
            results["agent_responses"]["customer_agent"] = {
                "agent": "Agent 1: Customer Agent",
                "status": "error", 
                "error": str(e)
            }
    
    # Agent 3: Deal Finder - Find similar deals
    if deal_finder:
        try:
            from agents.deal_finder import SearchCriteria
            criteria = SearchCriteria(max_price=300000, target_locations=["Blacksburg", "VA"])
            deals = await deal_finder.find_deals_now(criteria, 3)
            
            deals_data = []
            for deal in deals[:3]:  # Top 3 deals
                deals_data.append({
                    "property_address": deal.property_address,
                    "alert_type": deal.alert_type.value,
                    "title": deal.title,
                    "key_metrics": deal.key_metrics,
                    "confidence_score": deal.confidence_score
                })
            
            results["agent_responses"]["deal_finder"] = {
                "agent": "Agent 3: Deal Finder",
                "service": "Background Property Monitoring",
                "similar_deals": deals_data,
                "status": "success"
            }
        except Exception as e:
            results["agent_responses"]["deal_finder"] = {
                "agent": "Agent 3: Deal Finder",
                "status": "error",
                "error": str(e)
            }
    
    # System overview
    results["system_overview"] = {
        "total_agents": 3,
        "active_agents": len([k for k, v in results["agent_responses"].items() if v.get("status") == "success"]),
        "architecture": "3-Agent AI Real Estate Investment Platform",
        "models_used": ["Gemini 1.5 Pro", "Gemini 2.5 Flash"],
        "demo_note": "This demonstrates all three agents working together on a single property analysis"
    }
    
    return results


# =============================================================================
# ATTOM BRIDGE API ENDPOINTS
# =============================================================================

@app.post("/api/attom/search", response_model=PropertyListResponse)
async def search_properties_attom(criteria: PropertySearchCriteria):
    """Search for properties using ATTOM Data API"""
    try:
        if not attom_bridge_service:
            raise HTTPException(status_code=503, detail="ATTOM bridge service not available")
        
        logger.info(f"ATTOM property search requested")
        result = await attom_bridge_service.search_properties(criteria)
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.error_message)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ATTOM property search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Property search failed: {str(e)}")


@app.get("/api/attom/property/{address:path}", response_model=PropertyResponse)
async def get_property_details_attom(address: str):
    """Get detailed property information using ATTOM Data API"""
    try:
        if not attom_bridge_service:
            raise HTTPException(status_code=503, detail="ATTOM bridge service not available")
        
        logger.info(f"ATTOM property details requested for: {address}")
        result = await attom_bridge_service.get_property_details(address)
        
        if not result.success:
            raise HTTPException(status_code=404, detail=result.error_message)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ATTOM property details failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get property details: {str(e)}")


@app.post("/api/attom/valuation", response_model=ValuationResponse)
async def get_property_valuation_attom(request: PropertyValuationRequest):
    """Get property valuation with comparable sales using ATTOM Data API"""
    try:
        if not attom_bridge_service:
            raise HTTPException(status_code=503, detail="ATTOM bridge service not available")
        
        logger.info(f"ATTOM property valuation requested for: {request.address}")
        result = await attom_bridge_service.get_property_valuation(request)
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.error_message)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ATTOM property valuation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Property valuation failed: {str(e)}")


@app.post("/api/attom/market-analysis", response_model=MarketAnalysisResponse)
async def get_market_analysis_attom(request: MarketAnalysisRequest):
    """Get market analysis for a location using ATTOM Data API"""
    try:
        if not attom_bridge_service:
            raise HTTPException(status_code=503, detail="ATTOM bridge service not available")
        
        logger.info(f"ATTOM market analysis requested")
        result = await attom_bridge_service.get_market_analysis(request)
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.error_message)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ATTOM market analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Market analysis failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)