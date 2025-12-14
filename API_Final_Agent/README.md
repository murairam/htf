# API_Final_Agent - Unified Analysis Service

Single FastAPI service that merges ACE_Framework and EssenceAI pipelines into one unified codebase.

## Architecture

This service **fuses** the codebases of ACE_Framework and EssenceAI into a single project:

```
API_Final_Agent/
├── main.py                          # Single FastAPI app
├── api_final_agent/
│   ├── ace/                        # ACE_Framework code (internal module)
│   │   ├── agents.py
│   │   ├── config.py
│   │   ├── product_data.py
│   │   └── ...
│   ├── essence/                    # EssenceAI code (internal module)
│   │   ├── agents/
│   │   ├── rag_engine.py
│   │   └── ...
│   ├── pipelines/
│   │   ├── ace_pipeline.py        # Internal ACE runner
│   │   └── essence_pipeline.py    # Internal Essence runner
│   ├── unified_output.py           # Output merger
│   └── investigation.py           # Phase 2 investigation tool
├── tools/
│   └── (investigation tools)
└── artifacts/                      # Generated samples & reports
```

**Key Principle:** No HTTP calls between services. All pipelines run internally as Python modules.

## Installation

```bash
cd API_Final_Agent
pip install -r requirements.txt
```

### Optional: EssenceAI Full Support

For full EssenceAI functionality (not required - service works with mocks):

```bash
pip install llama-index>=0.10.0 llama-index-llms-openai>=0.1.0
```

## Configuration

Create a `.env` file or set environment variables:

```env
# Required for ACE pipeline
OPENAI_API_KEY=sk-your-key-here

# Optional: EssenceAI
TAVILY_API_KEY=your-tavily-key
```

## Running the Service

### Single Command

```bash
python main.py
```

The service will run on port 8003 (or `API_FINAL_AGENT_PORT` env var).

**No need to run ACE or EssenceAI separately** - everything runs in this single service.

## API Endpoints

### POST /run-analysis

Unified analysis endpoint.

**Request:**
```json
{
  "business_objective": "Increase flexitarian appeal",
  "barcode": "3017620422003",
  "product_link": "https://example.com/product",
  "product_description": "Plant-based chocolate spread"
}
```

**Validation:**
- `business_objective`: **required**
- At least one of: `barcode`, `product_link`, or `product_description` **required**

**Response:**
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

### POST /investigate

Run internal investigation to capture raw outputs from both pipelines.

Useful for Phase 2 - understanding output structures before refining unified format.

**Response:**
```json
{
  "status": "ok",
  "message": "Investigation complete. Check artifacts/ directory.",
  "results": {
    "ace_samples": 2,
    "essence_samples": 2,
    "artifacts_dir": "/path/to/artifacts"
  }
}
```

Generates:
- `artifacts/ace_raw_*.json`
- `artifacts/essence_raw_*.json`
- `artifacts/ace_schema_report.md`
- `artifacts/essence_schema_report.md`

## Example Requests

### With Barcode (ACE only)

```bash
curl -X POST http://localhost:8003/run-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "business_objective": "Increase market share",
    "barcode": "3017620422003"
  }'
```

### With Product Description (Essence only)

```bash
curl -X POST http://localhost:8003/run-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "business_objective": "Improve packaging design",
    "product_description": "Plant-based chocolate spread made from hazelnuts and cocoa"
  }'
```

### With Both (ACE + Essence)

```bash
curl -X POST http://localhost:8003/run-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "business_objective": "Comprehensive analysis",
    "barcode": "3017620422003",
    "product_description": "Plant-based chocolate spread"
  }'
```

## Output Fields Description

The unified output includes:

### Product Information
- Basic info (name, brand, category, product_id)
- Ingredients (text, count, additives)
- Nutrition (NOVA, NutriScore, nutriments)
- Labels and certifications
- Packaging (materials, recyclable)
- Origin and countries

### Analysis Results
- **Scoring Results**: Attractiveness, utility, positioning, global scores
- **SWOT Analysis**: Strengths, weaknesses, risks
- **Image Analysis**: Packaging description and visual observations
- **Packaging Improvements**: Actionable proposals
- **Go-to-Market Strategies**: Shelf positioning, B2B targeting, regional relevance
- **Evidence-Based Explanations**: Detailed reasoning for scores
- **Quality Insights**: Reflector analysis and improvement guidelines

### EssenceAI-Specific (if available)
- **Competitor Analysis**: Market intelligence
- **Research Insights**: Scientific paper insights
- **Marketing Strategy**: Recommendations based on research

### Raw Sources
- Complete raw outputs from both pipelines for traceability

## Development Workflow

1. **Phase 2: Investigation**
   ```bash
   curl -X POST http://localhost:8003/investigate
   ```
   Review `artifacts/*_schema_report.md` to understand output structures.

2. **Refine Unified Output**
   Update `api_final_agent/unified_output.py` based on investigation results.

3. **Test**
   Run analysis requests and verify merged output.

## Integration with Django

Django calls this single service:

```python
# In marketing_analyzer/fastapi_final_client.py
client = APIFinalAgentClient()
success, result = client.run_analysis(
    analysis_id=analysis_id,
    business_objective=request.business_objective,
    barcode=request.barcode,
    product_link=request.product_link,
    product_description=request.product_description
)
```

**No need to run ACE or EssenceAI separately** - this service handles everything internally.

## Troubleshooting

### Import Errors

If you see import errors, run:
```bash
python fix_imports.py
```

### EssenceAI Not Available

If EssenceAI dependencies are missing, the service will:
- Return mock data for Essence pipeline
- Continue working with ACE pipeline
- Set status to "partial" if only one pipeline succeeds

### ACE Pipeline Errors

Check that `OPENAI_API_KEY` is set:
```bash
export OPENAI_API_KEY='sk-your-key-here'
```

## Project Structure

- **Single FastAPI app**: `main.py`
- **Internal pipelines**: No HTTP calls, direct Python imports
- **Unified output**: One consistent JSON format
- **Investigation tools**: For understanding output structures
- **No external dependencies**: Everything runs in one process

## Status

✅ Phase 0: Codebase fusion complete
✅ Phase 1: Unified input model
✅ Phase 2: Investigation tool
✅ Phase 3: Unified output builder
✅ Phase 4: Single endpoint

**Ready for testing!**
