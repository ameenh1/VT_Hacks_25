#!/usr/bin/env python3
"""
Simple test script to verify Gemini API setup
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

def test_gemini_connection():
    """Test the Gemini API connection"""
    print("🔍 Testing Gemini AI API Connection...")
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key exists
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        print("Please add your API key to the .env file")
        return False
    
    if api_key == "your_actual_gemini_api_key_here":
        print("❌ Please replace 'your_actual_gemini_api_key_here' with your real API key")
        return False
    
    print(f"✅ API Key found (ends with: ...{api_key[-6:]})")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Initialize model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Test with a simple prompt
        print("📨 Sending test message to Gemini...")
        response = model.generate_content("Hello! Can you respond with 'Gemini API is working correctly!'?")
        
        if response.text:
            print(f"✅ Success! Gemini responded: {response.text}")
            return True
        else:
            print("❌ No response received from Gemini")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to Gemini API: {e}")
        return False

if __name__ == "__main__":
    print("🤖 Gemini API Connection Test")
    print("=" * 40)
    
    if test_gemini_connection():
        print("\n🎉 All tests passed! Your Gemini API setup is working correctly.")
        print("You can now start the chatbot server with: python main.py")
    else:
        print("\n❌ Setup incomplete. Please check your .env file and API key.")
        print("\nTo get your API key:")
        print("1. Go to https://makersuite.google.com/app/apikey")
        print("2. Create a new API key")
        print("3. Add it to your .env file as GEMINI_API_KEY=your_key_here")