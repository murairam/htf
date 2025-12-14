# Quick Start Guide

## Architecture

- **Django + React**: Main website on port 8000
- **API_Final_Agent**: Unified LLM service on port 8001

## Setup

### 1. Install Dependencies

```bash
# API_Final_Agent
cd API_Final_Agent
pip install -r requirements.txt

# Django (if not already installed)
cd ..
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file in project root:

```env
# API_Final_Agent
OPENAI_API_KEY=sk-your-key-here
API_FINAL_AGENT_PORT=8001

# Django
FINAL_AGENT_BASE_URL=http://localhost:8001
FINAL_AGENT_TIMEOUT=60
```

### 3. Start Services

**Terminal 1 - API_Final_Agent:**
```bash
cd API_Final_Agent
python main.py
```

Service runs on `http://localhost:8001`

**Terminal 2 - Django:**
```bash
# From project root
python manage.py runserver
# or for production with WebSockets:
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

Django runs on `http://localhost:8000`

### 4. Open Website

```
http://localhost:8000
```

## Testing

1. **Enter Business Objective** (required)
2. **Choose Input Method:**
   - Barcode (scan or manual)
   - Product Link
   - Product Description
3. **Submit** - Analysis runs via WebSocket
4. **View Results** - Data-driven rendering of unified JSON

## Key Files

- `config/settings.py` - Django settings with `FINAL_AGENT_BASE_URL`
- `marketing_analyzer/views.py` - POST /submit/ endpoint
- `marketing_analyzer/consumers.py` - WebSocket consumer
- `marketing_analyzer/fastapi_final_client.py` - API client
- `frontend/src/pages/HomePage.jsx` - Home form
- `frontend/src/pages/ResultsPage.jsx` - Results page (data-driven)

## Troubleshooting

### API_Final_Agent not responding

Check:
- Service is running on port 8001
- `FINAL_AGENT_BASE_URL` in Django settings matches
- Check logs: `API_Final_Agent/main.py` output

### WebSocket connection fails

Check:
- Django is running with `daphne` (not `runserver` for production)
- Redis is running (for Channels in production)
- Check browser console for WebSocket errors

### Analysis timeout

- Default timeout is 60 seconds
- Increase `FINAL_AGENT_TIMEOUT` if needed
- Check API_Final_Agent logs for slow operations

