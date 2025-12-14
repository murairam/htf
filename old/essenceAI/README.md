# essenceAI - B2B Market Intelligence Platform

**Sustainable Food Innovation Intelligence for Precision Fermentation, Plant-Based, and Algae sectors**

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd essenceAI
pip install -r requirements.txt
```

### 2. Set Up API Keys

Create a `.env` file in the `essenceAI` directory:

```bash
# Required: OpenAI API Key (you have credits)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: For better web search (free tier: 1000 requests/month)
# Sign up at https://tavily.com
TAVILY_API_KEY=your_tavily_api_key_here

# Optional: If using Claude instead of GPT-4
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Choose LLM provider: "openai" or "anthropic"
LLM_PROVIDER=openai
```

### 3. Add Research PDFs

Copy the hackathon research PDFs to the `data` folder:

```bash
cp ../hackthefork/*.pdf data/
```

### 4. Run the Application

```bash
streamlit run src/app.py
```

## 🏗️ Architecture

### Real-Time Data Sources

1. **Tavily API** (Free Tier) - Web search for competitor data
2. **OpenAI GPT-4o** - Intelligent data extraction and analysis
3. **LlamaIndex RAG** - Scientific paper analysis with citations

### How It Works

```
User Query → Tavily Search → OpenAI Extraction → Structured Data
              ↓
         Research PDFs → LlamaIndex → Cited Insights
              ↓
         Combined Intelligence → Dashboard
```

## 📊 Features

- **Real-time competitor analysis** - Live market data, not mock data
- **Scientific citations** - Every insight backed by research papers
- **Psychological segmentation** - Marketing strategies based on Food Essentialism research
- **Environmental benchmarking** - CO2 emissions and sustainability metrics

## 🎯 Hackathon Alignment

- ✅ **Economic Feasibility** - B2B SaaS model with clear revenue path
- ✅ **Environmental Relevance** - Accelerates sustainable food adoption
- ✅ **Scientific Quality** - Cites peer-reviewed research (Cheon et al., Flint et al.)
- ✅ **Technical Authenticity** - Real APIs, live data, functional prototype

## 🔧 API Setup Instructions

### Tavily API (Recommended - Free Tier)

1. Go to https://tavily.com
2. Sign up for free account
3. Get API key (1000 free searches/month)
4. Add to `.env` file

### OpenAI API (Required)

You already have credits! Just add your key to `.env`

## 📁 Project Structure

```
essenceAI/
├── src/
│   ├── app.py              # Streamlit UI
│   ├── rag_engine.py       # LlamaIndex + Citations
│   └── competitor_data.py  # Real-time data fetching
├── data/                   # Research PDFs go here
├── requirements.txt
└── .env                    # Your API keys (create this)
```

## 🎬 Demo Flow

1. User enters product concept: "Algae-based protein bar for athletes"
2. System searches real competitors via Tavily/OpenAI
3. RAG engine analyzes research papers for marketing insights
4. Dashboard shows:
   - Real competitor benchmarks (prices, CO2)
   - Cited marketing strategy (from research)
   - Market opportunity analysis

## 🏆 Winning Strategy

This architecture ensures:
- **No hallucinated data** - Real APIs + fallback logic
- **Verifiable sources** - Every claim has a citation
- **Fast MVP** - Works in 24 hours
- **Scalable** - Easy to add more data sources

## 📝 Next Steps

1. Set up API keys
2. Copy PDFs to data folder
3. Run `streamlit run src/app.py`
4. Test with different product concepts
5. Record demo video (< 2 minutes)

Good luck! 🚀
