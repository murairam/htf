# Weaviate Cloud Setup Guide

## Why Weaviate?

**Problem**: Every time you build the index, you pay for embeddings again (and hit rate limits).

**Solution**: Store embeddings in Weaviate Cloud. You only pay for embeddings ONCE, then load them instantly!

## Benefits

✅ **One-time embedding cost** - Embeddings stored in cloud  
✅ **Instant loading** - No rebuilding index every time  
✅ **No rate limits** - Only hit API once during initial setup  
✅ **Free tier available** - 14-day free sandbox cluster  
✅ **Persistent storage** - Embeddings survive restarts  

## Setup Steps

### 1. Create Free Weaviate Cloud Account

1. Go to https://console.weaviate.cloud
2. Sign up for free account
3. Create a new cluster:
   - Click "Create Cluster"
   - Choose "Sandbox" (free for 14 days)
   - Select region closest to you
   - Click "Create"

### 2. Get Your Credentials

After cluster is created:

1. Click on your cluster
2. Copy the **Cluster URL** (looks like: `https://xxxxx.weaviate.network`)
3. Go to "API Keys" tab
4. Copy the **Admin API Key**

### 3. Configure Environment Variables

Add to your `.env` file:

```bash
# Existing
OPENAI_API_KEY=your_openai_key_here

# Add these for Weaviate
WEAVIATE_URL=https://your-cluster.weaviate.network
WEAVIATE_API_KEY=your_weaviate_admin_key_here
```

### 4. Install Weaviate Client

```bash
cd /vercel/sandbox/essenceAI
pip install weaviate-client
```

### 5. Update Your App

**Option A: Use Weaviate by default (recommended)**

Edit `src/app.py`:

```python
# Change line 17:
from rag_engine_weaviate import WeaviateRAGEngine

# Change line 138:
st.session_state.rag_engine = WeaviateRAGEngine(data_dir=str(data_dir))
```

**Option B: Keep both options**

Edit `src/app.py` to let users choose:

```python
from rag_engine_optimized import OptimizedRAGEngine
from rag_engine_weaviate import WeaviateRAGEngine

# In sidebar:
use_weaviate = st.checkbox("Use Weaviate Cloud (faster, no rate limits)", value=True)

if st.button("🔄 Initialize Research Database"):
    if use_weaviate:
        st.session_state.rag_engine = WeaviateRAGEngine(data_dir=str(data_dir))
    else:
        st.session_state.rag_engine = OptimizedRAGEngine(data_dir=str(data_dir))
```

## Usage

### First Time (One-time setup)

```bash
cd /vercel/sandbox/essenceAI
export OPENAI_API_KEY="your-key"
export WEAVIATE_URL="https://your-cluster.weaviate.network"
export WEAVIATE_API_KEY="your-weaviate-key"

python -c "
from src.rag_engine_weaviate import WeaviateRAGEngine
engine = WeaviateRAGEngine(data_dir='data')
engine.initialize_index()
print('✅ Embeddings stored in Weaviate!')
"
```

This will take 5-10 minutes with rate limiting, but **you only do it once**!

### Every Time After

```bash
# Loads instantly from Weaviate!
python -c "
from src.rag_engine_weaviate import WeaviateRAGEngine
engine = WeaviateRAGEngine(data_dir='data')
engine.initialize_index()  # Loads in <1 second!
"
```

## Cost Comparison

### Without Weaviate (Current)
- **Every run**: Pay for embeddings (~$0.003)
- **10 runs**: $0.03
- **100 runs**: $0.30
- **Problem**: Rate limits every time

### With Weaviate
- **First run**: Pay for embeddings (~$0.003)
- **Every other run**: FREE (loads from Weaviate)
- **10 runs**: $0.003
- **100 runs**: $0.003
- **Benefit**: No rate limits after first run!

## Testing

### Test Rate-Limited Local Version

```bash
cd /vercel/sandbox/essenceAI
python test_rag_fix.py
```

### Test Weaviate Version

```bash
cd /vercel/sandbox/essenceAI
python test_weaviate.py
```

## Troubleshooting

### "WEAVIATE_URL not set"

Make sure you've added Weaviate credentials to `.env`:

```bash
cp .env.example .env
# Edit .env and add:
WEAVIATE_URL=https://your-cluster.weaviate.network
WEAVIATE_API_KEY=your-key
```

### "weaviate-client not installed"

```bash
pip install weaviate-client
```

### Connection errors

1. Check your cluster is running in Weaviate console
2. Verify the URL is correct (should start with `https://`)
3. Make sure API key is the Admin key, not Read-only

### Want to rebuild index

```bash
python -c "
from src.rag_engine_weaviate import WeaviateRAGEngine
engine = WeaviateRAGEngine(data_dir='data')
engine.initialize_index(force_reload=True)  # Rebuilds from scratch
"
```

## Migration from Local to Weaviate

If you've been using the local version:

1. Set up Weaviate (steps above)
2. Run initial index build (one time)
3. Update app.py to use WeaviateRAGEngine
4. Delete old `.storage` directory (optional)

```bash
cd /vercel/sandbox/essenceAI
rm -rf .storage  # Old local storage (no longer needed)
```

## Free Tier Limits

Weaviate Sandbox (free):
- **Duration**: 14 days
- **Storage**: 1 GB
- **Requests**: Unlimited
- **Perfect for**: Development and hackathons

For production, upgrade to paid tier (~$25/month).

## Summary

**Immediate Fix** (works now):
- Use `OptimizedRAGEngine` with rate limiting
- Takes 5-10 minutes every time
- Hits rate limits but retries automatically

**Better Solution** (recommended):
- Use `WeaviateRAGEngine` with cloud storage
- Takes 5-10 minutes ONCE
- Then loads instantly forever
- No more rate limit issues!

Choose based on your needs:
- **Quick test**: Use rate-limited local version
- **Production/Demo**: Use Weaviate version
