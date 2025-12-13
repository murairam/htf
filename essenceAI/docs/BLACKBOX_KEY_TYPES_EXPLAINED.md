# Blackbox AI API Key Types - Complete Explanation

## 🔑 Two Different Key Types Discovered

After extensive testing and documentation review, Blackbox AI has **TWO different API key types**:

### 1. **`bb_` Keys** (What You Have)
**Format:** `bb_89eba5664e1b...`

**Where to Get:**
- https://app.blackbox.ai/dashboard
- Free tier and paid accounts

**What It Works For:**
- ✅ **Repository Task API** (`https://cloud.blackbox.ai/api/tasks`)
  - Create tasks on GitHub repositories
  - Multi-agent execution
  - PR creation
- ✅ **GitHub APIs** (`https://cloud.blackbox.ai/api/github/*`)
  - Get organizations
  - Get repositories
  - Get branches
  - Get issues
- ✅ **Web Interface** (https://www.blackbox.ai)

**What It DOESN'T Work For:**
- ❌ **Chat Completion API** (`https://api.blackbox.ai/chat/completions`)
- ❌ **Image Generation API**
- ❌ **Video Generation API**
- ❌ **Standalone code generation** (without repository)

### 2. **`sk-` Keys** (LiteLLM Virtual Keys)
**Format:** `sk-...`

**Where to Get:**
- Requires **paid subscription** (Pro Plus or higher)
- https://app.blackbox.ai/dashboard (after upgrading)

**What It Works For:**
- ✅ **Everything `bb_` keys work for** PLUS:
- ✅ **Chat Completion API**
- ✅ **Image Generation API**
- ✅ **Video Generation API**
- ✅ **Standalone code generation**
- ✅ **Access to multiple AI models** (GPT-4, Claude, Gemini, etc.)

## 📊 API Endpoint Breakdown

### Endpoints That Work with `bb_` Keys:

```bash
# Repository Tasks
POST https://cloud.blackbox.ai/api/tasks
GET https://cloud.blackbox.ai/api/tasks/{taskId}

# GitHub Integration
GET https://cloud.blackbox.ai/api/github/orgs
GET https://cloud.blackbox.ai/api/github/repos
GET https://cloud.blackbox.ai/api/github/all-repos
GET https://cloud.blackbox.ai/api/github/branches
GET https://cloud.blackbox.ai/api/github/issues
```

### Endpoints That Require `sk-` Keys:

```bash
# Chat Completions
POST https://api.blackbox.ai/chat/completions

# Image Generation
POST https://api.blackbox.ai/image/generations

# Video Generation
POST https://api.blackbox.ai/video/generations
```

## 🎯 What This Means for Your Project

### Option 1: Use Repository-Based Workflow (Works Now!)

**With your current `bb_` key, you can:**

1. **Create a RepositoryAgent** that uses repository tasks
2. **Automate GitHub workflows**
3. **Create PRs automatically**
4. **Run multi-agent tasks on codebases**

**Example:**
```python
# This WILL work with your bb_ key!
import requests

url = "https://cloud.blackbox.ai/api/tasks"
headers = {
    "Authorization": f"Bearer {your_bb_key}",
    "Content-Type": "application/json"
}

payload = {
    "prompt": "Add error handling to the API",
    "repoUrl": "https://github.com/your-org/your-repo.git",
    "selectedBranch": "main",
    "selectedAgent": "blackbox",
    "selectedModel": "blackboxai/blackbox-pro"
}

response = requests.post(url, headers=headers, json=payload)
# This should work!
```

### Option 2: Upgrade for Chat Completions

**If you want standalone code generation:**
- Upgrade to paid plan
- Get `sk-` key
- Use chat completion API

### Option 3: Use OpenAI (Recommended for Now)

**For CodeAgent & QualityAgent:**
- Use OpenAI (you already have the key)
- Keep `bb_` key for future RepositoryAgent
- Best of both worlds!

## 💡 Recommended Architecture

### Hybrid Approach (Best Solution):

```
Your essenceAI System:
├── CompetitorAgent → Uses Tavily + OpenAI ✅ (Working)
├── CodeAgent → Uses OpenAI ✅ (Switch from Blackbox)
├── QualityAgent → Uses OpenAI ✅ (Switch from Blackbox)
└── RepositoryAgent → Uses Blackbox bb_ key ✅ (Add later)
    ├── GitHub integration
    ├── Automated PRs
    └── Multi-agent execution
```

**Benefits:**
1. ✅ All agents working immediately
2. ✅ No additional subscriptions needed
3. ✅ Can add RepositoryAgent later with your `bb_` key
4. ✅ Flexible and cost-effective

## 🚀 Next Steps

### Immediate (15 minutes):
**Switch CodeAgent & QualityAgent to OpenAI**
- Modify `blackbox_client.py` to use OpenAI
- Test all functionality
- Result: All 3 agents working

### Future Enhancement (When you want):
**Add RepositoryAgent with your `bb_` key**
- Create new agent for GitHub tasks
- Use Blackbox repository task API
- Automate PR creation
- Result: 4 agents with specialized purposes

## 📝 Summary

**Your `bb_` Key:**
- ✅ Valid and working
- ✅ Good for repository tasks
- ❌ Not for chat completions

**To Get `sk-` Key:**
- Need paid subscription
- Check https://www.blackbox.ai/pricing
- Upgrade at https://app.blackbox.ai/dashboard

**My Recommendation:**
- Use OpenAI for CodeAgent & QualityAgent (now)
- Keep `bb_` key for RepositoryAgent (later)
- Upgrade to `sk-` key only if you need multi-model access

## ❓ Decision Time

**What would you like to do?**

1. **Switch to OpenAI** → All agents working in 15 min
2. **Add RepositoryAgent** → Use your `bb_` key for GitHub tasks
3. **Upgrade Blackbox** → Get `sk-` key for chat completions
4. **Combination** → OpenAI now + RepositoryAgent later

Let me know!
