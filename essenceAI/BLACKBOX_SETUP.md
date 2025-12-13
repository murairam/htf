# Blackbox AI Dual-Key Setup Guide

## 🔑 Understanding Blackbox AI Key Types

Blackbox AI uses **TWO different API key types** for different services:

### 1. `bb_` Keys - Repository & GitHub Tasks
**Format:** `bb_89eba5664e1b...`

**What it does:**
- ✅ Create tasks on GitHub repositories
- ✅ Multi-agent execution on codebases
- ✅ GitHub API access (orgs, repos, branches, issues)
- ✅ Automated PR creation

**Where to get:**
- https://app.blackbox.ai/dashboard
- Available on free and paid tiers

### 2. `sk-` Keys - Chat Completions & AI Models
**Format:** `sk-...`

**What it does:**
- ✅ Chat completions
- ✅ Code generation (standalone)
- ✅ Image generation
- ✅ Video generation
- ✅ Access to multiple AI models (GPT-4, Claude, Gemini)

**Where to get:**
- https://app.blackbox.ai/dashboard
- **Requires paid subscription** (Pro Plus or higher)
- Check pricing: https://www.blackbox.ai/pricing

## 📝 Environment Variable Setup

### Option 1: Use Both Keys (Recommended)

Add to your `.env` file:

```bash
# For chat completions (requires sk- key)
BLACKBOX_CHAT_API_KEY=sk_your_chat_api_key_here

# For repository tasks (works with bb_ key)
BLACKBOX_TASK_API_KEY=bb_your_task_api_key_here

# Other APIs
OPENAI_API_KEY=your_openai_key_here
TAVILY_API_KEY=your_tavily_key_here
```

### Option 2: Use Single Key

If you only have one key type:

```bash
# This will be used for both (but only works for compatible APIs)
BLACKBOX_API_KEY=your_key_here
```

## 🚀 Usage Examples

### Using Chat Completion (Requires `sk-` key)

```python
from src.blackbox_client import BlackboxAIClient

# Initialize with sk- key
client = BlackboxAIClient(
    chat_api_key="sk_your_key_here"  # or set BLACKBOX_CHAT_API_KEY env var
)

# Generate code
code = client.generate_code(
    prompt="Create a Python function to calculate fibonacci",
    language="python"
)

print(code)
```

### Using Repository Tasks (Works with `bb_` key)

```python
from src.blackbox_client import BlackboxAIClient

# Initialize with bb_ key
client = BlackboxAIClient(
    task_api_key="bb_your_key_here"  # or set BLACKBOX_TASK_API_KEY env var
)

# Create a task on a repository
task = client.create_repository_task(
    prompt="Add error handling to the API endpoints",
    repo_url="https://github.com/your-org/your-repo.git",
    branch="main",
    agent="blackbox",
    model="blackboxai/blackbox-pro"
)

print(f"Task ID: {task['task']['id']}")
print(f"Status: {task['task']['status']}")

# Check task status
status = client.get_task_status(task['task']['id'])
print(f"Progress: {status['task']['progress']}%")
```

### Using Both Keys Together

```python
from src.blackbox_client import BlackboxAIClient

# Initialize with both keys
client = BlackboxAIClient(
    chat_api_key="sk_your_chat_key_here",
    task_api_key="bb_your_task_key_here"
)

# Use chat completion
code = client.generate_code("Create a REST API")

# Use repository task
task = client.create_repository_task(
    prompt="Implement the REST API",
    repo_url="https://github.com/your-org/your-repo.git"
)
```

## 🎯 Current System Configuration

### With Your Current `bb_` Key:

```python
# This WILL work
client = BlackboxAIClient(task_api_key="bb_your_key")
task = client.create_repository_task(...)  # ✅ Works

# This WON'T work
client = BlackboxAIClient(chat_api_key="bb_your_key")
code = client.generate_code(...)  # ❌ Requires sk- key
```

### When You Get `sk-` Key:

```python
# Everything works!
client = BlackboxAIClient(
    chat_api_key="sk_your_key",
    task_api_key="bb_your_key"  # or use sk- for both
)

code = client.generate_code(...)  # ✅ Works
task = client.create_repository_task(...)  # ✅ Works
```

## 💡 Recommended Setup

### Immediate (With Current `bb_` Key):

1. **Use OpenAI for code generation** (you already have the key)
2. **Keep `bb_` key for future repository tasks**
3. **All agents working immediately**

```bash
# .env file
OPENAI_API_KEY=your_openai_key_here
BLACKBOX_TASK_API_KEY=bb_your_key_here  # For future use
```

### Future (When You Upgrade):

1. **Get `sk-` key** from Blackbox AI
2. **Add to environment variables**
3. **Use both keys for full functionality**

```bash
# .env file
OPENAI_API_KEY=your_openai_key_here
BLACKBOX_CHAT_API_KEY=sk_your_new_key_here
BLACKBOX_TASK_API_KEY=bb_your_key_here
```

## 📊 Feature Matrix

| Feature | `bb_` Key | `sk-` Key |
|---------|-----------|-----------|
| Chat Completions | ❌ | ✅ |
| Code Generation (standalone) | ❌ | ✅ |
| Repository Tasks | ✅ | ✅ |
| GitHub APIs | ✅ | ✅ |
| Image Generation | ❌ | ✅ |
| Video Generation | ❌ | ✅ |
| Multi-Model Access | ❌ | ✅ |

## 🔧 Troubleshooting

### Error: "Authentication Error, LiteLLM Virtual Key expected"

**Cause:** Using `bb_` key for chat completions

**Solution:**
- Get `sk-` key (paid subscription)
- OR use OpenAI for code generation instead

### Error: "Task API key not configured"

**Cause:** No task key set

**Solution:**
```bash
# Add to .env
BLACKBOX_TASK_API_KEY=bb_your_key_here
```

### Error: "Chat API key not configured"

**Cause:** No chat key set

**Solution:**
```bash
# Add to .env
BLACKBOX_CHAT_API_KEY=sk_your_key_here
```

## 📚 More Information

- **Documentation:** See `docs/` folder for detailed guides
- **API Reference:** https://docs.blackbox.ai
- **Get API Keys:** https://app.blackbox.ai/dashboard
- **Pricing:** https://www.blackbox.ai/pricing
