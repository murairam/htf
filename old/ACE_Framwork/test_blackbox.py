"""
Test script for Blackbox AI integration in ACE Framework.

This script demonstrates how to use the Blackbox API provider.
"""
import os
import sys
from config import LLMConfig
from llm_client import create_client, Message

def test_blackbox_basic():
    """Test basic completion with Blackbox API."""
    print("=" * 60)
    print("Testing Blackbox AI Integration")
    print("=" * 60)
    
    # Check if API key is set
    api_key = os.getenv("BLACKBOX_API_KEY")
    if not api_key:
        print("\n❌ ERROR: BLACKBOX_API_KEY environment variable not set")
        print("\nPlease set your Blackbox API key:")
        print("  export BLACKBOX_API_KEY='your-api-key-here'")
        print("\nGet your API key from: https://www.blackbox.ai/")
        return False
    
    print(f"\n✓ API Key found: {api_key[:10]}...")
    
    # Configure Blackbox provider
    print("\n1. Creating Blackbox client configuration...")
    config = LLMConfig(
        provider="blackbox",
        model="blackboxai",
        temperature=0.7,
        max_tokens=500
    )
    print(f"   Provider: {config.provider}")
    print(f"   Model: {config.model}")
    print(f"   Temperature: {config.temperature}")
    
    # Create client
    print("\n2. Initializing Blackbox client...")
    try:
        client = create_client(config)
        print("   ✓ Client created successfully")
    except Exception as e:
        print(f"   ❌ Failed to create client: {e}")
        return False
    
    # Test basic completion
    print("\n3. Testing basic completion...")
    try:
        response = client.chat(
            system_prompt="You are a helpful assistant specialized in plant-based food analysis.",
            user_message="What are the key factors to consider when analyzing plant-based meat alternatives?"
        )
        print("   ✓ Completion successful")
        print(f"\n   Response:\n   {'-' * 56}")
        print(f"   {response.content[:300]}...")
        if response.usage:
            print(f"\n   Usage Statistics:")
            print(f"   - Prompt tokens: {response.usage.get('prompt_tokens', 'N/A')}")
            print(f"   - Completion tokens: {response.usage.get('completion_tokens', 'N/A')}")
            print(f"   - Total tokens: {response.usage.get('total_tokens', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Completion failed: {e}")
        return False
    
    # Test streaming
    print("\n4. Testing streaming completion...")
    try:
        print("   Streaming response: ", end="", flush=True)
        chunk_count = 0
        for chunk in client.stream_chat(
            system_prompt="You are a helpful assistant.",
            user_message="List 3 benefits of plant-based proteins in one sentence."
        ):
            print(chunk, end="", flush=True)
            chunk_count += 1
        print(f"\n   ✓ Streaming successful ({chunk_count} chunks)")
    except Exception as e:
        print(f"\n   ❌ Streaming failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All tests passed successfully!")
    print("=" * 60)
    return True


def test_blackbox_with_messages():
    """Test Blackbox with custom message format."""
    print("\n\n5. Testing with custom message format...")
    
    config = LLMConfig(provider="blackbox", model="blackboxai")
    client = create_client(config)
    
    messages = [
        Message(role="system", content="You are a food science expert."),
        Message(role="user", content="What is NOVA classification?"),
    ]
    
    try:
        response = client.complete(messages)
        print("   ✓ Custom message format successful")
        print(f"   Response preview: {response.content[:150]}...")
        return True
    except Exception as e:
        print(f"   ❌ Custom message format failed: {e}")
        return False


if __name__ == "__main__":
    print("\n🚀 Blackbox AI Integration Test Suite\n")
    
    success = test_blackbox_basic()
    
    if success:
        test_blackbox_with_messages()
        print("\n✅ Blackbox AI is ready to use in ACE Framework!")
        print("\nYou can now use Blackbox in your ACE configuration:")
        print("  config = ACEConfig(llm=LLMConfig(provider='blackbox'))")
    else:
        print("\n❌ Tests failed. Please check your configuration.")
        sys.exit(1)
