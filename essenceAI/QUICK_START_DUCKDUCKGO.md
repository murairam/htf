# Quick Start: DuckDuckGo Fallback

## What Changed?

✅ **Agents now always search the real web when Tavily fails**
❌ **NO MORE AI-generated estimates**

## Installation

```bash
cd essenceAI
pip install duckduckgo-search
```

## Testing

### Run the Full Test Suite
```bash
python test_duckduckgo_fallback.py
```

### Quick Manual Test
```python
from src.competitor_data import OptimizedCompetitorIntelligence

# Create instance
intel = OptimizedCompetitorIntelligence()

# Search for competitors
competitors = intel.get_competitors(
    product_concept="plant-based burger",
    category="Plant-Based",
    max_results=5
)

# Check results
for comp in competitors:
    print(f"{comp['Company']}: {comp['Source']}")
    # Source should NEVER say "AI Generated"
```

### Test Without Tavily
```python
import os

# Temporarily disable Tavily
if "TAVILY_API_KEY" in os.environ:
    del os.environ["TAVILY_API_KEY"]

# Now test - should use DuckDuckGo
intel = OptimizedCompetitorIntelligence()
competitors = intel.get_competitors(
    product_concept="precision fermentation protein",
    category="Precision Fermentation",
    max_results=3
)

print(f"Found {len(competitors)} competitors via DuckDuckGo")
```

## Verification Checklist

- [ ] `pip install duckduckgo-search` completed successfully
- [ ] Test suite passes: `python test_duckduckgo_fallback.py`
- [ ] No "AI Generated" in Source fields
- [ ] Logs show "DuckDuckGo" when Tavily unavailable
- [ ] Real web URLs in Source fields

## Fallback Chain

```
1. Tavily API ────────────► Real-time web search
         │
         │ (if fails)
         ▼
2. DuckDuckGo ────────────► Free web search (NEW!)
         │
         │ (if fails)
         ▼
3. Static Fallback ───────► Real company data
```

**❌ REMOVED: OpenAI AI estimates**

## Expected Behavior

### When Tavily Works
```
✓ Tavily API initialized successfully
✓ Successfully extracted 5 competitors via Tavily
```

### When Tavily Fails (NEW!)
```
⚠ Tavily unavailable - falling back to DuckDuckGo web search
✓ DuckDuckGo search initialized successfully
✓ Searching DuckDuckGo: Plant-Based companies products...
✓ Successfully extracted 5 competitors via DuckDuckGo
```

### When All Web Search Fails
```
⚠ All web search methods failed - using static fallback data
✓ Using static fallback data for category: Plant-Based
```

## Troubleshooting

### Issue: "DuckDuckGo not available"
**Solution:**
```bash
pip install duckduckgo-search
```

### Issue: "Rate limit exceeded"
**Solution:** DuckDuckGo may rate limit. Wait a few seconds and try again, or the system will automatically use static fallback.

### Issue: "No results found"
**Solution:** This is normal if the search query is too specific. The system will use static fallback data.

## Documentation

- Full details: `DUCKDUCKGO_FALLBACK_IMPLEMENTATION.md`
- Test suite: `test_duckduckgo_fallback.py`
- Implementation: `src/competitor_data.py`

## Support

If you encounter issues:
1. Check logs for error messages
2. Verify `duckduckgo-search` is installed
3. Run test suite to identify problems
4. Review `DUCKDUCKGO_FALLBACK_IMPLEMENTATION.md`
