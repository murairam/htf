# 🧪 Testing Checklist for essenceAI

Use this checklist before recording your demo video and submitting!

## ✅ Pre-Flight Checks

### 1. Environment Setup
- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with API keys
- [ ] OpenAI API key is valid and has credits
- [ ] (Optional) Tavily API key configured

### 2. Data Files
- [ ] PDFs are in `essenceAI/data/` folder
- [ ] At least 5 research PDFs present
- [ ] PDFs are readable (not corrupted)

### 3. File Structure
```
essenceAI/
├── src/
│   ├── app.py ✓
│   ├── rag_engine.py ✓
│   └── competitor_data.py ✓
├── data/
│   └── *.pdf (9 files) ✓
├── requirements.txt ✓
├── .env (you create this) ⚠️
└── README.md ✓
```

## 🧪 Functional Tests

### Test 1: App Launches
```bash
cd essenceAI
streamlit run src/app.py
```

**Expected Result:**
- [ ] App opens in browser at `http://localhost:8501`
- [ ] No error messages in terminal
- [ ] UI loads completely
- [ ] Sidebar shows API status

**If it fails:**
- Check if port 8501 is already in use
- Verify all dependencies are installed
- Check for Python syntax errors

---

### Test 2: API Configuration Check

**In the sidebar, verify:**
- [ ] ✅ OpenAI API (green checkmark)
- [ ] ✅ or ⚠️ Tavily API (green or warning)

**If OpenAI shows ❌:**
- Check `.env` file exists
- Verify `OPENAI_API_KEY=sk-...` is correct
- Restart the app

---

### Test 3: Research Database Initialization

**Steps:**
1. Click "🔄 Initialize Research Database" in sidebar
2. Wait for processing (30-60 seconds first time)

**Expected Result:**
- [ ] Progress bar appears
- [ ] Message: "✓ Index loaded successfully" or "✓ Index created"
- [ ] No error messages

**If it fails:**
- Check if PDFs are in `data/` folder
- Verify PDFs are not corrupted
- Check OpenAI API key is valid
- Look for error message details

---

### Test 4: Competitor Analysis (Precision Fermentation)

**Steps:**
1. Select Domain: "Precision Fermentation"
2. Select Segment: "Skeptic"
3. Enter: "Precision fermented artisan cheese for European market"
4. Click "🚀 Analyze Market"
5. Go to "Competitor Intelligence" tab

**Expected Result:**
- [ ] Loading spinner appears
- [ ] Competitor table displays (3-5 companies)
- [ ] Metrics show: Avg Price, Avg CO₂, Competitor Count
- [ ] Charts render correctly (Price comparison, CO₂ comparison)
- [ ] Data looks realistic (not all zeros or identical)

**Check the data:**
- [ ] Company names are real (e.g., Perfect Day, Remilk)
- [ ] Prices are reasonable ($20-60/kg range)
- [ ] CO₂ values are realistic (1-3 kg range)

---

### Test 5: Marketing Strategy with Citations

**Steps:**
1. Same product concept as Test 4
2. Go to "Marketing Strategy" tab
3. Wait for analysis

**Expected Result:**
- [ ] Strategy text appears (2-3 paragraphs)
- [ ] Strategy mentions the selected segment ("Skeptic")
- [ ] "View Research Citations" expander is present
- [ ] Click expander - citations appear
- [ ] Each citation shows:
  - [ ] Source file name (e.g., "Cheon_et_al_2025")
  - [ ] Page number
  - [ ] Relevance score
  - [ ] Text excerpt

**Quality Check:**
- [ ] Strategy is specific (not generic)
- [ ] Mentions psychological factors
- [ ] Provides actionable recommendations
- [ ] Citations are from actual research papers

---

### Test 6: Research Insights

**Steps:**
1. Go to "Research Insights" tab
2. Wait for analysis

**Expected Result:**
- [ ] Insights text appears
- [ ] Mentions consumer acceptance factors
- [ ] "Research Sources" expander shows citations
- [ ] Citations reference the PDFs in data folder

---

### Test 7: Plant-Based Domain

**Repeat Tests 4-6 with:**
- Domain: "Plant-Based"
- Segment: "High Essentialist"
- Product: "Plant-based burger emphasizing juicy texture and beefy flavor"

**Expected Result:**
- [ ] Different competitors appear (Beyond Meat, Impossible Foods)
- [ ] Strategy emphasizes sensory mimicry (for High Essentialist)
- [ ] Charts update with new data

---

### Test 8: Algae Domain

**Repeat Tests 4-6 with:**
- Domain: "Algae"
- Segment: "Non-Consumer"
- Product: "Algae-based protein powder for athletes"

**Expected Result:**
- [ ] Algae-specific competitors (Algama, Sophie's BioNutrients)
- [ ] Strategy focuses on familiarity (for Non-Consumer)
- [ ] Lower CO₂ emissions shown (algae is very sustainable)

---

## 🎬 Demo Video Preparation

### Before Recording:
- [ ] Close unnecessary browser tabs
- [ ] Clear browser cache
- [ ] Restart the app for fresh session
- [ ] Prepare your script (< 2 minutes)
- [ ] Test your microphone
- [ ] Use Loom or similar screen recorder

### During Recording:
- [ ] Show the homepage briefly
- [ ] Enter a product concept
- [ ] Narrate what's happening
- [ ] Show competitor data
- [ ] **IMPORTANT:** Click "View Research Citations"
- [ ] Explain the value proposition
- [ ] Keep it under 2 minutes!

### Script Template:
```
"essenceAI is a B2B intelligence platform for sustainable food companies.

[Enter product concept]

It fetches real-time competitor data using AI...
[Show competitor table and charts]

And provides marketing strategies backed by scientific research...
[Show strategy tab]

Every recommendation includes citations from peer-reviewed papers...
[Click and show citations]

This helps food-tech companies make faster, data-driven decisions
that accelerate the transition to sustainable food."
```

---

## 🐛 Common Issues & Fixes

### Issue: "OPENAI_API_KEY not found"
**Fix:**
```bash
# Make sure .env file exists in essenceAI directory
cd essenceAI
cat .env  # Should show your API key
```

### Issue: "No PDF files found"
**Fix:**
```bash
# Copy PDFs to data folder
cp ../hackthefork/*.pdf data/
ls data/*.pdf  # Should show 9 PDFs
```

### Issue: "Module not found: streamlit"
**Fix:**
```bash
pip install -r requirements.txt
# Or
pip install streamlit llama-index pandas plotly
```

### Issue: Competitor data looks fake/identical
**Fix:**
- This means Tavily API isn't working
- Check if `TAVILY_API_KEY` is in `.env`
- It's okay! OpenAI will generate realistic data
- For demo, explain it's using AI-generated market estimates

### Issue: Citations not showing
**Fix:**
- Make sure you clicked "Initialize Research Database"
- Wait for indexing to complete
- Check if PDFs are in data folder
- Restart app and try again

### Issue: App is slow
**Fix:**
- First run is always slower (indexing PDFs)
- Subsequent runs use cached index
- Tavily API calls take 2-3 seconds (normal)
- LlamaIndex queries take 3-5 seconds (normal)

---

## ✅ Final Checklist Before Submission

- [ ] All tests passed
- [ ] Demo video recorded (< 2 minutes)
- [ ] Video uploaded (YouTube/Loom link)
- [ ] Code pushed to GitHub
- [ ] README.md is clear
- [ ] .env file NOT committed (check .gitignore)
- [ ] All team members credited
- [ ] Submission form completed
- [ ] Submitted before Sunday 4 PM!

---

## 🎯 Quality Assurance

### The app should demonstrate:
1. ✅ **Real-time data** - Not hardcoded
2. ✅ **Scientific citations** - Verifiable sources
3. ✅ **Professional UI** - Clean, modern design
4. ✅ **Fast performance** - Responds in seconds
5. ✅ **Clear value** - Obvious B2B use case

### Red flags to avoid:
- ❌ Hardcoded/mock data without API calls
- ❌ No citations or fake citations
- ❌ Broken UI or error messages
- ❌ Slow (> 30 seconds) responses
- ❌ Unclear value proposition

---

## 📞 Need Help?

If something isn't working:
1. Check this checklist again
2. Read error messages carefully
3. Check the QUICKSTART.md guide
4. Verify API keys are correct
5. Try restarting the app

**Remember:** The judges care about:
- ✅ Functional prototype
- ✅ Scientific quality (citations!)
- ✅ Economic feasibility (B2B model)
- ✅ Environmental relevance (CO₂ data)

Good luck! 🚀🌱
