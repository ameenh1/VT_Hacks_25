# PowerShell script to start the ATTOM Bridge API
Write-Host "🏠 Starting ATTOM Bridge API..." -ForegroundColor Green
Write-Host "The API will be available at: http://localhost:8000" -ForegroundColor Yellow
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the API" -ForegroundColor Red
Write-Host ""

try {
    python attom_bridge_api.py
} catch {
    Write-Host "❌ Error starting bridge API: $_" -ForegroundColor Red
    Write-Host "Make sure you have installed the requirements:" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Bridge API stopped." -ForegroundColor Yellow
Read-Host "Press Enter to exit"