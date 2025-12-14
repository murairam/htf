# Django Integration with API_Final_Agent

## Architecture Overview

```
┌─────────────────┐
│  Django + React │  Port 8000
│  (Main Website) │
└────────┬────────┘
         │ HTTP POST /run-analysis
         │ WebSocket (status updates)
         ▼
┌─────────────────┐
│ API_Final_Agent │  Port 8001
│  (Unified LLM)  │
└─────────────────┘
```

## Configuration

### Django Settings

Add to `config/settings.py`:

```python
# API_Final_Agent Unified Service Configuration
FINAL_AGENT_BASE_URL = os.environ.get('FINAL_AGENT_BASE_URL', 'http://localhost:8001')
FINAL_AGENT_TIMEOUT = int(os.environ.get('FINAL_AGENT_TIMEOUT', '60'))
```

### Environment Variables

Create `.env` file or set:

```bash
export FINAL_AGENT_BASE_URL=http://localhost:8001
export FINAL_AGENT_TIMEOUT=60
```

## Django Backend Changes

### 1. POST /submit/ Endpoint (`marketing_analyzer/views.py`)

- Creates `analysis_id` (UUID)
- Validates inputs:
  - `business_objective` required
  - At least one of: `barcode`, `product_link`, `product_description`
- Returns `analysis_id` and redirect URL
- No image upload handling (removed)

### 2. WebSocket Consumer (`marketing_analyzer/consumers.py`)

**Flow:**
1. Client connects to `ws/analysis/<analysis_id>/`
2. Consumer immediately sends: `{"type":"status","status":"started","progress":0}`
3. Consumer sends: `{"type":"status","status":"processing","progress":30}`
4. Consumer calls `APIFinalAgentClient.run_analysis()` synchronously (timeout 60s)
5. On success: sends `{"type":"final_result","payload":<unified_json>}`
6. On error: sends `{"type":"status","status":"error","message":"Analysis failed. Please try again."}`

**No background tasks, no retries, no caching.**

### 3. API Client (`marketing_analyzer/fastapi_final_client.py`)

- Uses `FINAL_AGENT_BASE_URL` from Django settings
- Calls `POST /run-analysis` with unified request
- Returns `(success: bool, result: dict)`

## React Frontend Changes

### 1. HomePage (`frontend/src/pages/HomePage.jsx`)

**Form Fields:**
- `business_objective` (required textarea)
- `barcode` (optional, with QuaggaJS scanner + manual input)
- `product_link` (optional)
- `product_description` (optional)

**Validation:**
- Frontend blocks submit if `business_objective` empty
- Frontend blocks submit if none of `{barcode, product_link, product_description}` provided
- No image upload (removed)

**Submission:**
- POST to `/submit/` with JSON payload
- Redirects to `/results/<analysis_id>/` on success

### 2. ResultsPage (`frontend/src/pages/ResultsPage.jsx`)

**Data-Driven Rendering:**
- Displays `payload.merged` by default (main content)
- Optional collapsible "Debug" section for `payload.raw_sources`
- No hardcoded keys like "Product Details" or "Performance Scores"
- Renders sections conditionally based on what exists in the JSON

**Image Display:**
- Only shows if `image_front_url` exists in unified JSON
- Checks: `results.image_front_url` or `merged.product_information.image_front_url`
- Hides image section if URL not found

**WebSocket Handling:**
- Connects to `ws/analysis/<analysis_id>/`
- Handles `status` messages (started, processing, error)
- Handles `final_result` message with unified JSON payload

## API Contract

### Request (Django → API_Final_Agent)

```json
POST /run-analysis
{
  "analysis_id": "uuid-from-django",
  "business_objective": "Increase flexitarian appeal",
  "barcode": "3017620422003",
  "product_link": "https://...",
  "product_description": "Plant-based product..."
}
```

### Response (API_Final_Agent → Django)

```json
{
  "analysis_id": "uuid",
  "input": {...},
  "status": "ok|partial|error",
  "merged": {
    "product_information": {...},
    "scoring_results": {...},
    "swot_analysis": [...],
    "image_analysis": {...},
    "packaging_improvements": [...],
    "go_to_market_strategies": [...],
    "competitor_analysis": {...},
    "research_insights": {...},
    "marketing_strategy": {...},
    "quality_insights": {...}
  },
  "raw_sources": {
    "ace": {...},
    "essence": {...}
  },
  "errors": [],
  "timestamp": "2025-01-13T..."
}
```

## Running the Services

### 1. Start API_Final_Agent

```bash
cd API_Final_Agent
pip install -r requirements.txt
python main.py
```

Service runs on `http://localhost:8001` (or `API_FINAL_AGENT_PORT` env var).

### 2. Start Django

```bash
# Set environment variable
export FINAL_AGENT_BASE_URL=http://localhost:8001

# Run Django
python manage.py runserver
# or
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

Django runs on `http://localhost:8000`.

### 3. Open Website

```
http://localhost:8000
```

## Testing

### Test with Barcode

1. Go to homepage
2. Enter business objective
3. Scan or enter barcode
4. Submit
5. Wait for WebSocket updates
6. View results page with unified JSON

### Test with Product Description

1. Go to homepage
2. Enter business objective
3. Enter product description
4. Submit
5. Wait for WebSocket updates
6. View results page with unified JSON

### Test with Product Link

1. Go to homepage
2. Enter business objective
3. Enter product link
4. Submit
5. Wait for WebSocket updates
6. View results page with unified JSON

## Error Handling

- **API_Final_Agent unavailable**: WebSocket sends error status
- **Timeout (60s)**: WebSocket sends error status
- **Invalid input**: Django returns 400 before creating analysis
- **Analysis fails**: WebSocket sends error status with user-friendly message

## Key Points

✅ **Single service**: Only API_Final_Agent needed (no separate ACE/Essence)
✅ **Synchronous calls**: No Celery, no background tasks
✅ **No caching**: Fresh analysis every time
✅ **Data-driven UI**: React renders based on JSON structure
✅ **Clean error handling**: User-friendly messages, no stack traces
✅ **WebSocket updates**: Real-time status during analysis

