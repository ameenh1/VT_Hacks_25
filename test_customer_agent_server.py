"""
Test script for Customer Agent Server
=====================================

Simple test to verify the customer agent server is working properly.
"""

import asyncio
import requests
import json
import time

async def test_customer_agent_api():
    """Test the customer agent API endpoints"""
    
    base_url = "http://localhost:8001"
    
    print("🚀 Testing Customer Agent API...")
    print("=" * 50)
    
    # Test 1: Health check
    try:
        print("1. Testing health endpoint...")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check passed: {data['status']}")
            print(f"   📊 Active sessions: {data['active_sessions']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("   ❌ Could not connect to server. Make sure it's running on port 8001")
        return
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return
    
    # Test 2: Start chat session
    print("\n2. Starting new chat session...")
    try:
        response = requests.post(f"{base_url}/chat/start", json={})
        if response.status_code == 200:
            data = response.json()
            session_id = data['session_id']
            print(f"   ✅ Session started: {session_id}")
            print(f"   💬 Initial message: {data['message'][:100]}...")
        else:
            print(f"   ❌ Failed to start session: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Start session error: {e}")
        return
    
    # Test 3: Send a test message
    print("\n3. Sending test message...")
    try:
        test_message = "Hi! I'm interested in finding investment properties in Austin, Texas."
        response = requests.post(f"{base_url}/chat/message", json={
            "session_id": session_id,
            "message": test_message
        })
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Message sent successfully")
            print(f"   🏠 Current step: {data['current_step']}")
            print(f"   💬 Response: {data['message'][:150]}...")
        else:
            print(f"   ❌ Failed to send message: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Send message error: {e}")
        return
    
    # Test 4: Check session status
    print("\n4. Checking session status...")
    try:
        response = requests.get(f"{base_url}/chat/{session_id}/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status check passed")
            print(f"   📝 Messages: {data['message_count']}")
            print(f"   🏠 Step: {data['current_step']}")
        else:
            print(f"   ❌ Failed to get status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Status check error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Customer Agent API test completed!")
    print("\n📋 Next steps:")
    print("   1. Open your browser and go to the frontend (index.html)")
    print("   2. Click the chatbot widget (bottom-right corner)")
    print("   3. Start chatting with the assistant!")
    print(f"   4. Server is running at: {base_url}")

if __name__ == "__main__":
    asyncio.run(test_customer_agent_api())