"""
Simple test to verify Blackbox AI API format
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("BLACKBOX_API_KEY")

if not api_key:
    print("❌ BLACKBOX_API_KEY not found in .env")
    exit(1)

print(f"✅ API Key found: {api_key[:10]}...")

# Test different API endpoints and formats
endpoints = [
    "https://api.blackbox.ai/v1/chat/completions",
    "https://api.blackbox.ai/chat/completions",
    "https://www.blackbox.ai/api/chat",
]

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Simple test payload
payload = {
    "messages": [
        {"role": "user", "content": "Say 'Hello World'"}
    ],
    "model": "blackbox"
}

print("\nTesting Blackbox AI API endpoints...\n")

for endpoint in endpoints:
    print(f"Testing: {endpoint}")
    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  ✅ SUCCESS!")
            print(f"  Response: {response.json()}")
            break
        else:
            print(f"  ❌ Error: {response.text[:200]}")
    except Exception as e:
        print(f"  ❌ Exception: {str(e)[:100]}")
    print()

print("\n" + "="*60)
print("Note: Blackbox AI might use a different API format.")
print("Check https://www.blackbox.ai/api for documentation")
print("="*60)
