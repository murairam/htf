# Final JSON Contract - API_Final_Agent Unified Output

This document describes the exact structure of the unified JSON response from `API_Final_Agent` `POST /run-analysis` endpoint.

## Top-Level Structure

```json
{
  "analysis_id": "string (UUID)",
  "input": {
    "business_objective": "string (required)",
    "barcode": "string | null",
    "product_link": "string | null",
    "product_description": "string | null",
    "domain": "string | null",
    "segment": "string | null"
  },
  "status": "ok | partial | error",
  "timestamp": "ISO 8601 datetime string",
  "merged": {
    // Main display content - see Merged Section below
  },
  "raw_sources": {
    "ace": {
      // Complete ACE pipeline output (or null)
    },
    "essence": {
      // Complete Essence pipeline output (or null)
    }
  },
  "errors": [
    {
      "source": "ace | essence",
      "error": "error message string"
    }
  ]
}
```

## Main Display Content Location

**Location:** `merged` (top-level key)

The `merged` section contains the intelligently combined and normalized data from both ACE and Essence pipelines. This is the **primary content** that should be displayed to users.

### Merged Section Structure

The `merged` section is **data-driven** and may contain any of the following fields (depending on which pipelines ran successfully):

#### Product Information
- `product_information` - Product details (name, brand, ingredients, nutrition, etc.)
- `image_front_url` - Product image URL (from OpenFoodFacts)

#### Business Objectives
- `business_objectives` - Array of objectives from all sources:
  ```json
  [
    {"source": "input", "objective": "..."},
    {"source": "ace", "objective": "..."},
    {"source": "essence", "objective": "..."}
  ]
  ```

#### Scoring & Analysis (from ACE)
- `scoring_results` - Scores (attractiveness, utility, positioning, global)
- `swot_analysis` - Array of SWOT analyses from different sources
- `evidence_based_explanations` - Explanations for scores
- `quality_insights` - Quality analysis and improvement guidelines

#### Image Analysis (from ACE)
- `image_analysis` - Package description, visual observations, detected problems

#### Improvements & Strategy
- `packaging_improvements` - Array of improvement proposals
- `go_to_market_strategies` - Array of GTM strategies
- `marketing_strategy` - Marketing strategy (from Essence)

#### Market Intelligence (from Essence)
- `competitor_analysis` - Competitor data and analysis
- `research_insights` - Research findings
- `workflow` - Workflow steps executed

#### Visualizations
- `visuals` - Array of visual artifacts:
  ```json
  [
    {
      "path": "string (dot notation path)",
      "title": "string",
      "type": "base64_image | plotly_chart | detected_visual | potential_base64",
      "format": "string (e.g., 'image/png', 'plotly_json')",
      "data_or_url": "string (base64 data URI or path reference)",
      "source": "ace | essence (optional)"
    }
  ]
  ```

#### Unhandled Fields
- Fields not explicitly handled are preserved with prefixes:
  - `ace_<field_name>` - Unhandled ACE fields
  - `essence_<field_name>` - Unhandled Essence fields

## Raw Sources Location

**Location:** `raw_sources` (top-level key)

The `raw_sources` section contains the **complete, unmodified** outputs from both pipelines:

- `raw_sources.ace` - Complete ACE pipeline output (or `null` if ACE didn't run)
- `raw_sources.essence` - Complete Essence pipeline output (or `null` if Essence didn't run)

These should be displayed in a **collapsible Debug panel** for developers and power users.

## Visuals/Charts Location

**Location:** `merged.visuals` (array)

Visual artifacts are detected and included in `merged.visuals` as an array of visual objects.

### Visual Types

1. **base64_image**
   - `data_or_url` contains a base64 data URI (e.g., `data:image/png;base64,...`)
   - **Rendering:** Render directly as `<img src={data_or_url}>`

2. **plotly_chart**
   - `data_or_url` contains a path reference to the chart data
   - Chart data structure exists in `raw_sources` at the specified path
   - **Rendering:** 
     - Option 1: Use plotly.js to render interactively (requires plotly.js library)
     - Option 2: Show metadata and link to raw data
     - Option 3: Convert to static image if possible

3. **detected_visual**
   - Visual artifact detected but format unknown
   - **Rendering:** Display metadata and path

4. **potential_base64**
   - Potential base64 image but not confirmed
   - **Rendering:** Attempt to render as image, fallback to metadata

## Status Values

- `ok` - Both ACE and Essence pipelines completed successfully
- `partial` - One pipeline succeeded, one failed
- `error` - Both pipelines failed

## Rendering Strategy

### Primary Display (Main View)
1. Display `merged` content as the primary view
2. Use dynamic rendering - don't hardcode field names
3. For objects: Render as key-value pairs or cards
4. For arrays: Render as lists
5. For long text: Render in paragraphs

### Visuals Section
1. Check if `merged.visuals` exists and has items
2. Render each visual according to its type:
   - **base64_image:** Direct `<img>` tag
   - **plotly_chart:** Metadata + link to raw data (or plotly.js if available)
   - **Other:** Metadata display

### Debug Panel
1. Collapsible section (default: collapsed)
2. Display `raw_sources.ace` (if not null)
3. Display `raw_sources.essence` (if not null)
4. Format as JSON with syntax highlighting

### Error Handling
1. If `status === "error"`: Display error message prominently
2. If `status === "partial"`: Show warning that some data may be missing
3. Display `errors` array if present

## Example Response

```json
{
  "analysis_id": "123e4567-e89b-12d3-a456-426614174000",
  "input": {
    "business_objective": "Increase flexitarian appeal",
    "barcode": "3017620422003",
    "product_link": null,
    "product_description": null
  },
  "status": "ok",
  "timestamp": "2025-01-15T10:30:00Z",
  "merged": {
    "product_information": {
      "basic_info": {
        "name": "Product Name",
        "brand": "Brand Name"
      }
    },
    "scoring_results": {
      "scores": {
        "global_score": 75.5
      }
    },
    "visuals": [
      {
        "path": "competitor_analysis.charts.price_comparison",
        "title": "Price Comparison",
        "type": "plotly_chart",
        "format": "plotly_json"
      }
    ]
  },
  "raw_sources": {
    "ace": { /* complete ACE output */ },
    "essence": { /* complete Essence output */ }
  },
  "errors": []
}
```

## Key Principles

1. **Zero Loss:** All data from ACE and Essence is preserved (either in `merged` or `raw_sources`)
2. **Data-Driven:** Don't assume fixed fields - render what exists
3. **Traceability:** `raw_sources` provides complete traceability
4. **Flexibility:** Structure adapts to which pipelines ran successfully

