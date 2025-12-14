# Website Integration - Complete Guide

This document describes the complete integration of the unified `API_Final_Agent` with the Django + React website.

## Architecture Overview

```
React UI (served by Django)
  |
  | REST + WebSocket
  v
Django (orchestrator + Channels WebSocket)
  |
  | HTTP REST
  v
API_Final_Agent (unified FastAPI service)
  |
  | Internal pipelines
  v
ACE + Essence (fused internally)
```

## Ports

- **Django**: `http://localhost:8000`
- **API_Final_Agent**: `http://localhost:8001`

## JSON Contract

See `docs/final_json_contract.md` for the complete JSON structure.

### Key Points:

- **Main Display Content**: `merged` (top-level key)
- **Raw Sources**: `raw_sources.ace` and `raw_sources.essence`
- **Visuals**: `merged.visuals` (array)
- **Status**: `ok | partial | error`

## Django Backend

### Models

**`Analysis`** model stores:
- `analysis_id` (UUID, primary key)
- `barcode`, `product_link`, `product_description` (optional)
- `objectives` (required - stores business_objective)
- `result_data` (JSONField - stores complete unified JSON)
- `status` (pending/processing/completed/error)
- `created_at`, `updated_at`

### Endpoints

1. **`POST /submit/`**
   - Accepts: `business_objective` (required), `barcode` OR `product_link` OR `product_description`
   - Returns: `{analysis_id, redirect_url}`
   - Creates `Analysis` record with status='pending'

2. **`GET /results/<analysis_id>/`**
   - Renders React app (same template as home)
   - React router handles the results page

3. **`GET /api/results/<analysis_id>/`** (NEW)
   - Returns saved analysis result for reload-safe results page
   - Returns: `{success, analysis_id, status, result}`

### WebSocket

**`ws/analysis/<analysis_id>/`**

Consumer (`AnalysisConsumer`):
- Joins group `analysis_<analysis_id>`
- Calls `API_Final_Agent` `/run-analysis` endpoint
- Sends status updates:
  - `{type: 'status', status: 'started', progress: 0}`
  - `{type: 'status', status: 'processing', progress: 30}`
  - `{type: 'final_result', payload: <unified_json>}`
- Saves result to `Analysis.result_data`
- Updates `Analysis.status` to 'completed' or 'error'

## React Frontend

### HomePage (`/`)

**Inputs:**
- `business_objective` (required, textarea)
- Input method selection (tabs):
  - **Barcode**: QuaggaJS scanner + manual input
  - **Product Link**: URL input
  - **Product Description**: Textarea

**Validation:**
- `business_objective` required
- At least one of barcode/link/description required

**Flow:**
1. User submits form
2. POST to `/submit/`
3. Receive `analysis_id`
4. Navigate to `/results/<analysis_id>/`

### ResultsPage (`/results/<analysis_id>/`)

**Reload-Safe:**
- On mount, tries to fetch saved result from `/api/results/<analysis_id>/`
- If found, displays immediately (no WebSocket needed)
- If not found, connects WebSocket for real-time updates

**WebSocket Flow:**
1. Connect to `ws/analysis/<analysis_id>/`
2. Receive status updates
3. Receive `final_result` with complete unified JSON
4. Display results

**Display Sections:**

1. **Main View** (from `merged`):
   - Product Image (if `image_front_url` exists)
   - Product Details
   - Performance Scores
   - Image Analysis
   - SWOT Analysis
   - Packaging Improvements
   - Go-to-Market Strategy
   - Evidence-Based Explanations
   - Quality Insights
   - Criteria Breakdown

2. **Visualizations** (if `merged.visuals` exists):
   - Uses `VisualsRenderer` component
   - Supports: base64 images, plotly charts, detected visuals
   - Rendered in dedicated accordion section

3. **Complete Analysis Data**:
   - Generic `KeyValueRenderer` for all `merged` fields
   - Dynamic rendering of any structure
   - Collapsible accordion

4. **Debug Panel** (collapsible):
   - `raw_sources.ace` (if exists)
   - `raw_sources.essence` (if exists)
   - Full merged data structure
   - Input echo

**Status Display:**
- Banner showing analysis status (ok/partial/error)
- Error messages if present
- Warning for partial results

## Components

### `KeyValueRenderer`
Generic recursive renderer for JSON data:
- Handles objects, arrays, primitives
- Accordion for nested structures
- Expandable long strings
- Max depth protection

### `VisualsRenderer`
Renders visual artifacts:
- **base64_image**: Direct `<img>` tag
- **plotly_chart**: Metadata + instructions
- **detected_visual**: Warning message
- **potential_base64**: Attempts image render

### `Accordion`
Reusable collapsible section component

### `ProgressBar`
Progress indicator for analysis status

### `BarcodeScanner`
QuaggaJS-based barcode scanner component

## Data Flow

### New Analysis

1. User submits form on HomePage
2. Django creates `Analysis` record
3. React navigates to `/results/<analysis_id>/`
4. ResultsPage connects WebSocket
5. Django consumer calls `API_Final_Agent`
6. `API_Final_Agent` runs ACE/Essence pipelines internally
7. Unified JSON returned to Django
8. Django saves to `Analysis.result_data`
9. Django sends via WebSocket to React
10. React displays results

### Reloaded Results Page

1. User refreshes `/results/<analysis_id>/`
2. ResultsPage fetches from `/api/results/<analysis_id>/`
3. If found, displays immediately
4. If not found, connects WebSocket (may be completed already)

## Error Handling

### Django
- Validation errors return 400 with error message
- Analysis errors saved to `Analysis.error_message`
- WebSocket sends user-friendly error messages

### React
- Form validation before submission
- Error state display
- Retry button on error
- Status banner for partial/error results

## Visual Rendering

### Base64 Images
```jsx
<img src={visual.data_or_url} alt={visual.title} />
```

### Plotly Charts
- Metadata displayed
- Instructions to use plotly.js
- Link to raw data in `raw_sources`

### Other Visuals
- Type and format information
- Path reference to raw data

## Testing

### Local Development

1. Start API_Final_Agent:
   ```bash
   cd API_Final_Agent
   python main.py
   ```

2. Start Django:
   ```bash
   python manage.py runserver
   ```

3. Access:
   - Home: `http://localhost:8000/`
   - Results: `http://localhost:8000/results/<analysis_id>/`

### Test Scenarios

1. **Barcode Analysis**:
   - Submit with barcode + objective
   - Verify ACE pipeline runs
   - Check results display

2. **Product Link Analysis**:
   - Submit with product_link + objective
   - Verify Essence pipeline runs
   - Check results display

3. **Product Description Analysis**:
   - Submit with product_description + objective
   - Verify Essence pipeline runs
   - Check results display

4. **Combined Analysis**:
   - Submit with barcode + product_link + objective
   - Verify both pipelines run
   - Check merged results

5. **Reload Test**:
   - Complete an analysis
   - Refresh results page
   - Verify saved result loads

6. **Error Handling**:
   - Submit invalid barcode
   - Verify error display
   - Check status banner

## Key Features

✅ **Zero Information Loss**: All data preserved in `raw_sources`  
✅ **Dynamic Rendering**: Generic components handle any JSON structure  
✅ **Visual Support**: Charts and images properly displayed  
✅ **Reload-Safe**: Results persist and reload correctly  
✅ **Error Handling**: Clear error states and messages  
✅ **Status Tracking**: Real-time progress and status updates  
✅ **Debug Mode**: Full raw data accessible  

## Future Enhancements

- [ ] Add plotly.js for interactive chart rendering
- [ ] Export results as PDF/JSON
- [ ] Comparison view for multiple analyses
- [ ] Historical analysis dashboard
- [ ] Real-time collaboration (multiple users)

