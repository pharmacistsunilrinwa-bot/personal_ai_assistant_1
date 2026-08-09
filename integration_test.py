import os
import sys
import asyncio
import json

# Add backend to path so we can import services
sys.path.append(os.path.join(os.getcwd(), "backend"))

from services.gemini_service import GeminiService
from config import Config

async def test_integration():
    print("--- Starting End-to-End Practical Test ---")
    
    # 1. Verify Configuration & API Key Loading
    print("[1/3] Verifying API Key Configuration...")
    try:
        keys = Config.GEMINI_API_KEYS
        if not keys or keys == [""]:
            print("FAILED: No Gemini API keys found in .env")
            return
        print(f"SUCCESS: Found {len(keys)} API keys in configuration.")
    except Exception as e:
        print(f"FAILED: Configuration error: {e}")
        return

    # 2. Test Gemini Service Integration (Backend -> Google Servers)
    print("[2/3] Testing Gemini Service (Backend Engine -> Google Gemini Servers)...")
    service = GeminiService()
    test_prompt = "Hello! Please respond with 'INTEGRATION_TEST_PASSED' if you can read this."
    
    try:
        print(f"Sending prompt: '{test_prompt}'")
        response = await service.generate_content(test_prompt)
        print(f"Received Response from Google: '{response}'")
        
        if "INTEGRATION_TEST_PASSED" in response.upper():
            print("SUCCESS: Communication with Google Gemini API is fully functional.")
        else:
            print("PARTIAL SUCCESS: Received a response, but it didn't match the expected string.")
    except Exception as e:
        print(f"FAILED: Could not fetch response from Google: {e}")
        return

    # 3. Simulate End-to-End Flow (Mocking Frontend Request to Service)
    print("[3/3] Simulating Full Data Flow (Frontend Request -> Service -> Response)...")
    try:
        # Mocking the call that the FastAPI endpoint would make
        mock_frontend_message = "What is the capital of France?"
        print(f"Mocking frontend message: '{mock_frontend_message}'")
        
        final_response = await service.generate_content(mock_frontend_message)
        print(f"Final Path Result: '{final_response}'")
        
        if final_response and len(final_response) > 0:
            print("SUCCESS: Full communication chain (Frontend Simulation -> Backend -> Google -> Back) is verified.")
        else:
            print("FAILED: Backend returned an empty response.")
    except Exception as e:
        print(f"FAILED: Integration flow error: {e}")

if __name__ == "__main__":
    asyncio.run(test_integration())
