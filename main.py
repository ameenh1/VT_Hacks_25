from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Gemini Chatbot API", version="1.0.0")

# Configure Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables")
    raise ValueError("Please set GEMINI_API_KEY in your .env file")

genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model
try:
    model = genai.GenerativeModel('gemini-2.5-flash')
    logger.info("Gemini model initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gemini model: {e}")
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
    """Handle chat messages and return Gemini AI responses"""
    try:
        if not message.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        logger.info(f"Received message: {message.message[:50]}...")
        
        # Generate response using Gemini
        response = model.generate_content(message.message)
        
        if not response.text:
            raise HTTPException(status_code=500, detail="No response generated from Gemini")
        
        logger.info("Successfully generated response")
        return ChatResponse(response=response.text, status="success")
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test the Gemini API with a simple prompt
        test_response = model.generate_content("Hello, are you working?")
        if test_response.text:
            return {"status": "healthy", "gemini_api": "connected"}
        else:
            return {"status": "unhealthy", "gemini_api": "no_response"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)