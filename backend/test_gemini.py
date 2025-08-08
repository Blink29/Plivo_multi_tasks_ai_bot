#!/usr/bin/env python3
"""
Test script for Gemini API setup
Run this to verify your API key and connection
"""

import os
from dotenv import load_dotenv
from google import genai

def test_gemini_setup():
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("💡 Please add your API key to the .env file:")
        print("   GEMINI_API_KEY=your_actual_api_key_here")
        return False
    
    if api_key == "your_actual_api_key_here":
        print("❌ Please replace the placeholder API key with your actual Gemini API key")
        print("🔗 Get your API key from: https://aistudio.google.com/app/apikey")
        return False
    
    try:
        # Set API key for client
        os.environ["GEMINI_API_KEY"] = api_key
        
        # Initialize client
        client = genai.Client()
        
        # Test API call
        print("🔄 Testing Gemini API connection...")
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents="Say hello and confirm the API is working!"
        )
        
        print("✅ Gemini API connection successful!")
        print(f"🤖 Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to Gemini API: {str(e)}")
        print("🔍 Please check:")
        print("   1. Your API key is correct")
        print("   2. You have internet connection")
        print("   3. The google-genai package is installed")
        return False

if __name__ == "__main__":
    print("🧪 Testing Gemini API Setup")
    print("=" * 30)
    test_gemini_setup()
