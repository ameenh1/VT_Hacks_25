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
from typing import Dict, Any, Optional
import logging
import uvicorn
from datetime import datetime
import asyncio

# Import the customer agent
from agents.customer_agent import CustomerAgent
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
class ChatStartRequest(BaseModel):
    user_id: Optional[str] = None

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
        # Start a new chatbot session
        session = customer_agent.start_chatbot_session()
        
        # Get the initial greeting message
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
                "budget_preferences": session.user_preferences.budget_preferences,
                "investment_strategy": session.user_preferences.investment_strategy.value if session.user_preferences.investment_strategy else None,
                "timeline": session.user_preferences.timeline
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

# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "customer_agent_server:app",
        host="0.0.0.0",
        port=8001,  # Different port from ATTOM bridge
        reload=True,
        log_level="info"
    )