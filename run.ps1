# PowerShell script to run the Gemini Chatbot
Write-Host "Starting Gemini Chatbot Server..." -ForegroundColor Green
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
}

Write-Host "Installing/updating dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "Starting FastAPI server..." -ForegroundColor Green
Write-Host "Open http://localhost:8000 in your browser" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload