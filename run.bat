@echo off
echo Starting Gemini Chatbot Server...
echo.

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
)

echo Installing/updating dependencies...
pip install -r requirements.txt

echo.
echo Starting FastAPI server...
echo Open http://localhost:8000 in your browser
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload