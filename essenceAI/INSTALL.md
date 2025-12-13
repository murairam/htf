# 📦 Installation Guide

## Quick Install (2 minutes)

### Step 1: Install Dependencies

```bash
cd essenceAI
pip install -r requirements.txt
```

Or use pip3:
```bash
python3 -m pip install -r requirements.txt
```

### Step 2: Verify Installation

```bash
python3 test_agent_setup.py
```

**Expected Output:**
```
🎉 All tests passed! Agent system is ready to use.
Total: 5/5 tests passed
```

---

## 🔧 Detailed Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Install All Dependencies

```bash
# Navigate to project directory
cd essenceAI

# Install all required packages
pip install -r requirements.txt
```

### What Gets Installed

The `requirements.txt` includes:

**Core Dependencies:**
- `streamlit>=1.31.0` - Web UI framework
- `llama-index>=0.10.0` - RAG engine
- `pandas>=2.0.0` - Data manipulation
- `plotly>=5.18.0` - Visualizations
- `python-dotenv>=1.0.0` - Environment variables

**LLM Providers:**
- `llama-index-llms-openai>=0.1.0` - OpenAI integration
- `llama-index-llms-anthropic>=0.1.0` - Anthropic integration
- `openai>=1.12.0` - OpenAI API
- `anthropic>=0.18.0` - Anthropic API

**Data Sources:**
- `requests>=2.31.0` - HTTP requests
- `tavily-python>=0.3.0` - Web search API

**Testing:**
- `pytest>=7.4.0` - Test framework
- `pytest-mock>=3.11.0` - Mocking
- `pytest-cov>=4.1.0` - Coverage
- `pytest-asyncio>=0.21.0` - Async testing

---

## ✅ Verify Installation

### Method 1: Quick Verification

```bash
python3 test_agent_setup.py
```

### Method 2: Check Imports

```bash
python3 -c "from agents import MarketingAgent; print('✓ Agents installed successfully')"
```

### Method 3: Run Tests

```bash
pytest tests/test_agents.py::TestMarketingAgent -v
```

---

## 🐛 Troubleshooting

### Issue: "No module named 'llama_index'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "No module named 'agents'"

**Solution:** Make sure you're in the essenceAI directory
```bash
cd essenceAI
python3 test_agent_setup.py
```

### Issue: Permission denied

**Solution:** Use user installation
```bash
pip install --user -r requirements.txt
```

### Issue: Old package versions

**Solution:** Upgrade packages
```bash
pip install --upgrade -r requirements.txt
```

---

## 🔑 Optional: API Keys Setup

For full functionality (Competitor and Research agents), set up API keys:

### Create .env file

```bash
cd essenceAI
cat > .env << 'EOF'
# Required for Competitor and Research agents
OPENAI_API_KEY=sk-your-openai-key-here

# Optional: Better competitor data
TAVILY_API_KEY=tvly-your-tavily-key-here

# Optional: Use Anthropic instead of OpenAI
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# LLM Provider (openai or anthropic)
LLM_PROVIDER=openai
EOF
```

### Get API Keys

**OpenAI:**
1. Go to https://platform.openai.com/api-keys
2. Create new API key
3. Add to `.env` file

**Tavily (Optional):**
1. Go to https://tavily.com
2. Sign up (free tier: 1000 requests/month)
3. Get API key
4. Add to `.env` file

---

## 🎯 Installation Verification Checklist

- [ ] Python 3.9+ installed
- [ ] pip installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Test passes (`python3 test_agent_setup.py`)
- [ ] Agents import successfully
- [ ] (Optional) API keys configured in `.env`

---

## 🚀 Quick Start After Installation

### 1. Test the System

```bash
python3 test_agent_setup.py
```

### 2. Try Marketing Agent (No API Key)

```bash
python3 test_marketing.py
```

### 3. Run Examples

```bash
python3 examples/agent_usage_examples.py
```

### 4. Run Full Test Suite

```bash
./run_all_tests.sh
```

---

## 📦 Virtual Environment (Recommended)

### Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify
python3 test_agent_setup.py
```

### Deactivate

```bash
deactivate
```

---

## 🔄 Update Installation

To update to latest versions:

```bash
pip install --upgrade -r requirements.txt
```

---

## 📊 Installation Size

Approximate disk space required:
- Dependencies: ~500 MB
- Project files: ~5 MB
- **Total: ~505 MB**

---

## 🎓 Next Steps After Installation

1. ✅ Verify installation: `python3 test_agent_setup.py`
2. ✅ Read quick start: `AGENTS_QUICKSTART.md`
3. ✅ Try examples: `python3 examples/agent_usage_examples.py`
4. ✅ Read documentation: `AGENTS_README.md`
5. ✅ (Optional) Add API keys to `.env`

---

## 🆘 Need Help?

- **Installation issues:** Check troubleshooting section above
- **Testing issues:** See `HOW_TO_TEST.md`
- **Usage questions:** See `AGENTS_QUICKSTART.md`
- **Full documentation:** See `AGENTS_README.md`

---

## ✨ Success!

If `python3 test_agent_setup.py` shows:
```
🎉 All tests passed! Agent system is ready to use.
```

**You're all set! The agent system is ready to use.** 🚀

---

**Installation complete!** Check `AGENTS_QUICKSTART.md` to start using the agents.
