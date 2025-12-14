# Migration Guide: From Gateway to Unified Service

## What Changed

**Before:** API_Final_Agent was a gateway that made HTTP calls to separate ACE_Framework and EssenceAI services.

**After:** API_Final_Agent is a **single unified service** that merges both codebases internally.

## Key Differences

### Architecture

**Old:**
```
API_Final_Agent (gateway)
  ├─ HTTP → ACE_Framework (port 8001)
  └─ HTTP → EssenceAI (port 8002)
```

**New:**
```
API_Final_Agent (unified service)
  ├─ Internal ACE pipeline (no HTTP)
  └─ Internal Essence pipeline (no HTTP)
```

### Running Services

**Old:** Required 3 services running:
- ACE_Framework on port 8001
- EssenceAI on port 8002
- API_Final_Agent on port 8003

**New:** Only 1 service needed:
- API_Final_Agent on port 8003 (includes everything)

### Code Structure

**Old:**
- `services/orchestrator.py` - Made HTTP calls
- `services/normalizers/` - Normalized HTTP responses
- `essence_wrapper.py` - Separate wrapper service

**New:**
- `api_final_agent/ace/` - ACE code as internal module
- `api_final_agent/essence/` - Essence code as internal module
- `api_final_agent/pipelines/` - Internal pipeline runners
- `api_final_agent/unified_output.py` - Direct output merger

## Django Integration

**No changes needed!** Django already calls `APIFinalAgentClient` which points to `API_FINAL_AGENT_URL`.

The endpoint `/run-analysis` accepts the same request format, so Django integration is unchanged.

## Deployment

### Old Deployment

```bash
# Start 3 services
cd ACE_Framwork && uvicorn api:app --port 8001 &
cd essenceAI && python essence_wrapper.py &
cd API_Final_Agent && python main.py &
```

### New Deployment

```bash
# Start 1 service
cd API_Final_Agent && python main.py
```

That's it! Everything runs in one process.

## Benefits

1. **Simpler deployment**: One service instead of three
2. **Faster execution**: No HTTP overhead between pipelines
3. **Easier debugging**: All code in one place
4. **Better error handling**: Direct exception propagation
5. **Unified logging**: Single log stream

## Migration Steps

1. ✅ Codebases merged into `api_final_agent/ace/` and `api_final_agent/essence/`
2. ✅ Imports adapted for unified structure
3. ✅ Pipelines run internally (no HTTP)
4. ✅ Unified output builder created
5. ✅ Single endpoint `/run-analysis` implemented
6. ✅ Django integration unchanged (already compatible)

## Testing

Test the unified service:

```bash
# Start service
cd API_Final_Agent
python main.py

# Test with barcode
curl -X POST http://localhost:8003/run-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "business_objective": "Test objective",
    "barcode": "3017620422003"
  }'

# Test with product description
curl -X POST http://localhost:8003/run-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "business_objective": "Test objective",
    "product_description": "Plant-based product"
  }'
```

## Troubleshooting

### Import Errors

If you see import errors in ACE or Essence modules:

```bash
cd API_Final_Agent
python fix_imports.py
```

### Missing Dependencies

Install all dependencies:

```bash
cd API_Final_Agent
pip install -r requirements.txt
```

### EssenceAI Not Working

If EssenceAI dependencies are missing, the service will:
- Return mock data for Essence pipeline
- Continue working with ACE pipeline
- Set status to "partial"

This is intentional - the service degrades gracefully.

## Next Steps

1. Test the unified service locally
2. Run investigation tool: `POST /investigate`
3. Review schema reports in `artifacts/`
4. Refine unified output based on investigation
5. Deploy single service (no need for ACE/Essence separately)

## Summary

✅ **Single service** - No more gateway pattern
✅ **Internal pipelines** - No HTTP calls between services
✅ **Unified codebase** - Everything in one project
✅ **Django compatible** - No changes needed
✅ **Ready to deploy** - One command to run everything

