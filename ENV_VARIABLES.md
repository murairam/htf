# Environment Variables Configuration

## Required Variables

### API Keys

**OPENAI_API_KEY** (Required)
- Used by: API_Final_Agent (ACE pipeline for LLM analysis)
- Format: `sk-...`
- Example: `OPENAI_API_KEY=sk-proj-...`

**BLACKBOX_API_KEY** (Optional, for Blackbox AI provider)
- Used by: API_Final_Agent (ACE pipeline, if using Blackbox as LLM provider)
- Format: `sk-...` or `bb-...`
- Example: `BLACKBOX_API_KEY=sk-zJValC5qOR6n62aSOmoxNw`

### Service URLs

**FINAL_AGENT_BASE_URL** (Optional)
- Default: `http://localhost:8001`
- Used by: Django to connect to API_Final_Agent
- Example: `FINAL_AGENT_BASE_URL=http://localhost:8001`

**FINAL_AGENT_TIMEOUT** (Optional)
- Default: `180` (seconds)
- Used by: Django client for API_Final_Agent requests
- Example: `FINAL_AGENT_TIMEOUT=180`

**API_FINAL_AGENT_PORT** (Optional)
- Default: `8001`
- Used by: API_Final_Agent service port
- Example: `API_FINAL_AGENT_PORT=8001`

## How Variables Are Loaded

### For API_Final_Agent

The service reads environment variables directly from the system environment:

```python
# In api_final_agent/ace/config.py
BLACKBOX_API_KEY = os.getenv("BLACKBOX_API_KEY", "")
```

When you run `make all-services` or `./run_all_services.sh`:
1. The script loads `.env` file: `export $(grep -v '^#' .env | xargs)`
2. This exports all variables to the shell environment
3. When API_Final_Agent starts, it reads from `os.getenv()`

### For Django

Django reads from `config/settings.py`:

```python
# In config/settings.py
FINAL_AGENT_BASE_URL = os.environ.get('FINAL_AGENT_BASE_URL', 'http://localhost:8001')
FINAL_AGENT_TIMEOUT = int(os.environ.get('FINAL_AGENT_TIMEOUT', '180'))
```

## Current .env File

Your `.env` file should contain:

```env
# Required
OPENAI_API_KEY=sk-proj-...

# Optional (for Blackbox AI provider)
BLACKBOX_API_KEY=sk-zJValC5qOR6n62aSOmoxNw

# Service Configuration
FINAL_AGENT_BASE_URL=http://localhost:8001
FINAL_AGENT_TIMEOUT=180
API_FINAL_AGENT_PORT=8001
```

## Verification

To verify that variables are loaded correctly:

```bash
# Load .env manually
source <(grep -v '^#' .env | sed 's/^/export /')

# Check if BLACKBOX_API_KEY is set
echo $BLACKBOX_API_KEY

# Or test in Python
python3 -c "import os; print('BLACKBOX_API_KEY:', os.getenv('BLACKBOX_API_KEY', 'NOT SET'))"
```

## Important Notes

1. **Never commit `.env` to git** - It contains sensitive API keys
2. **Restart services** after changing `.env`:
   ```bash
   make stop-services
   make all-services
   ```
3. **Variables are loaded at startup** - Changes require service restart
4. **API_Final_Agent reads directly from environment** - No Django settings needed for API keys

