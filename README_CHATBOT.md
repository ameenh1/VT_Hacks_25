# EquityNest Chatbot Widget Integration

## Overview

This integration adds a sophisticated chatbot widget to the EquityNest frontend that connects users with the customer agent for personalized real estate investment guidance.

## Features

🤖 **Smart Conversational Flow**: Multi-step conversation that collects user preferences
💬 **Modern Chat Interface**: Sleek, responsive chatbot widget with real-time messaging
🏠 **Investment Guidance**: Helps users define their property search criteria
📱 **Mobile-Friendly**: Fully responsive design that works on all devices
⚡ **Real-Time**: Instant responses powered by Google's Gemini AI

## Architecture

```
Frontend (HTML/CSS/JS) ↔ Customer Agent Server (FastAPI) ↔ Customer Agent (Python)
```

- **Frontend Widget**: Modern chat interface integrated into existing design
- **Customer Agent Server**: Standalone FastAPI server (port 8001)
- **Customer Agent**: Conversational AI with structured preference collection

## Quick Start

### 1. Install Dependencies

```bash
pip install fastapi uvicorn google-generativeai pydantic
```

### 2. Set up Google Gemini API

You'll need a Google Gemini API key. Set it as an environment variable:

```bash
# Windows
set GOOGLE_API_KEY=your_api_key_here

# Linux/Mac
export GOOGLE_API_KEY=your_api_key_here
```

### 3. Start the Customer Agent Server

```bash
# Option 1: Using the convenience script
python start_chatbot_server.py

# Option 2: Direct uvicorn command
python -m uvicorn customer_agent_server:app --host 0.0.0.0 --port 8001 --reload
```

### 4. Open the Frontend

Simply open `frontend/index.html` in your browser. The chatbot widget will appear in the bottom-right corner.

## Testing

### Test the API directly:

```bash
python test_customer_agent_server.py
```

### Test through the Frontend:

1. Open `frontend/index.html` in your browser
2. Click the chat widget (🏠 icon) in the bottom-right
3. Start chatting with the assistant!

## API Endpoints

The customer agent server provides the following endpoints:

- `GET /` - Service info
- `GET /health` - Health check
- `POST /chat/start` - Start new chat session
- `POST /chat/message` - Send message to chatbot
- `GET /chat/{session_id}/status` - Get session status
- `DELETE /chat/{session_id}` - End chat session

## Conversation Flow

The chatbot guides users through these steps:

1. **Greeting** - Welcome and initial interaction
2. **Location** - Where they want to invest
3. **Property Type** - Single-family, multi-family, etc.
4. **Property Specs** - Bedrooms, bathrooms, size preferences
5. **Budget** - Investment budget range
6. **Investment Strategy** - Buy-and-hold, fix-and-flip, etc.
7. **Timeline** - When they want to purchase
8. **Summary** - Review and confirm preferences
9. **Handoff** - Transfer to deal-finding system

## Customization

### Styling
Edit `frontend/styles.css` - look for the "CHATBOT WIDGET STYLES" section

### Conversation Flow
Modify `agents/customer_agent.py` to customize the conversation steps

### API Configuration
Update `customer_agent_server.py` to change ports, CORS settings, etc.

## File Structure

```
├── customer_agent_server.py      # Standalone FastAPI server for chatbot
├── start_chatbot_server.py       # Convenience script to start server
├── test_customer_agent_server.py # API testing script
├── frontend/
│   ├── index.html                # Updated with chatbot widget HTML
│   ├── styles.css                # Updated with chatbot widget styles
│   └── script.js                 # Updated with chatbot functionality
└── agents/
    └── customer_agent.py         # Existing customer agent (unchanged)
```

## Troubleshooting

### Common Issues:

1. **Server won't start**:
   - Make sure you have the required packages installed
   - Check that port 8001 is available
   - Verify you're running from the project root directory

2. **Chat widget not appearing**:
   - Make sure JavaScript is enabled in your browser
   - Check browser console for errors
   - Verify the server is running on port 8001

3. **API connection errors**:
   - Ensure the customer agent server is running
   - Check network connectivity to localhost:8001
   - Verify CORS settings if accessing from different domain

4. **AI responses not working**:
   - Make sure you have a valid Google Gemini API key
   - Check the API key is properly set as environment variable
   - Review server logs for error messages

## Development Notes

- The chatbot widget is completely independent of the ATTOM bridge API
- Session management is handled in-memory (sessions are lost on server restart)
- The design matches the existing EquityNest theme and color scheme
- All animations and interactions follow modern web standards

## Next Steps

1. **Persistence**: Add database storage for chat sessions
2. **Authentication**: Integrate with user login system
3. **Analytics**: Track conversation completion rates and user preferences
4. **Integration**: Connect the preference handoff to actual property search
5. **Enhancements**: Add file upload, voice messages, or other advanced features