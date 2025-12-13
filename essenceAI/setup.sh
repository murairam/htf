#!/bin/bash

# essenceAI Setup Script
# Run this to set up the project quickly

echo "🌱 Setting up essenceAI..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Create virtual environment (optional but recommended)
read -p "Create virtual environment? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✓ Virtual environment created and activated"
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
# essenceAI API Keys

# Required: OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Tavily API Key (free tier: 1000 requests/month)
# Sign up at https://tavily.com
TAVILY_API_KEY=your_tavily_api_key_here

# LLM Provider: "openai" or "anthropic"
LLM_PROVIDER=openai
EOF
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your API keys!"
else
    echo ""
    echo "✓ .env file already exists"
fi

# Create data directory
mkdir -p data
echo "✓ Data directory created"

# Check for PDFs
pdf_count=$(ls -1 data/*.pdf 2>/dev/null | wc -l)
if [ $pdf_count -eq 0 ]; then
    echo ""
    echo "⚠️  No PDFs found in data/ directory"
    echo "📄 Copy research PDFs to data/ folder:"
    echo "   cp ../hackthefork/*.pdf data/"
else
    echo "✓ Found $pdf_count PDF(s) in data/ directory"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your OpenAI API key"
echo "2. (Optional) Sign up for Tavily API at https://tavily.com"
echo "3. Copy PDFs to data/ folder if not done already"
echo "4. Run: streamlit run src/app.py"
echo ""
echo "🚀 Happy hacking!"
