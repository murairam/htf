# How to Get Blackbox AI API Key

## 🔑 Getting the Correct API Key

You need an **`sk-` prefixed API key** (LiteLLM Virtual Key) for programmatic API access.

### Step-by-Step Guide:

#### 1. **Visit Blackbox AI Dashboard**
Go to: https://app.blackbox.ai/dashboard

#### 2. **Check Your Current Plan**
- Look for your subscription tier
- Free tier gives `bb_` keys (web interface only)
- Paid plans give `sk-` keys (API access)

#### 3. **Upgrade to Paid Plan (if needed)**

**Option A: Check Pricing Page**
- Visit: https://www.blackbox.ai/pricing
- Look for plans that include "API Access"
- Common tiers:
  - **Pro**: Basic API access
  - **Pro Plus**: Full API access + advanced features
  - **Enterprise**: Custom solutions

**Option B: Contact Support**
- If pricing isn't clear, contact Blackbox AI support
- Ask specifically about "API access" and "LiteLLM Virtual Keys"
- Email: support@blackbox.ai (check their website for current contact)

#### 4. **Generate API Key**
After upgrading:
1. Go to https://app.blackbox.ai/dashboard
2. Look for "API Keys" section
3. Click "Generate New Key" or "Create API Key"
4. Copy the key (should start with `sk-`)
5. Store it securely

#### 5. **Update Your .env File**
```bash
# Replace your current key
BLACKBOX_API_KEY=sk_your_new_api_key_here
```

## 🆓 Alternative: Free Options

If you don't want to pay for Blackbox AI, here are free alternatives:

### Option 1: Use OpenAI (You Already Have This!)
- ✅ You already have OpenAI API key
- ✅ GPT-4 is excellent for code tasks
- ✅ No additional cost
- ✅ I can modify the agents to use OpenAI in 15 minutes

### Option 2: Use Other Free AI APIs

**Groq (Fast & Free):**
- Website: https://groq.com
- Free tier: 30 requests/minute
- Models: Llama 3, Mixtral, etc.
- Great for code tasks

**Google Gemini (Free Tier):**
- Website: https://ai.google.dev
- Free tier: 60 requests/minute
- Models: Gemini 1.5 Pro, Flash
- Good for code generation

**Together AI:**
- Website: https://together.ai
- Free tier available
- Multiple open-source models
- Code-focused models available

**Anthropic Claude (Paid but excellent):**
- Website: https://anthropic.com
- Claude 3.5 Sonnet is excellent for code
- Similar pricing to OpenAI

## 💰 Cost Comparison

### Blackbox AI (Estimated):
- **Free**: `bb_` key, web interface only
- **Pro**: ~$20-30/month (check current pricing)
- **Pro Plus**: ~$50+/month (full API access)

### OpenAI (Current):
- **GPT-4o-mini**: $0.15 / 1M input tokens (~$0.60 / 1M output)
- **GPT-4o**: $2.50 / 1M input tokens (~$10 / 1M output)
- **Pay-as-you-go**: Only pay for what you use

### Groq (Free):
- **Free tier**: 30 requests/minute
- **Paid**: $0.05-0.10 / 1M tokens
- **Very fast**: 500+ tokens/second

## 🎯 My Recommendation

**Use OpenAI for now:**

**Why:**
1. ✅ You already have it
2. ✅ No additional cost
3. ✅ Excellent for code tasks
4. ✅ All agents working in 15 minutes
5. ✅ Can switch to Blackbox AI later if needed

**Later, when you want:**
- Upgrade to Blackbox AI for multi-model access
- Add RepositoryAgent for GitHub integration
- Use Blackbox for specialized tasks

## 📝 What to Do Right Now

**Immediate Action:**
1. Tell me: "Switch to OpenAI"
2. I'll modify the code in 15 minutes
3. All 3 agents will be working
4. You can upgrade to Blackbox AI anytime later

**Or:**
1. Visit https://www.blackbox.ai/pricing
2. Upgrade to a paid plan
3. Get your `sk-` API key
4. Update `.env` file
5. Test again - everything will work!

## ❓ Questions?

**Q: Can I use my `bb_` key for anything?**
A: Only for the web interface at https://www.blackbox.ai. Not for programmatic API access.

**Q: How much does Blackbox AI cost?**
A: Check https://www.blackbox.ai/pricing for current pricing. Usually $20-50/month for API access.

**Q: Is OpenAI better than Blackbox AI?**
A: They're different:
- **OpenAI**: Direct access to GPT models, pay-as-you-go
- **Blackbox AI**: Access to multiple models (GPT, Claude, Gemini) through one API, monthly subscription

**Q: Can I switch later?**
A: Yes! The code is designed to be flexible. You can switch between providers anytime.

## 🚀 Ready to Proceed?

Just let me know:
- **"Switch to OpenAI"** - I'll modify the code now
- **"I'll upgrade Blackbox"** - I'll wait for your new `sk-` key
- **"Keep as-is"** - I'll complete with CompetitorAgent only

Your choice!
