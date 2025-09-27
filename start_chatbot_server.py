"""
EquityNest Development Server Launcher
======================================

Convenient script to start the customer agent server for frontend integration.
"""

import subprocess
import sys
import time
import os

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'fastapi',
        'uvicorn', 
        'google-generativeai',
        'pydantic'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print(f"\n💡 Install them with: pip install {' '.join(missing_packages)}")
        return False
    
    return True

def start_customer_agent_server():
    """Start the customer agent server"""
    print("🚀 Starting EquityNest Customer Agent Server...")
    print("=" * 60)
    print("🌟 Customer Agent API will be available at: http://localhost:8001")
    print("📚 API Documentation: http://localhost:8001/docs")
    print("🔧 To stop the server, press Ctrl+C")
    print("=" * 60)
    
    try:
        # Start the customer agent server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "customer_agent_server:app",
            "--host", "0.0.0.0",
            "--port", "8001", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped gracefully")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def main():
    print("🏠 EquityNest - Customer Agent Server")
    print("====================================\n")
    
    # Check dependencies
    if not check_dependencies():
        return
    
    print("✅ All dependencies are installed!\n")
    
    # Check if we're in the right directory
    if not os.path.exists("agents/customer_agent.py"):
        print("❌ Please run this script from the project root directory")
        print("💡 Make sure you can see the 'agents' folder in the current directory")
        return
    
    print("📁 Project structure looks good!\n")
    
    # Start the server
    start_customer_agent_server()

if __name__ == "__main__":
    main()