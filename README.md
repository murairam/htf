# 🌱 Plant-Based Packaging Intelligence

**AI-powered marketing & packaging analysis for plant-based food innovation**

---

## 🧠 Problem

Plant-based food companies face a high failure rate when launching new products:
- packaging does not clearly communicate value or utility,
- consumers distrust ultra-processed or "greenwashed" products,
- pricing is often misaligned with perceived benefits,
- go-to-market decisions (shelf placement, B2B targeting) rely on costly and slow market studies.

Early-stage startups and food innovators lack **fast, affordable, and science-informed tools** to evaluate how their products will be perceived **before** going to market.

---

## 💡 Solution Overview

**Plant-Based Packaging Intelligence** is an AI-driven system that analyzes plant-based food products using:
- product identification data (barcode),
- business objectives provided by the company.

The system produces **interpretable scores** and a **strategic marketing analysis** tailored specifically to the plant-based food ecosystem.

---

## 🏗️ Architecture

### Technology Stack

**Frontend:**
- React 18 with Vite
- Tailwind CSS for styling
- QuaggaJS for barcode scanning
- WebSocket for real-time updates

**Backend:**
- Django 5.0 (Python web framework)
- Django Channels (WebSocket support)
- Redis (WebSocket channel layer)
- Daphne (ASGI server)

**LLM Service:**
- FastAPI (separate service on port 8001)
- OpenAI GPT-4 integration
- OpenFoodFacts API integration
- ACE Framework for structured analysis

### System Flow

1. User submits product barcode and business objectives
2. Django creates analysis record and returns analysis_id
3. Frontend opens WebSocket connection
4. Django consumer calls FastAPI `/run-analysis` endpoint with:
   - analysis_id
   - barcode
   - objectives
5. FastAPI service:
   - Looks up product from OpenFoodFacts
   - Extracts `image_front_url` from product data
   - Runs LLM analysis with GPT-4
   - Returns complete JSON with scores, recommendations, and image URL
6. Django relays final result via WebSocket
7. Frontend displays results with conditional image rendering

---

## 🔌 Inputs

The solution takes **two required inputs**:

### 1️⃣ Product Barcode (Required)
- EAN / UPC barcode
- Camera scanning with QuaggaJS
- Manual fallback input
- Used to retrieve product data from OpenFoodFacts
- Product image automatically fetched via `image_front_url`

### 2️⃣ Business Objectives (Required)
A natural language prompt defined by the company, for example:
- *"Improve shelf attractiveness in retail"*
- *"Reduce perception of ultra-processed food"*
- *"Adapt packaging for B2B foodservice buyers"*

**Note**: No image upload required - product images are automatically retrieved from OpenFoodFacts database.

---

## 📊 Outputs

### 🎯 Product Scores (0-100)

| Score | Description |
|------|------------|
| **Attractiveness Score** | Visual and emotional appeal of the packaging |
| **Price Score** | Coherence between price, product promise, and market expectations |
| **Utility Score** | Perceived usefulness (nutrition, usage, clarity of benefits) |
| **Global Score** | Weighted synthesis aligned with the company's objective |

### 🧭 Strategic Analysis

- **SWOT Analysis**: Strengths, weaknesses, opportunities, threats
- **Packaging Improvements**: Specific recommendations with priority levels
- **Go-to-Market Strategy**: Shelf positioning, regional relevance, B2B targeting

### 🖼️ Product Image

- Automatically retrieved from OpenFoodFacts via `image_front_url`
- Displayed only if available in the database
- No manual upload required

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Redis (for production WebSocket)
- OpenAI API key

### 1. Clone the Repository

```bash
git clone <repository-url>
cd htf
```

### 2. Backend Setup (Django)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 3. Frontend Setup (React)

```bash
cd frontend
npm install
cd ..
```

### 4. FastAPI Service Setup

```bash
cd ACE_Framwork

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set OpenAI API key
export OPENAI_API_KEY='your-openai-api-key-here'
```

### 5. Redis Setup (Production)

**Ubuntu/Debian:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

---

## 🎮 Running the Application

### Development Mode

**Terminal 1 - FastAPI Service:**
```bash
./run_fastapi.sh
```

**Terminal 2 - Django + React:**
```bash
./run_dev.sh
```

Access the application:
- **Frontend**: http://localhost:5173
- **Django Backend**: http://localhost:8000
- **FastAPI Service**: http://localhost:8001

### Production Mode

**Terminal 1 - FastAPI Service:**
```bash
./run_fastapi.sh
```

**Terminal 2 - Django (with built React):**
```bash
./run_prod.sh
```

Access the application:
- **Application**: http://localhost:8000
- **FastAPI Service**: http://localhost:8001

---

## 📁 Project Structure

```
htf/
├── config/                      # Django project settings
│   ├── settings.py             # Main settings
│   ├── urls.py                 # URL routing
│   ├── asgi.py                 # ASGI configuration
│   └── wsgi.py                 # WSGI configuration
│
├── marketing_analyzer/          # Main Django app
│   ├── models.py               # Analysis data model (no image field)
│   ├── views.py                # HTTP views (submit, results)
│   ├── consumers.py            # WebSocket consumer
│   ├── routing.py              # WebSocket routing
│   ├── fastapi_client.py       # FastAPI integration
│   ├── urls.py                 # App URL patterns
│   ├── templates/              # Django templates
│   └── migrations/             # Database migrations
│
├── frontend/                    # React frontend (Vite)
│   ├── src/
│   │   ├── components/         # Reusable components
│   │   │   ├── BarcodeScanner.jsx
│   │   │   ├── ProgressBar.jsx
│   │   │   └── Accordion.jsx
│   │   ├── pages/              # Page components
│   │   │   ├── HomePage.jsx    # No image upload
│   │   │   └── ResultsPage.jsx # Conditional image display
│   │   ├── App.jsx             # Main app component
│   │   └── main.jsx            # Entry point
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── ACE_Framwork/               # FastAPI LLM service
│   ├── api.py                  # FastAPI endpoints
│   ├── requirements.txt
│   └── ...
│
├── run_dev.sh                  # Development launcher
├── run_prod.sh                 # Production launcher
├── run_fastapi.sh              # FastAPI service launcher
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🔧 Configuration

### Environment Variables

**Django (config/settings.py):**
- `DEBUG`: Set to `False` in production
- `SECRET_KEY`: Change in production
- `ALLOWED_HOSTS`: Add your domain in production
- `FASTAPI_URL`: FastAPI service URL (default: http://localhost:8001)
- `FASTAPI_TIMEOUT`: Request timeout in seconds (default: 60)

**FastAPI (ACE_Framwork):**
- `OPENAI_API_KEY`: Your OpenAI API key (required)

---

## 🧪 Testing

### Test Barcode Examples

- **3017620422003** - Nutella (Ferrero)
- **3017624010701** - Kinder Bueno
- **8076809513623** - Barilla Pasta
- **5449000000996** - Coca-Cola

### Manual Testing Flow

1. Start FastAPI service
2. Start Django + React
3. Open http://localhost:5173 (dev) or http://localhost:8000 (prod)
4. Scan or enter a barcode
5. Enter business objectives
6. Submit and watch real-time analysis
7. Review scores and recommendations
8. Product image displays automatically if available

---

## 📝 API Documentation

### Django Endpoints

**POST /submit/**
- Submit new analysis request
- Body: `multipart/form-data` with `barcode`, `objectives`
- Returns: `{ "analysis_id": "uuid", "redirect_url": "/results/uuid/" }`

**GET /results/<analysis_id>/**
- View analysis results page
- Returns: HTML page with React app

**WebSocket /ws/analysis/<analysis_id>/**
- Real-time analysis updates
- Messages:
  - Status: `{ "type": "status", "status": "processing", "progress": 60, "message": "..." }`
  - Result: `{ "type": "final_result", "payload": {...} }`
  - Error: `{ "type": "status", "status": "error", "message": "..." }`

### FastAPI Endpoints

**GET /**
- Health check
- Returns: `{ "status": "ok" }`

**POST /run-analysis**
- Run complete LLM analysis
- Body: `{ "analysis_id": "uuid", "barcode": "1234567890123", "objectives": "..." }`
- Returns: Complete JSON with:
  - `image_front_url`: Product image from OpenFoodFacts
  - `scoring_results`: Scores (attractiveness, price, utility, global)
  - `swot_analysis`: SWOT analysis
  - `packaging_improvement_proposals`: Recommendations
  - `go_to_market_strategy`: GTM strategy

---

## 🐛 Troubleshooting

### FastAPI Service Not Running
```bash
# Check if service is running
curl http://localhost:8001/

# Start the service
./run_fastapi.sh
```

### WebSocket Connection Failed
- Ensure Redis is running (production)
- Check Django Channels configuration
- Verify ASGI server (Daphne) is running

### No Product Image Displayed
- Normal behavior if product not in OpenFoodFacts
- Check browser console for image load errors
- Verify `image_front_url` in JSON response

---

## ⚠️ Disclaimer

This project is a **prototype**.  
Scores and analyses are based on AI-driven indicators and available data, and should be used as **decision-support tools**, not as definitive market predictions.

---

**Built with ❤️ for plant-based food innovation**
