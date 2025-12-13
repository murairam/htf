# Manual Testing Guide - essenceAI

## Quick Test (5 minutes)

### Prerequisites
✅ App is running at http://localhost:8501
✅ API keys are set in `.env` file

---

## Test Scenario 1: Plant-Based Product Analysis

### Step 1: Open the App
1. Go to http://localhost:8501 in your browser
2. **Expected**: App loads with "essenceAI" title and sidebar

### Step 2: Enter Product Concept
1. In the text area, type: `Plant-based burger for French market`
2. **Expected**: Text appears in the input field

### Step 3: Select Options
1. **Category**: Select "Plant-Based"
2. **Target Segment**: Select "Skeptic"
3. **Expected**: Dropdowns work correctly

### Step 4: Generate Analysis
1. Click "🚀 Generate Market Intelligence"
2. **Expected**:
   - Loading spinner appears
   - Progress messages show
   - Results appear in ~10-30 seconds

### Step 5: Verify Results
Check that you see:
- ✅ **Competitor Benchmarking** table with 3 competitors
- ✅ **Marketing Strategy** text with recommendations
- ✅ **Scientific Sources** expandable section
- ✅ **Usage Statistics** showing API calls and cache hits

---

## Test Scenario 2: Precision Fermentation

### Quick Test
1. Enter: `Precision fermentation cheese alternative`
2. Category: "Precision Fermentation"
3. Segment: "High Essentialist"
4. Click Generate
5. **Expected**: Different competitors and strategy focused on "meat essence"

---

## Test Scenario 3: Algae-Based Product

### Quick Test
1. Enter: `Algae protein powder for athletes`
2. Category: "Algae"
3. Segment: "Non-Consumer"
4. Click Generate
5. **Expected**: Algae-specific competitors and familiar use-case messaging

---

## What to Check

### ✅ UI Elements
- [ ] Sidebar shows correctly
- [ ] Input field accepts text
- [ ] Dropdowns work
- [ ] Button is clickable
- [ ] Loading states appear

### ✅ Data Display
- [ ] Competitor table shows 3 rows
- [ ] Prices are in € format
- [ ] CO₂ values are reasonable
- [ ] Marketing claims are relevant

### ✅ Marketing Strategy
- [ ] Text is coherent and relevant
- [ ] Mentions the selected segment
- [ ] Provides actionable recommendations
- [ ] References research papers

### ✅ Citations
- [ ] "Verify Scientific Sources" expands
- [ ] Shows PDF filenames
- [ ] Page numbers included (if available)

### ✅ Statistics
- [ ] Shows API calls made
- [ ] Shows cache hits
- [ ] Cache efficiency percentage
- [ ] Total competitors in database

---

## Common Issues & Solutions

### Issue: "API Key not found"
**Solution**: Check `.env` file has:
```
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

### Issue: "Rate limit exceeded"
**Solution**:
- Wait 60 seconds
- Or use cached results (run same query again)

### Issue: No competitors shown
**Solution**:
- Check internet connection
- Verify Tavily API key is valid
- Fallback data should still appear

### Issue: No marketing strategy
**Solution**:
- Check OpenAI API key
- Verify you have API credits
- Check console for error messages

---

## Performance Benchmarks

### Expected Times
- **First run** (no cache): 15-30 seconds
- **Cached run**: 2-5 seconds
- **PDF indexing** (first time): 30-60 seconds

### Expected Costs (per analysis)
- **Without cache**: ~$0.05-0.10
- **With cache**: ~$0.01-0.02
- **80% reduction** after first run

---

## Testing Checklist

### Basic Functionality
- [ ] App loads without errors
- [ ] Can enter text
- [ ] Can select options
- [ ] Button triggers analysis
- [ ] Results display correctly

### All Categories
- [ ] Plant-Based works
- [ ] Precision Fermentation works
- [ ] Algae works

### All Segments
- [ ] High Essentialist works
- [ ] Skeptic works
- [ ] Non-Consumer works

### Caching
- [ ] First run takes longer
- [ ] Second run is faster
- [ ] Cache stats update
- [ ] Efficiency increases

---

## Quick Smoke Test (2 minutes)

Run this single test to verify everything works:

```
Product: "Plant-based milk alternative"
Category: Plant-Based
Segment: Skeptic
Expected: Results in <30 seconds with 3 competitors
```

If this works, your app is ready for the demo! 🎉

---

## Demo Preparation Tips

1. **Pre-cache your demo queries**
   - Run your demo scenarios once before presenting
   - This ensures fast response during the pitch

2. **Have backup examples ready**
   - Plant-Based: "Vegan cheese for pizza"
   - Fermentation: "Animal-free whey protein"
   - Algae: "Spirulina energy bars"

3. **Highlight the caching**
   - Show the statistics panel
   - Demonstrate the speed improvement
   - Emphasize the 80% cost reduction

4. **Show the citations**
   - Expand the "Verify Scientific Sources"
   - Point out the research papers
   - Emphasize scientific quality

---

**Last Updated**: December 13, 2024
