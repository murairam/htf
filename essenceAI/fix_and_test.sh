#!/bin/bash
# Quick setup and test script for the rate limit fix

set -e

echo "=============================================="
echo "essenceAI - Rate Limit Fix Setup & Test"
echo "=============================================="
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the essenceAI directory"
    exit 1
fi

# Check for API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set in environment"
    
    if [ -f ".env" ]; then
        echo "✓ Found .env file, loading..."
        export $(cat .env | grep -v '^#' | xargs)
    else
        echo ""
        echo "Please set your OpenAI API key:"
        echo "  export OPENAI_API_KEY='your-key-here'"
        echo ""
        echo "Or create a .env file:"
        echo "  cp .env.example .env"
        echo "  # Edit .env and add your key"
        exit 1
    fi
fi

echo "✓ API key found"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt
pip install -q llama-index-embeddings-openai
echo "✓ Dependencies installed"
echo ""

# Show PDF status
echo "📄 Research PDFs in data directory:"
ls -lh data/*.pdf 2>/dev/null | awk '{print "   " $9 " (" $5 ")"}'
echo ""

PDF_COUNT=$(ls -1 data/*.pdf 2>/dev/null | wc -l)
echo "   Total: $PDF_COUNT PDFs"
echo ""

if [ $PDF_COUNT -gt 6 ]; then
    echo "⚠️  Warning: You have $PDF_COUNT PDFs. Consider moving non-research PDFs to data/hackathon_docs/"
    echo ""
fi

# Clean old cache
if [ -d ".storage" ] || [ -d ".cache" ]; then
    echo "🗑️  Cleaning old cache..."
    rm -rf .storage .cache
    echo "✓ Cache cleared"
    echo ""
fi

# Run test
echo "🧪 Running test..."
echo ""
python test_rag_fix.py

echo ""
echo "=============================================="
echo "✅ Setup complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "  1. If test passed, you're ready to use the app"
echo "  2. Run: streamlit run src/app.py"
echo "  3. Click 'Initialize Research Database' in sidebar"
echo ""
echo "For more details, see RATE_LIMIT_FIX.md"
