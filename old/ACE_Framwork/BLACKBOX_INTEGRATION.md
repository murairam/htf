# Blackbox AI Integration Guide

This document describes the integration of Blackbox AI as an LLM provider in the ACE Framework.

## Overview

Blackbox AI has been successfully integrated as a new LLM provider option alongside OpenAI, Google Gemini, and Anthropic Claude. The integration uses the OpenAI-compatible API format, making it seamless to switch between providers.

## Changes Made

### 1. Configuration (`config.py`)

Added support for Blackbox API key and provider configuration:

```python
# New environment variable
BLACKBOX_API_KEY = os.getenv("BLACKBOX_API_KEY", "")

# Updated LLMConfig.__post_init__()
def __post_init__(self):
    if self.api_key is None:
        # ... existing providers ...
        elif self.provider == "blackbox":
            self.api_key = BLACKBOX_API_KEY
```

### 2. LLM Client (`llm_client.py`)

Added `BlackboxClient` class that extends `LLMClient`:

```python
class BlackboxClient(LLMClient):
    """Blackbox AI API client (OpenAI-compatible)."""
    
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        import openai
        self.client = openai.OpenAI(
            api_key=config.api_key,
            base_url="https://api.blackbox.ai/v1"
        )
    
    def complete(self, messages: List[Message]) -> LLMResponse:
        # Standard OpenAI-compatible completion
        ...
    
    def stream(self, messages: List[Message]) -> Generator[str, None, None]:
        # Standard OpenAI-compatible streaming
        ...
```

Updated factory function:

```python
def create_client(config: LLMConfig) -> LLMClient:
    provider = config.provider.lower()
    # ... existing providers ...
    elif provider == "blackbox":
        return BlackboxClient(config)
```

### 3. Documentation (`README.md`)

Added Blackbox to the supported providers table and usage examples.

### 4. Test Script (`test_blackbox.py`)

Created a comprehensive test script to verify the integration.

## Usage

### Basic Setup

1. **Set your API key:**

```bash
export BLACKBOX_API_KEY="your-api-key-here"
```

Get your API key from: https://www.blackbox.ai/

2. **Use in your code:**

```python
from config import LLMConfig, ACEConfig
from llm_client import create_client

# Option 1: Using environment variable
config = LLMConfig(provider="blackbox", model="blackboxai")
client = create_client(config)

# Option 2: Explicit API key
config = LLMConfig(
    provider="blackbox",
    model="blackboxai",
    api_key="your-api-key-here"
)
client = create_client(config)
```

### Available Models

| Model | Description | Use Case |
|-------|-------------|----------|
| `blackboxai` | Standard model | General purpose, cost-effective |
| `blackboxai-pro` | Pro model | Advanced reasoning, better quality |
| `gpt-4o` | Vision model | Image analysis (if supported) |

### Integration with ACE Framework

```python
from config import ACEConfig, LLMConfig

# Configure ACE to use Blackbox
ace_config = ACEConfig(
    llm=LLMConfig(
        provider="blackbox",
        model="blackboxai",
        temperature=0.0,
        max_tokens=4096
    )
)

# Use with agents
from agents import ACESystem
ace = ACESystem(ace_config)
result = ace.analyze(product_data, image_analysis, objective)
```

### Testing the Integration

Run the test script to verify everything works:

```bash
cd ACE_Framwork
export BLACKBOX_API_KEY="your-api-key-here"
python test_blackbox.py
```

Expected output:
```
🚀 Blackbox AI Integration Test Suite

============================================================
Testing Blackbox AI Integration
============================================================

✓ API Key found: sk-xxxxxx...

1. Creating Blackbox client configuration...
   Provider: blackbox
   Model: blackboxai
   Temperature: 0.7

2. Initializing Blackbox client...
   ✓ Client created successfully

3. Testing basic completion...
   ✓ Completion successful
   ...

4. Testing streaming completion...
   ✓ Streaming successful

============================================================
✓ All tests passed successfully!
============================================================
```

## API Compatibility

Blackbox AI uses an OpenAI-compatible API, which means:

- ✅ Same message format (role, content)
- ✅ Same response structure
- ✅ Streaming support
- ✅ Usage statistics (tokens)
- ✅ Error handling

## Benefits of Using Blackbox AI

1. **Cost-Effective**: Generally more affordable than OpenAI
2. **OpenAI-Compatible**: Easy migration, no code changes needed
3. **Good Performance**: Competitive quality for most tasks
4. **Simple Integration**: Uses existing OpenAI SDK

## Troubleshooting

### Error: "Blackbox API key is required"

**Solution:** Set the `BLACKBOX_API_KEY` environment variable:
```bash
export BLACKBOX_API_KEY="your-key"
```

### Error: "openai package not installed"

**Solution:** Install the OpenAI package:
```bash
pip install openai>=1.0.0
```

### Error: API connection issues

**Solution:** Check:
1. API key is valid
2. Internet connection is working
3. Blackbox API service is operational

## Comparison with Other Providers

| Feature | OpenAI | Blackbox | Google | Anthropic |
|---------|--------|----------|--------|-----------|
| API Format | Native | OpenAI-compatible | Custom | Custom |
| Streaming | ✅ | ✅ | ✅ | ✅ |
| Vision | ✅ | ✅* | ✅ | ✅ |
| Cost | $$$ | $$ | $$ | $$$ |
| Setup | Easy | Easy | Easy | Easy |

*Vision support depends on model availability

## Future Enhancements

Potential improvements for the Blackbox integration:

- [ ] Add support for additional Blackbox-specific models
- [ ] Implement custom parameters if Blackbox offers unique features
- [ ] Add performance benchmarking
- [ ] Create migration guide from OpenAI to Blackbox

## Support

For issues related to:
- **ACE Framework integration**: Check this documentation
- **Blackbox API**: Visit https://docs.blackbox.ai/
- **OpenAI SDK**: Visit https://github.com/openai/openai-python

## Version History

- **v1.0.0** (2024-01-XX): Initial Blackbox AI integration
  - Added BlackboxClient class
  - Updated configuration system
  - Created test suite
  - Updated documentation
