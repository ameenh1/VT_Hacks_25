"""
Simple Bridge API Starter
========================

This script starts the bridge API with proper error handling and keeps it running.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🏠 Starting ATTOM Bridge API...")
    print("=================================")
    print("API URL: http://localhost:8000")
    print("Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("=================================")
    print("Press Ctrl+C to stop the server")
    print("")
    
    # Import and run
    import uvicorn
    from attom_bridge_api import app
    
    # Start the server
    uvicorn.run(
        app,
        host="localhost",
        port=8000,
        log_level="info",
        access_log=True
    )
    
except KeyboardInterrupt:
    print("\n🛑 Bridge API stopped by user")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you have installed the requirements:")
    print("  pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Error starting bridge API: {e}")
    print("Check the error details above.")
finally:
    print("\n👋 Bridge API session ended")
    input("Press Enter to exit...")