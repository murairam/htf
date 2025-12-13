"""
Test Blackbox AI Chat Completion API with correct format
Based on official documentation: https://docs.blackbox.ai/api-reference/chat
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("BLACKBOX_API_KEY")

print(f"✅ API Key: {api_key[:15]}...")

# Correct endpoint from documentation
url = "https://api.blackbox.ai/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Test with different models from the documentation
test_cases = [
    {
        "name": "Test 1: GPT-4 via Blackbox",
        "payload": {
            "model": "blackboxai/openai/gpt-4",
            "messages": [
                {
                    "role": "user",
                    "content": "Say 'Hello from Blackbox AI!'"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 50,
            "stream": False
        }
    },
    {
        "name": "Test 2: Blackbox Model",
        "payload": {
            "model": "blackbox",
            "messages": [
                {
                    "role": "user",
                    "content": "Write a Python function to add two numbers"
                }
            ],
            "temperature": 0.1,
            "max_tokens": 200,
            "stream": False
        }
    },
    {
        "name": "Test 3: Claude via Blackbox",
        "payload": {
            "model": "blackboxai/anthropic/claude-3-5-sonnet-20241022",
            "messages": [
                {
                    "role": "user",
                    "content": "Explain what 2+2 equals"
                }
            ],
            "temperature": 0.5,
            "max_tokens": 100,
            "stream": False
        }
    }
]

print("\nTesting Blackbox AI Chat Completion API...\n")
print("="*60)

for test in test_cases:
    print(f"\n{test['name']}")
    print("-"*60)
    print(f"Model: {test['payload']['model']}")

    try:
        response = requests.post(url, headers=headers, json=test['payload'], timeout=30)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS!")
            print(f"\nResponse:")
            print(f"  ID: {result.get('id', 'N/A')}")
            print(f"  Model: {result.get('model', 'N/A')}")
            print(f"  Provider: {result.get('provider', 'N/A')}")

            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"  Content: {content[:150]}...")

            if 'usage' in result:
                usage = result['usage']
                print(f"\nToken Usage:")
                print(f"  Prompt: {usage.get('prompt_tokens', 0)}")
                print(f"  Completion: {usage.get('completion_tokens', 0)}")
                print(f"  Total: {usage.get('total_tokens', 0)}")

            print("\n✅ API IS WORKING!")
            break  # Stop after first success
        else:
            print(f"❌ Error {response.status_code}")
            print(f"Response: {response.text[:300]}")

    except Exception as e:
        print(f"❌ Exception: {str(e)}")

print("\n" + "="*60)
