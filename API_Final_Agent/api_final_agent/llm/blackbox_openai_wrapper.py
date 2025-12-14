"""
BLACKBOX AI - OpenAI Compatible Wrapper
Simple wrapper to use BLACKBOX AI with OpenAI SDK
"""

import os
from openai import OpenAI


def get_blackbox_client(api_key: str = None) -> OpenAI:
    """
    Get OpenAI client configured for BLACKBOX AI.
    
    BLACKBOX AI has an OpenAI-compatible API, so we just need to:
    1. Change the base_url to BLACKBOX
    2. Use a BLACKBOX model name
    
    Args:
        api_key: BLACKBOX API key (defaults to BLACKBOX_API_KEY env var)
        
    Returns:
        OpenAI client configured for BLACKBOX
    """
    if api_key is None:
        api_key = os.getenv("BLACKBOX_API_KEY")
        if not api_key:
            raise ValueError("BLACKBOX_API_KEY not found in environment")
    
    return OpenAI(
        api_key=api_key,
        base_url="https://api.blackbox.ai/v1"
    )


# Recommended models for different tasks
BLACKBOX_MODELS = {
    "chat": "blackboxai/blackbox-pro",  # Best for general chat
    "code": "blackboxai/deepseek/deepseek-chat",  # Best for code
    "reasoning": "blackboxai/deepseek/deepseek-r1",  # Best for reasoning
    "vision": "blackboxai/openai/gpt-4o",  # Best for image analysis
    "fast": "blackboxai/openai/gpt-4o-mini",  # Fast and cheap
    "embedding": "blackboxai/beautyyuyanli/multilingual-e5-large"  # For embeddings
}


def get_recommended_model(task: str = "chat") -> str:
    """
    Get recommended BLACKBOX model for a specific task.
    
    Args:
        task: Task type (chat, code, reasoning, vision, fast, embedding)
        
    Returns:
        Model name
    """
    return BLACKBOX_MODELS.get(task, BLACKBOX_MODELS["chat"])
