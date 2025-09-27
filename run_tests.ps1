# ATTOM Housing Data System Test Runner
# PowerShell script to run different test scenarios

Write-Host "🏠 ATTOM HOUSING DATA SYSTEM TEST RUNNER" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

# Check if bridge API is running
function Test-BridgeAPI {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 3 -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

$bridgeRunning = Test-BridgeAPI

Write-Host "System Status:" -ForegroundColor Yellow
Write-Host "  ATTOM Client: ✅ Available" -ForegroundColor Green
if ($bridgeRunning) {
    Write-Host "  Bridge API: ✅ Running on localhost:8000" -ForegroundColor Green
} else {
    Write-Host "  Bridge API: ❌ Not running" -ForegroundColor Red
}
Write-Host ""

Write-Host "Available Test Options:" -ForegroundColor Yellow
Write-Host "  1. Test ATTOM Client Only (Direct API calls)" -ForegroundColor Cyan
Write-Host "  2. Test Bridge API Only (Requires API running)" -ForegroundColor Cyan
Write-Host "  3. Test Complete System (Client + Bridge + Integration)" -ForegroundColor Cyan
Write-Host "  4. Quick Essential Tests" -ForegroundColor Cyan
Write-Host "  5. Start Bridge API" -ForegroundColor Cyan
Write-Host "  6. Exit" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "Select test option (1-6)"

switch ($choice) {
    "1" {
        Write-Host "🧪 Running ATTOM Client Tests..." -ForegroundColor Green
        python test_complete_system.py --skip-bridge --skip-integration
    }
    "2" {
        if ($bridgeRunning) {
            Write-Host "🧪 Running Bridge API Tests..." -ForegroundColor Green
            python test_complete_system.py --skip-client --skip-integration
        } else {
            Write-Host "❌ Bridge API is not running!" -ForegroundColor Red
            Write-Host "Start it first with option 5 or run: python attom_bridge_api.py" -ForegroundColor Yellow
        }
    }
    "3" {
        if ($bridgeRunning) {
            Write-Host "🧪 Running Complete System Tests..." -ForegroundColor Green
            python test_complete_system.py
        } else {
            Write-Host "❌ Bridge API is not running!" -ForegroundColor Red
            Write-Host "Complete system tests require the bridge API." -ForegroundColor Yellow
            Write-Host "Start it first with option 5 or run: python attom_bridge_api.py" -ForegroundColor Yellow
        }
    }
    "4" {
        Write-Host "🧪 Running Quick Tests..." -ForegroundColor Green
        if ($bridgeRunning) {
            python test_complete_system.py --quick
        } else {
            Write-Host "Bridge API not running - testing client only..." -ForegroundColor Yellow
            python test_complete_system.py --quick --skip-bridge --skip-integration
        }
    }
    "5" {
        Write-Host "🚀 Starting Bridge API..." -ForegroundColor Green
        Write-Host "The API will be available at: http://localhost:8000" -ForegroundColor Yellow
        Write-Host "Open another terminal to run tests while this is running." -ForegroundColor Yellow
        Write-Host ""
        python attom_bridge_api.py
    }
    "6" {
        Write-Host "👋 Goodbye!" -ForegroundColor Green
        exit
    }
    default {
        Write-Host "❌ Invalid option selected." -ForegroundColor Red
    }
}

Write-Host ""
Read-Host "Press Enter to exit"