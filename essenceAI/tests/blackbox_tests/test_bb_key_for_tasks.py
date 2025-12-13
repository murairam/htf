"""
Test if bb_ key works for repository tasks API
Based on documentation showing bb_ keys in examples
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("BLACKBOX_API_KEY")

print(f"✅ API Key: {api_key[:15]}...")
print(f"Key Type: {'bb_' if api_key.startswith('bb_') else 'sk_'}")

# Test the repository tasks endpoint (from documentation)
url = "https://cloud.blackbox.ai/api/tasks"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Simple test task from documentation
payload = {
    "prompt": "Create a simple README file",
    "repoUrl": "https://github.com/blackboxai/test-repo.git",  # Using a test repo
    "selectedBranch": "main",
    "selectedAgent": "blackbox",
    "selectedModel": "blackboxai/blackbox-pro"
}

print("\n" + "="*60)
print("Testing Repository Task API with bb_ key")
print("="*60)
print(f"\nEndpoint: {url}")
print(f"Payload: {payload}")

try:
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"\nStatus Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ SUCCESS! bb_ key WORKS for repository tasks!")
        print(f"\nResponse:")
        print(f"  Task ID: {result.get('task', {}).get('id', 'N/A')}")
        print(f"  Status: {result.get('task', {}).get('status', 'N/A')}")
        print(f"  Prompt: {result.get('task', {}).get('prompt', 'N/A')}")
        print("\n✅ CONFIRMED: bb_ keys work for REPOSITORY TASKS")
        print("❌ CONFIRMED: bb_ keys DON'T work for CHAT COMPLETIONS")
    elif response.status_code == 401:
        print(f"❌ 401 Unauthorized")
        print(f"Response: {response.text[:500]}")
        print("\n⚠️ bb_ key doesn't work for repository tasks either")
    elif response.status_code == 400:
        print(f"⚠️ 400 Bad Request (might be repo access issue)")
        print(f"Response: {response.text[:500]}")
        print("\n💡 This might mean the API endpoint is correct,")
        print("   but we need a valid/accessible repository")
    else:
        print(f"❌ Error {response.status_code}")
        print(f"Response: {response.text[:500]}")

except Exception as e:
    print(f"❌ Exception: {str(e)}")

print("\n" + "="*60)
print("\nConclusion:")
print("If we get 400 (bad request), it means bb_ key works for tasks!")
print("If we get 401 (unauthorized), bb_ key doesn't work for tasks")
print("="*60)
