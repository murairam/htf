# PlantMarket Advisor

**AI-Powered Packaging Analysis and Go-to-Market Strategy for Plant-Based Food Products**

PlantPack Intelligence is a multi-agent system that analyzes plant-based food products using structured data, packaging image analysis, and business objectives. It produces explainable scores across four dimensions and generates actionable go-to-market recommendations specifically tailored to the plant-based food ecosystem.
<img width="1192" height="687" alt="image" src="https://github.com/user-attachments/assets/b7dbea21-50d1-4726-a0b7-ca21735b58da" />

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Solution Overview](#solution-overview)
3. [System Architecture](#system-architecture)
4. [Multi-Agent Pipeline](#multi-agent-pipeline)
5. [Scoring Methodology](#scoring-methodology)
6. [Input Specification](#input-specification)
7. [Output Specification](#output-specification)
8. [Playbook System](#playbook-system)
9. [Technology Stack](#technology-stack)
10. [Installation](#installation)
11. [Usage](#usage)
12. [API Reference](#api-reference)
13. [Project Structure](#project-structure)
14. [Configuration](#configuration)
15. [Testing](#testing)
16. [Troubleshooting](#troubleshooting)
17. [Disclaimer](#disclaimer)

---

## Problem Statement

Plant-based food companies face significant challenges when launching new products:

- Packaging frequently fails to communicate value proposition or utility clearly
- Consumers increasingly distrust products perceived as ultra-processed or greenwashed
- Pricing strategies are often misaligned with perceived benefits and market expectations
- Go-to-market decisions (shelf placement, B2B targeting, regional expansion) rely on costly and slow market studies
- French and European regulations (AGEC, Triman, REACH) create compliance complexity

Early-stage startups and food innovators lack fast, affordable, and evidence-based tools to evaluate how their products will be perceived before market launch.

---

## Solution Overview

PlantPack Intelligence addresses these challenges through an AI-driven analysis system that combines:

- **Product Data Normalization**: Extracts and normalizes critical fields from OpenFoodFacts for plant-based analysis
- **Packaging Image Analysis**: Uses GPT Vision to analyze packaging design, claims, and visual communication
- **Multi-Dimensional Scoring**: Evaluates products across four weighted dimensions with detailed evidence
- **Evolving Knowledge Base**: Learns from each analysis through an evolving playbook system
- **Actionable Recommendations**: Generates specific packaging improvements and go-to-market strategies

The system produces interpretable scores and strategic marketing analysis specifically calibrated for the plant-based food ecosystem in France and Europe.

---

## System Architecture

### High-Level Architecture

```
+-----------------------------------------------------------------------------------+
|                              PLANTPACK INTELLIGENCE                                |
+-----------------------------------------------------------------------------------+
|                                                                                    |
|   FRONTEND (React + Vite)                                                         |
|   +------------------+  +------------------+  +------------------+                 |
|   | Barcode Scanner  |  | Objective Input  |  | Results Display  |                |
|   | (QuaggaJS)       |  | (Business Goals) |  | (Scores + SWOT)  |                |
|   +--------+---------+  +--------+---------+  +--------+---------+                |
|            |                     |                     ^                          |
|            +----------+----------+                     |                          |
|                       |                                |                          |
|                       v                                |                          |
|   BACKEND (Django + Channels)                          |                          |
|   +--------------------------------------------------+ |                          |
|   | WebSocket Handler | REST API | Redis Pub/Sub     | |                          |
|   +--------------------------------------------------+ |                          |
|                       |                                |                          |
|                       v                                |                          |
|   LLM SERVICE (FastAPI)                                |                          |
|   +--------------------------------------------------+ |                          |
|   | OpenFoodFacts    | GPT-4 Vision | ACE Pipeline   |-+                          |
|   | Data Retrieval   | Image Analysis| Multi-Agent   |                            |
|   +--------------------------------------------------+                            |
|                       |                                                           |
|                       v                                                           |
|   +--------------------------------------------------+                            |
|   |                 PLAYBOOK (JSON)                   |                           |
|   |  Evolving Knowledge Base for Plant-Based Analysis |                           |
|   +--------------------------------------------------+                            |
|                                                                                    |
+-----------------------------------------------------------------------------------+
```

### Data Flow

1. User submits product barcode and business objectives via frontend
2. Django backend creates analysis record and returns analysis_id
3. Frontend opens WebSocket connection for real-time updates
4. Django consumer calls FastAPI /run-analysis endpoint
5. FastAPI service retrieves product data from OpenFoodFacts, normalizes fields, retrieves product image, runs GPT Vision analysis, executes ACE pipeline, and returns complete analysis
6. Django relays results via WebSocket
7. Frontend displays scores, SWOT analysis, and recommendations

---

## Multi-Agent Pipeline

PlantPack Intelligence uses an Agentic Context Engineering (ACE) architecture with three specialized agents.

### Pipeline Architecture

```
+-----------------------------------------------------------------------------------+
|                              ACE PIPELINE                                          |
+-----------------------------------------------------------------------------------+
|                                                                                    |
|   INPUTS                                                                          |
|   +----------------+     +----------------+     +----------------+                 |
|   | Product Data   |     | Image Analysis |     | Business       |                |
|   | (Normalized)   |     | (GPT Vision)   |     | Objective      |                |
|   +-------+--------+     +-------+--------+     +-------+--------+                |
|           |                      |                      |                         |
|           +----------------------+----------------------+                         |
|                                  |                                                |
|                                  v                                                |
|                    +----------------------------+                                 |
|                    |      PLAYBOOK              |<------------------+             |
|                    | (Accumulated Knowledge)    |                   |             |
|                    +-------------+--------------+                   |             |
|                                  |                                  |             |
|                                  v                                  |             |
|   +----------------------------------------------------------------------+        |
|   |                      GENERATOR AGENT                                 |        |
|   |  - Analyzes product data, image, and playbook knowledge             |        |
|   |  - Applies 4-dimension scoring with evidence                         |        |
|   |  - Generates SWOT analysis and GTM recommendations                   |        |
|   +----------------------------------------------------------------------+        |
|                                  |                                                |
|                                  v                                                |
|   +----------------------------------------------------------------------+        |
|   |                      REFLECTOR AGENT                                 |        |
|   |  - Audits Generator analysis quality                                 |        |
|   |  - Identifies reasoning flaws and inconsistencies                    |        |
|   |  - Extracts generalizable insights                                   |        |
|   +----------------------------------------------------------------------+        |
|                                  |                                                |
|                                  v                                                |
|   +----------------------------------------------------------------------+        |
|   |                      CURATOR AGENT                                   |        |
|   |  - Converts insights into playbook bullets                           |--------+
|   |  - Adds new rules to appropriate sections                            |
|   |  - Only agent that modifies playbook                                 |
|   +----------------------------------------------------------------------+
|                                  |
|                                  v
|                    +----------------------------+
|                    |          OUTPUT            |
|                    | Complete Intelligence      |
|                    +----------------------------+
+-----------------------------------------------------------------------------------+
```
![WhatsApp Image 2025-12-14 at 15 56 38](https://github.com/user-attachments/assets/3acffe4b-15a5-48c2-b885-74ad1b02a1da)


### Agent Responsibilities

**Generator Agent**: Primary analysis agent that produces scores, SWOT analysis, and recommendations. Reads playbook but does not modify it.

**Reflector Agent**: Quality assurance agent that audits Generator output, identifies flaws, and extracts learnable insights. Does not modify playbook.

**Curator Agent**: Knowledge management agent that converts Reflector insights into playbook bullets. Only agent authorized to modify playbook.

---

## Scoring Methodology

### Fixed Weighting Model

```
TOTAL_SCORE = (ENVIRONMENTAL_IMPACT x 0.40) + 
              (PRODUCTION_QUALITY x 0.30) + 
              (CONSUMER_EXPERIENCE x 0.20) + 
              (PLANT_BASED_SPECIFICITY x 0.10)
```

### Dimension 1: Environmental Impact (40%)

Evaluates the ecological footprint of the packaging.

| Sub-dimension | Description |
|---------------|-------------|
| Recyclability and End-of-Life | Capacity to be recycled in France (infrastructure, mono-material, sorting instructions) |
| Material Sourcing and Origin | Sustainability of materials (recycled content, FSC/PEFC, bio-sourced, traceability) |
| Weight and Volume Reduction | Material optimization (weight, empty space, decorative elements) |
| Reuse and Circular Economy | Reuse potential (deposit system, refillable design, bulk options) |

### Dimension 2: Production Quality (30%)

Evaluates the technical performance of the packaging.

| Sub-dimension | Description |
|---------------|-------------|
| Product Protection and Barriers | Barriers against oxidation, moisture, light, shocks; shelf life impact |
| Manufacturing Compatibility | Inks, adhesives, additives compatible with recycling (NIR, separability) |
| Functional Design | Ergonomics (opening, portioning, resealing, microwave/fridge compatibility) |

### Dimension 3: Consumer Experience (20%)

Evaluates attractiveness and practicality.

| Sub-dimension | Description |
|---------------|-------------|
| Aesthetic and Brand Appeal | Visual attractiveness, plant-based value coherence, greenwashing absence |
| Practical Utility and Convenience | Daily use (portability, formats, refills, innovations) |
| Information and Education | Sorting/recycling clarity, QR codes, date legibility, anti-littering |

### Dimension 4: Plant-Based Specificity (10%)

Evaluates adaptation to plant-based products and regulatory compliance.

| Sub-dimension | Description |
|---------------|-------------|
| Regulatory Compliance | AGEC/REACH compliance (Triman, claims, prohibited substances) - ELIMINATORY |
| Plant-Based Product Adaptation | Adaptation to plant-based constraints (oxidation, concentrated formats) |
| Supply Chain Optimization | Logistics (stackability, right-sizing, B2B reusability) |

**Default Score**: 50.0 if data unavailable

**Eliminatory Rule**: Regulatory violation sets total_score to 0

---

## Input Specification

### Product Data Structure

```json
{
  "product_id": "3760020507350",
  "name": "La Vie Jambon Vegetal",
  "brand": "La Vie",
  "plant_based_category": "meat_alternatives",
  "ingredients_text": "Eau, farine de ble, huile de tournesol...",
  "ingredients_count": 15,
  "additives_count": 3,
  "nova_group": 4,
  "nutriscore": "A",
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
  "countries": ["France", "Belgium"],
  "image_front_url": "https://images.openfoodfacts.org/..."
}
```

### Image Analysis Structure

```json
{
  "image_description": "Modern packaging with green and pink colors, prominent VEGETAL claim...",
  "observations": [
    "Clear plant-based positioning with leaf iconography",
    "Premium shelf presence with matte finish"
  ],
  "problemes_detectes": [
    {
      "probleme": "Small ingredient list difficult to read",
      "indice_visuel": "Font size below 8pt",
      "gravite": "Mineur",
      "impact": "consumer_experience"
    }
  ]
}
```

### Business Objective

Natural language description of the company's primary goal:
- "Improve shelf attractiveness in retail"
- "Reduce perception of ultra-processed food"
- "Justify premium pricing positioning"
- "Adapt packaging for B2B foodservice buyers"

---

## Output Specification

### Complete Analysis Report

```json
{
  "export_metadata": {
    "export_date": "2025-12-13T15:30:00",
    "export_type": "PlantPack Intelligence - Complete Report",
    "version": "1.0.0"
  },
  
  "business_objective": {
    "objective_key": "increase_flexitarian_appeal",
    "objective_description": "Increase Flexitarian Appeal",
    "scoring_weights": {
      "environmental_impact": 0.40,
      "production_quality": 0.30,
      "consumer_experience": 0.20,
      "plant_based_specificity": 0.10
    }
  },
  
  "scoring_results": {
    "confidence_level": "high",
    "used_bullet_ids": ["sr-00001", "pbh-00002"],
    "compliance": {
      "regulatory_compliance": "pass",
      "issues": []
    },
    "scores": {
      "environmental_impact_score": 65.0,
      "production_quality_score": 70.0,
      "consumer_experience_score": 75.0,
      "plant_based_specificity_score": 80.0,
      "total_score": 69.5
    },
    "score_breakdown": {
      "environmental_impact": {
        "recyclability": {
          "score": 70.0,
          "evidence": ["Detailed explanation of recyclability assessment..."]
        }
      }
    }
  },
  
  "swot_analysis": {
    "strengths": ["Recyclable materials", "AGEC compliant", "Clear positioning"],
    "weaknesses": ["No FSC certification", "No circular economy features"],
    "risks": ["Evolving regulations", "Rising sustainability expectations"]
  },
  
  "packaging_improvement_proposals": [
    "Obtain FSC certification for cardboard components",
    "Incorporate 30% recycled PET in tray"
  ],
  
  "go_to_market_strategy": {
    "shelf_positioning": "Premium plant-based section at eye level",
    "b2b_targeting": "Flexitarian-friendly restaurant chains",
    "regional_relevance": "Strong fit for urban French markets"
  }
}
```

---

## Playbook System

The playbook is an evolving knowledge base that accumulates learnings from each analysis.

### Playbook Sections

| Section | Purpose |
|---------|---------|
| scoring_rules | Quantitative rules for calculating dimension scores |
| plant_based_heuristics | Category-specific decision guidelines |
| ultra_processing_pitfalls | Common mistakes related to NOVA, additives, clean label |
| packaging_patterns | Material choices, certifications, greenwashing detection |
| go_to_market_rules | Market positioning, channel selection, pricing |

### Example Bullets

```json
{
  "scoring_rules": [
    "Products with NOVA 4 + >15 additives should cap production_quality at 45/100",
    "Non-recyclable packaging reduces environmental_impact by 15-20 points"
  ],
  "plant_based_heuristics": [
    "Meat alternatives require protein >15g/100g for consumer_experience >70"
  ],
  "packaging_patterns": [
    "Missing Triman symbol = regulatory_compliance fail"
  ]
}
```

---

## Technology Stack

### Frontend
- React 18 with Vite
- Tailwind CSS
- QuaggaJS (barcode scanning)
- WebSocket (real-time updates)

### Backend
- Django 5.0
- Django Channels (WebSocket)
- Redis (channel layer)
- Daphne (ASGI server)

### LLM Service
- FastAPI
- OpenAI GPT-4 / GPT-4 Vision
- OpenFoodFacts API

---

## Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- Redis (production)
- OpenAI API key

### Backend Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

### Frontend Setup

```bash
cd frontend
npm install
```

### LLM Service Setup

```bash
cd ACE_Framework
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY='your-key'
```

---

## Usage

### Development Mode

Terminal 1:
```bash
./run_fastapi.sh
```

Terminal 2:
```bash
./run_dev.sh
```

Access: http://localhost:5173 (frontend), http://localhost:8001 (API)

### Command Line

```bash
python cli.py analyze --barcode 3760020507350 --objective "increase_flexitarian_appeal"
python cli.py playbook stats
```

### Streamlit Interface

```bash
cd ACE_Framework
streamlit run app.py
```

---

## API Reference

### POST /submit/
Submit analysis request. Returns analysis_id.

### WebSocket /ws/analysis/<id>/
Real-time progress updates and final results.

### POST /run-analysis
Execute complete LLM analysis pipeline.

### GET /playbook/stats
Retrieve playbook statistics.

---

## Project Structure

```
plantpack-intelligence/
|-- config/                     # Django settings
|-- marketing_analyzer/         # Django application
|-- frontend/                   # React frontend
|-- ACE_Framework/              # FastAPI LLM service
|   |-- agents.py               # Multi-agent pipeline
|   |-- api.py                  # FastAPI endpoints
|   |-- playbook.py             # Playbook management
|   |-- product_data.py         # OpenFoodFacts client
|   +-- playbook.json           # Knowledge base
|-- run_dev.sh
|-- run_prod.sh
+-- run_fastapi.sh
```

---

## Configuration

### Environment Variables

Django:
- DEBUG, SECRET_KEY, ALLOWED_HOSTS
- FASTAPI_URL (default: http://localhost:8001)
- FASTAPI_TIMEOUT (default: 60)

FastAPI:
- OPENAI_API_KEY (required)

---

## Testing

### Test Barcodes

| Barcode | Product |
|---------|---------|
| 3760020507350 | La Vie Jambon Vegetal |
| 3274080005003 | Cristaline Water |
| 3017620422003 | Nutella |

---

## Troubleshooting

**FastAPI not running**: Check with `curl http://localhost:8001/`

**WebSocket failed**: Verify Redis is running

**Context length exceeded**: Playbook is automatically truncated

**No product image**: Normal if product not in OpenFoodFacts

---

## Disclaimer

PlantMarket Advisor is a prototype decision-support tool. Scores and analyses are AI-driven indicators and should be used as inputs to business decisions, not as definitive predictions.

Regulatory compliance assessments are indicative only and do not constitute legal advice.

---

**PlantMarket Advisor- Accelerating plant-based food innovation through AI-powered packaging analysis**
