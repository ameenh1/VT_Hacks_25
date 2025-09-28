"""
Customer Agent Server
====================

Standalone FastAPI server for the customer-facing chatbot.
This server handles all customer interactions and conversation flows
independently from the ATTOM bridge API.

Features:
- Chatbot session management
- Real-time conversation handling
- User preference collection
- Clean API endpoints for frontend integration

Author: VT Hacks 25 Team
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import uvicorn
from datetime import datetime
import asyncio

# Import the customer agent
from agents.customer_agent import CustomerAgent, FrontendPreferences as AgentFrontendPreferences
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API key from environment variables
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.error("❌ GEMINI_API_KEY not found in environment variables!")
    logger.error("💡 Make sure your .env file contains: GEMINI_API_KEY=your_api_key_here")
    raise ValueError("GEMINI_API_KEY is required")

logger.info("✅ Successfully loaded GEMINI_API_KEY from environment")

# Initialize FastAPI app
app = FastAPI(
    title="EquityNest Customer Agent API",
    description="Customer-facing chatbot API for real estate investment guidance",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for web applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests/responses
class FrontendPreferences(BaseModel):
    location: Optional[str] = None
    property_types: List[str] = []
    budget_min: Optional[int] = None
    budget_max: Optional[int] = None

class ChatStartRequest(BaseModel):
    user_id: Optional[str] = None
    frontend_data: Optional[FrontendPreferences] = None

class ChatStartResponse(BaseModel):
    session_id: str
    message: str
    status: str

class ChatMessageRequest(BaseModel):
    session_id: str
    message: str

class ChatMessageResponse(BaseModel):
    session_id: str
    message: str
    current_step: str
    completed: bool
    preferences_collected: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    active_sessions: int

# Initialize customer agent with a mock deal finder callback
def deal_finder_callback(preferences):
    """Mock callback function for when chatbot collects user preferences"""
    logger.info(f"User preferences collected: {preferences}")
    # In a real implementation, this would trigger property search logic
    return {
        "status": "preferences_received", 
        "preferences": preferences,
        "message": "Great! I've collected your preferences. Let me find some properties for you..."
    }

# Initialize the customer agent
customer_agent = CustomerAgent(api_key=api_key, deal_finder_callback=deal_finder_callback)

# API Endpoints

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "service": "EquityNest Customer Agent API",
        "status": "active",
        "version": "1.0.0"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        active_sessions=len(customer_agent.active_sessions)
    )

@app.post("/chat/start", response_model=ChatStartResponse)
async def start_chat(request: ChatStartRequest):
    """Start a new chatbot session"""
    try:
        # Convert frontend data format if provided
        agent_frontend_data = None
        if request.frontend_data:
            agent_frontend_data = AgentFrontendPreferences(
                location=request.frontend_data.location,
                property_types=request.frontend_data.property_types,
                budget_min=request.frontend_data.budget_min,
                budget_max=request.frontend_data.budget_max
            )
        
        # Start a new chatbot session with frontend data
        session = customer_agent.start_chatbot_session(frontend_data=agent_frontend_data)
        
        # Get the initial greeting message - customize based on pre-filled data
        if agent_frontend_data:
            # Create a personalized greeting that acknowledges the form data
            prefilled_info = []
            if agent_frontend_data.location:
                prefilled_info.append(f"properties in {agent_frontend_data.location}")
            if agent_frontend_data.property_types:
                types_friendly = {
                    'primary-residence': 'a primary residence',
                    'fix-flip': 'fix and flip opportunities',
                    'rental-property': 'rental properties',
                    'multi-family': 'multi-family properties',
                    'quick-deals': 'quick wholesale deals'
                }
                type_names = [types_friendly.get(t, t) for t in agent_frontend_data.property_types]
                if len(type_names) == 1:
                    prefilled_info.append(f"looking for {type_names[0]}")
                else:
                    prefilled_info.append(f"interested in {', '.join(type_names[:-1])} and {type_names[-1]}")
            
            if agent_frontend_data.budget_min or agent_frontend_data.budget_max:
                budget_parts = []
                if agent_frontend_data.budget_min:
                    budget_parts.append(f"${agent_frontend_data.budget_min:,}")
                if agent_frontend_data.budget_max:
                    budget_parts.append(f"${agent_frontend_data.budget_max:,}")
                budget_str = " - ".join(budget_parts) if len(budget_parts) == 2 else f"up to {budget_parts[0]}" if budget_parts else ""
                if budget_str:
                    prefilled_info.append(f"with a budget of {budget_str}")
            
            context = ", ".join(prefilled_info) if prefilled_info else "your investment goals"
            
            initial_message = f"""👋 Hi there! I see you're interested in {context}. That's exciting!

I'm your EquityNest assistant, and I'm here to help you find the perfect real estate investment opportunities. I've noted your preferences from the form, and I'd love to learn more about what you're looking for.

What's driving your interest in real estate investing right now? Are you looking to get started, or are you expanding an existing portfolio?"""
        else:
            initial_message = """👋 Hi there! I'm your EquityNest assistant, and I'm here to help you find the perfect real estate investment opportunities.

I'll ask you a few questions to understand what you're looking for, and then I can help you discover properties that match your investment goals.

Ready to get started? Tell me a bit about what kind of property investment you're interested in!"""

        logger.info(f"Started new chat session: {session.session_id}")
        
        return ChatStartResponse(
            session_id=session.session_id,
            message=initial_message,
            status="active"
        )
        
    except Exception as e:
        logger.error(f"Error starting chat session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start chat session: {str(e)}")

@app.post("/chat/message", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest):
    """Send a message to the chatbot and get a response"""
    try:
        # Validate session exists
        if request.session_id not in customer_agent.active_sessions:
            raise HTTPException(status_code=404, detail="Chat session not found. Please start a new session.")
        
        # Get the session
        session = customer_agent.active_sessions[request.session_id]
        
        # Process the message
        response_message = await customer_agent.handle_chatbot_message(
            request.session_id, 
            request.message
        )
        
        # Check if preferences collection is complete
        completed = session.current_step.value == "handoff"
        preferences_collected = None
        
        if completed:
            # Convert preferences to a serializable format
            preferences_collected = {
                "location_preferences": session.user_preferences.location_preferences,
                "property_preferences": session.user_preferences.property_preferences,
                "financial_preferences": session.user_preferences.financial_preferences,
                "timeline_preferences": session.user_preferences.timeline_preferences
            }
        
        return ChatMessageResponse(
            session_id=request.session_id,
            message=response_message,
            current_step=session.current_step.value,
            completed=completed,
            preferences_collected=preferences_collected
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@app.get("/chat/{session_id}/status")
async def get_chat_status(session_id: str):
    """Get the current status of a chat session"""
    try:
        if session_id not in customer_agent.active_sessions:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        session = customer_agent.active_sessions[session_id]
        
        return {
            "session_id": session_id,
            "current_step": session.current_step.value,
            "message_count": len(session.conversation_history),
            "completed": session.current_step.value == "handoff",
            "created_at": session.session_id  # This contains timestamp info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get chat status: {str(e)}")

@app.delete("/chat/{session_id}")
async def end_chat(session_id: str):
    """End a chat session"""
    try:
        if session_id in customer_agent.active_sessions:
            del customer_agent.active_sessions[session_id]
            logger.info(f"Ended chat session: {session_id}")
            return {"status": "session_ended", "session_id": session_id}
        else:
            raise HTTPException(status_code=404, detail="Chat session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending chat session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to end chat session: {str(e)}")

@app.get("/chat/{session_id}/deal-finder-data")
async def get_deal_finder_data(session_id: str):
    """Get structured data for deal_finder agent"""
    try:
        deal_finder_data = customer_agent.get_session_deal_finder_data(session_id)
        
        if not deal_finder_data:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        return {
            "status": "success",
            "session_id": session_id,
            "deal_finder_data": deal_finder_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting deal finder data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get deal finder data: {str(e)}")

@app.post("/chat/{session_id}/trigger-deal-finder")
async def trigger_deal_finder(session_id: str):
    """Trigger handoff to deal_finder agent"""
    try:
        result = customer_agent.trigger_deal_finder_handoff(session_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "status": "success",
            "session_id": session_id,
            "handoff_result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering deal finder: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger deal finder: {str(e)}")

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "customer_agent_server:app",
        host="0.0.0.0",
        port=8001,  # Different port from ATTOM bridge
        reload=True,
        log_level="info"
    )