# Quick Start - Rate Limit Fix

## 🚨 Problem
Getting `429 Too Many Requests` errors when building embeddings.

## ✅ Two Solutions Available

### Solution 1: Rate-Limited (Works Now) ⚡

**No setup required - just run it!**

```bash
cd /vercel/sandbox/essenceAI
export OPENAI_API_KEY="your-key"
python test_rag_fix.py
```

- ⏳ Takes 5-10 minutes
- ✅ Will complete successfully
- 🔄 Needs to run every time

### Solution 2: Weaviate Cloud (Recommended) 🚀

**5-minute setup, then instant forever!**

```bash
# 1. Get free Weaviate cluster
# Go to: https://console.weaviate.cloud
# Create sandbox cluster, copy URL and API key

# 2. Install and test
cd /vercel/sandbox/essenceAI
pip install weaviate-client
export OPENAI_API_KEY="your-openai-key"
export WEAVIATE_URL="https://your-cluster.weaviate.network"
export WEAVIATE_API_KEY="your-weaviate-key"
python test_weaviate.py
```

- ⏳ First time: 5-10 minutes
- ⚡ After that: <1 second
- 💰 One-time embedding cost

## 📊 Comparison

| Feature | Rate-Limited | Weaviate |
|---------|--------------|----------|
| Setup time | 0 min | 5 min |
| First run | 5-10 min | 5-10 min |
| Second run | 5-10 min | <1 sec |
| Rate limits | Rare | None |
| Cost per run | $0.003 | $0.003 (first only) |

## 🎯 Recommendation

- **Quick test**: Use rate-limited version
- **Development/Demo**: Use Weaviate version

## 📚 Full Documentation

- `RATE_LIMIT_SOLUTION.md` - Complete guide
- `WEAVIATE_SETUP.md` - Weaviate setup steps
- `RATE_LIMIT_FIX.md` - Original fix details

## 🆘 Help

Both solutions work! Choose based on your needs:

**Just want it to work now?**
→ Use rate-limited version (no setup)

**Want it fast after first time?**
→ Use Weaviate version (5-min setup)
