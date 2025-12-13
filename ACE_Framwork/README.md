# ACE Plant-Based Packaging Intelligence

**Agentic Context Engineering** - A multi-agent system for analyzing plant-based food products with explainable scores and actionable go-to-market recommendations.

---

## 🏗️ Multi-Agent System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           ACE PIPELINE ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                    │
│   │   INPUT      │     │   INPUT      │     │   INPUT      │                    │
│   │  Product     │     │   Image      │     │  Business    │                    │
│   │   Data       │     │  Analysis    │     │  Objective   │                    │
│   └──────┬───────┘     └──────┬───────┘     └──────┬───────┘                    │
│          │                    │                    │                             │
│          └────────────────────┼────────────────────┘                             │
│                               ▼                                                  │
│                    ┌──────────────────────┐                                      │
│                    │     📚 PLAYBOOK      │◄─────────────────────┐              │
│                    │  (Accumulated        │                      │              │
│                    │   Knowledge Base)    │                      │              │
│                    └──────────┬───────────┘                      │              │
│                               │                                  │              │
│                               ▼                                  │              │
│   ┌───────────────────────────────────────────────────────────────────────┐     │
│   │                      🤖 GENERATOR AGENT                               │     │
│   │  • Analyzes product data + image + playbook                          │     │
│   │  • Applies scoring rubric (Attractiveness, Utility, Positioning)     │     │
│   │  • Computes weighted global score based on objective                 │     │
│   │  • Generates evidence-based explanations                             │     │
│   │  • Produces packaging proposals & GTM recommendations                │     │
│   └───────────────────────────┬───────────────────────────────────────────┘     │
│                               │                                                  │
│                               ▼                                                  │
│   ┌───────────────────────────────────────────────────────────────────────┐     │
│   │                      🔍 REFLECTOR AGENT                               │     │
│   │  • Audits Generator's analysis quality                               │     │
│   │  • Identifies reasoning flaws & inconsistencies                      │     │
│   │  • Extracts generalizable insights                                   │     │
│   │  • Evaluates playbook bullet usage (helpful/misused/irrelevant)      │     │
│   └───────────────────────────┬───────────────────────────────────────────┘     │
│                               │                                                  │
│                               ▼                                                  │
│   ┌───────────────────────────────────────────────────────────────────────┐     │
│   │                      📝 CURATOR AGENT                                 │     │
│   │  • Decides if Reflector insights contain reusable knowledge          │     │
│   │  • Converts insights into generalizable playbook bullets             │     │
│   │  • Adds new rules to appropriate playbook sections                   │──────┘
│   │  • Ensures no duplicates or product-specific content                 │
│   └───────────────────────────┬───────────────────────────────────────────┘
│                               │
│                               ▼
│                    ┌──────────────────────┐
│                    │      📤 OUTPUT       │
│                    │  Complete Product    │
│                    │   Intelligence       │
│                    └──────────────────────┘
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📥 Input Structure

### 1. Product Data (from OpenFoodFacts or manual entry)

```json
{
  "product_id": "3760020507350",
  "name": "La Vie Jambon Végétal",
  "brand": "La Vie",
  "plant_based_category": "meat_alternatives",
  "ingredients_text": "Eau, farine de blé, huile de tournesol...",
  "ingredients_count": 15,
  "additives_count": 3,
  "nova_group": 4,
  "nutriscore": "a",
  "nutriments": {
    "proteins_100g": 16.0,
    "fiber_100g": 2.5,
    "salt_100g": 1.8,
    "sugars_100g": 0.5
  },
  "labels": ["vegan", "organic"],
  "packaging": {
    "materials": ["plastic", "cardboard"],
    "recyclable": true
  },
  "origin": "France",
  "countries": ["France", "Belgium"]
}
```

### 2. Image Analysis (from GPT Vision)

```json
{
  "image_description": "Modern packaging with green and pink colors, prominent 'VÉGÉTAL' claim...",
  "observations": [
    "Clear plant-based positioning with leaf iconography",
    "Premium shelf presence with matte finish"
  ],
  "problemes_detectes": [
    {
      "probleme": "Small ingredient list difficult to read",
      "indice_visuel": "Font size < 8pt on back panel",
      "gravite": "Mineur",
      "impact": "attractivité"
    }
  ]
}
```

### 3. Business Objective

| Objective | Scoring Weights | Focus |
|-----------|-----------------|-------|
| `reduce_upf_perception` | A:20% U:40% P:40% | Clean label, natural positioning |
| `launch_in_gms` | A:40% U:30% P:30% | Shelf appeal, mass market |
| `reposition_brand` | A:30% U:30% P:40% | Brand coherence, positioning |
| `increase_flexitarian_appeal` | A:45% U:35% P:20% | Attractiveness for plant-curious |

---

## 📤 Output Structure

### Complete Product Intelligence Export

```json
{
  "export_metadata": {
    "export_date": "2025-12-13T15:30:00",
    "export_type": "ACE Plant-Based Product Intelligence - Complete Report",
    "version": "1.0.0"
  },
  
  "business_objective": {
    "objective_key": "increase_flexitarian_appeal",
    "objective_description": "Increase Flexitarian Appeal - Focus on attractiveness for plant-curious consumers",
    "scoring_weights": {
      "attractiveness": 0.45,
      "utility": 0.35,
      "positioning": 0.20
    }
  },
  
  "product_information": {
    "basic_info": { "name": "...", "brand": "...", "category": "..." },
    "ingredients": { "text": "...", "count": 15, "additives": 3 },
    "nutrition": { "nova_group": 4, "nutriscore": "a", "nutriments": {...} },
    "labels_certifications": ["vegan", "organic"],
    "packaging": { "materials": [...], "recyclable": true }
  },
  
  "scoring_results": {
    "confidence_level": "high",
    "scores": {
      "attractiveness_score": 75.0,
      "utility_score": 62.5,
      "positioning_score": 83.3,
      "global_score": 72.4
    },
    "criteria_breakdown": {
      "attractiveness": {
        "readability": "yes",
        "visual_simplicity": "simple",
        "naturalness_cues": "clear",
        "familiarity": "familiar"
      },
      "utility": {
        "benefit_clarity": "clear",
        "usage_clarity": "partially clear",
        "ingredients_promise_coherence": "partially coherent",
        "message_focus": "focused"
      },
      "positioning": {
        "positioning_clarity": "clear",
        "tone_consistency": "consistent",
        "greenwashing_risk": "low"
      }
    }
  },
  
  "evidence_based_explanations": {
    "attractiveness": ["Modern design with clear hierarchy visible on front panel", "..."],
    "utility": ["High protein (16g/100g) prominently displayed", "..."],
    "positioning": ["Consistent plant-based messaging across all panels", "..."],
    "global": ["Strong overall score driven by clear positioning and premium aesthetics"]
  },
  
  "swot_analysis": {
    "strengths": ["High protein content", "Strong brand recognition", "Clean design"],
    "weaknesses": ["NOVA 4 classification", "3 additives present"],
    "risks": ["Ultra-processed perception in health-conscious markets"]
  },
  
  "packaging_improvement_proposals": [
    "Add natural ingredient imagery to reduce ultra-processed perception",
    "Increase font size for ingredient list (min 10pt)"
  ],
  
  "go_to_market_strategy": {
    "shelf_positioning": "Premium plant-based section, eye-level placement",
    "b2b_targeting": "Flexitarian-friendly restaurant chains and corporate catering",
    "regional_relevance": "Strong fit for urban European markets, expand to UK"
  }
}
```

---

## 🧠 Scoring Rubric (0-100 Scale)

### A) Attractiveness Score

| Criterion | Values | Points |
|-----------|--------|--------|
| `readability` | "yes" / "partially" / "no" | 1 / 0.5 / 0 |
| `visual_simplicity` | "simple" / "moderate" / "overloaded" | 1 / 0.5 / 0 |
| `naturalness_cues` | "clear" / "weak" / "none" | 1 / 0.5 / 0 |
| `familiarity` | "familiar" / "somewhat familiar" / "unfamiliar" | 1 / 0.5 / 0 |

**Formula:** `Attractiveness_score = average(4 criteria) × 100`

### B) Utility Score

| Criterion | Values | Points |
|-----------|--------|--------|
| `benefit_clarity` | "clear" / "partially clear" / "unclear" | 1 / 0.5 / 0 |
| `usage_clarity` | "clear" / "partially clear" / "unclear" | 1 / 0.5 / 0 |
| `ingredients_promise_coherence` | "coherent" / "partially coherent" / "not coherent" | 1 / 0.5 / 0 |
| `message_focus` | "focused" / "somewhat scattered" / "scattered" | 1 / 0.5 / 0 |

**Formula:** `Utility_score = average(4 criteria) × 100`

### C) Positioning Score

| Criterion | Values | Points |
|-----------|--------|--------|
| `positioning_clarity` | "clear" / "somewhat clear" / "unclear" | 1 / 0.5 / 0 |
| `tone_consistency` | "consistent" / "partially consistent" / "inconsistent" | 1 / 0.5 / 0 |
| `greenwashing_risk` | "low" / "moderate" / "high" | 1 / 0.5 / 0 |

**Formula:** `Positioning_score = average(3 criteria) × 100`

### Score Modifiers (from Product Data)

| Factor | Modifier |
|--------|----------|
| NOVA 1-2 | +5 to utility |
| NOVA 4 | -10 to utility |
| 0 additives | +5 to positioning |
| 4+ additives | -5 to positioning |
| Protein >15g/100g | +5 to utility |
| Fiber >5g/100g | +3 to utility |
| Each trusted label | +2 to positioning (max +10) |
| Recyclable packaging | +5 to positioning |

---

## 📚 Playbook Structure (Evolving Knowledge Base)

```json
{
  "scoring_rules": [
    "Products with NOVA 4 + >15 additives should cap utility at 45/100",
    "Meat alternatives require protein >15g for positioning >70"
  ],
  "plant_based_heuristics": [
    "Meat alternatives: protein >12g/100g is a strength",
    "Plant milks: sugar <5g is good, >8g is a concern"
  ],
  "ultra_processing_pitfalls": [
    "Long ingredient lists (>15) trigger ultra-processed perception",
    "E-numbers visible on front panel reduce trust"
  ],
  "packaging_patterns": [
    "Non-recyclable plastic reduces attractiveness by 10-20 points",
    "Green color without eco-certification triggers greenwashing risk"
  ],
  "go_to_market_rules": [
    "B2B targeting requires emphasizing consistency over taste",
    "GMS launch needs strong shelf differentiation"
  ]
}
```

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY="your-key"

# Launch Streamlit UI
streamlit run app.py

# CLI usage
python cli.py analyze --barcode 3760020507350 --objective "increase_flexitarian_appeal"

# API server
python api.py
```

---

## 📁 Project Structure

```
htf_ace/
├── app.py              # Streamlit web interface
├── agents.py           # Multi-agent system (Generator, Reflector, Curator)
├── llm_client.py       # LLM client abstraction (OpenAI, Anthropic, Google)
├── product_data.py     # OpenFoodFacts client & image analysis
├── playbook.py         # Playbook management & evolution
├── config.py           # Configuration & constants
├── prompts.py          # Legacy prompt templates
├── cli.py              # Command-line interface
├── api.py              # REST API
├── playbook.json       # Evolving knowledge base
└── requirements.txt    # Dependencies
```

---

## 🎯 Features

- **Normalized Product Data**: Extracts critical fields from OpenFoodFacts for plant-based analysis
- **GPT Vision Image Analysis**: Analyzes packaging with expert-level observations
- **Business Objective Weighting**: Objectives influence scores and recommendations
- **Evolving Playbook**: System learns and improves through accumulated knowledge
- **Complete JSON Export**: Export all intelligence (scores, strategies, SWOT) for integration
- **Clean User Output**: Internal processes (agents, playbook) are never exposed to end users