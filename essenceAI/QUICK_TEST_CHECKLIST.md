# Quick Test Checklist - Optional Segment Feature

## 🧪 Test Session: Optional Consumer Segment

**Date**: December 13, 2024
**Feature**: Make consumer segment targeting optional
**Time Estimate**: 5 minutes

---

## Pre-Test Setup

✅ App running at: http://localhost:8501
✅ Changes deployed: Optional segment checkbox added
✅ New method: `get_general_strategy()` implemented

---

## Test 1: UI - Checkbox Interaction (1 min)

### Steps:
1. Open http://localhost:8501 in your browser
2. Look at the sidebar under "🧠 Target Consumer Segment"
3. Verify you see:
   - [ ] Text: "*Optional: Add psychological targeting*"
   - [ ] Checkbox: "Enable segment-specific insights" (unchecked by default)
   - [ ] Segment dropdown is HIDDEN when unchecked

4. Click the checkbox to enable it
5. Verify:
   - [ ] Segment dropdown appears
   - [ ] Shows 3 options: Skeptic, High Essentialist, Non-Consumer

6. Uncheck the checkbox
7. Verify:
   - [ ] Segment dropdown disappears again

**Result**: ✅ Pass / ❌ Fail

---

## Test 2: General Strategy Mode (2 min)

### Steps:
1. Make sure checkbox is **UNCHECKED** (segment disabled)
2. Select category: "Plant-Based"
3. Enter product: "Plant-based burger for French market"
4. Click "🚀 Analyze Market"
5. Go to "🧠 Marketing Strategy" tab

### Expected Results:
- [ ] Analysis completes without errors
- [ ] Header shows: "📝 General Marketing Strategy" (not "Recommended Strategy")
- [ ] Strategy text appears with general recommendations
- [ ] Blue info box appears with tip: "💡 **Tip:** Enable 'segment-specific insights'..."
- [ ] NO segment explanation section at the bottom
- [ ] Citations still appear in "📚 Scientific Sources"

**Result**: ✅ Pass / ❌ Fail

**Notes**: _____________________________________

---

## Test 3: Segment-Specific Mode (2 min)

### Steps:
1. **CHECK** the "Enable segment-specific insights" checkbox
2. Select segment: "Skeptic"
3. Keep same product: "Plant-based burger for French market"
4. Click "🚀 Analyze Market" again
5. Go to "🧠 Marketing Strategy" tab

### Expected Results:
- [ ] Analysis completes without errors
- [ ] Header shows: "📝 Recommended Strategy"
- [ ] Shows: "**Target Segment:** Skeptic"
- [ ] Strategy text is tailored to Skeptics
- [ ] NO blue tip box about enabling segments
- [ ] Segment explanation section appears at bottom with 3 columns:
  - Description
  - Key Insight
  - Strategy
- [ ] Citations appear in "📚 Scientific Sources"

**Result**: ✅ Pass / ❌ Fail

**Notes**: _____________________________________

---

## Quick Smoke Tests (Optional - 30 seconds each)

### Test Different Segments:
- [ ] High Essentialist - Strategy mentions "essence" or "mimicry"
- [ ] Non-Consumer - Strategy mentions "familiar" or "ease of use"

### Test Different Categories:
- [ ] Precision Fermentation (general mode)
- [ ] Algae (segment mode)

---

## Summary

**Total Tests**: 3 core tests
**Passed**: _____ / 3
**Failed**: _____ / 3

### Issues Found:
1. _____________________________________
2. _____________________________________
3. _____________________________________

### Overall Status:
- [ ] ✅ Ready for demo
- [ ] ⚠️ Minor issues (can proceed)
- [ ] ❌ Blocking issues (needs fix)

---

## Quick Fix Guide

### If checkbox doesn't toggle dropdown:
- Refresh the page (Ctrl+R or Cmd+R)
- Check browser console for errors (F12)

### If "get_general_strategy" error appears:
- The method might not be loaded
- Restart Streamlit: `Ctrl+C` then `streamlit run src/app.py`

### If analysis hangs:
- Check API keys in `.env` file
- Check terminal for error messages
- Try with segment enabled first (uses existing method)

---

**Tester**: _____________________
**Completion Time**: _____________________
**Ready for Hackathon**: ✅ Yes / ❌ No
