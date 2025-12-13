"""
Test Blackbox AI web API format
Based on the error message suggesting app.blackbox.ai
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("BLACKBOX_API_KEY")

print(f"✅ API Key: {api_key[:15]}...")

# Try the web API format
url = "https://www.blackbox.ai/api/chat"

# Different payload formats to try
payloads = [
    # Format 1: Simple message
    {
        "messages": [{"role": "user", "content": "Say hello"}],
        "apiKey": api_key
    },
    # Format 2: With model
    {
        "messages": [{"role": "user", "content": "Say hello"}],
        "model": "blackbox",
        "apiKey": api_key
    },
    # Format 3: Direct message
    {
        "message": "Say hello",
        "apiKey": api_key
    },
]

headers = {
    "Content-Type": "application/json",
}

print("\nTesting different payload formats...\n")

for i, payload in enumerate(payloads, 1):
    print(f"Test {i}: {list(payload.keys())}")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✅ SUCCESS!")
            result = response.text[:500]
            print(f"  Response: {result}")
            print("\n✅ Found working format!")
            print(f"Payload structure: {payload}")
            break
        else:
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:150]}")
    print()
