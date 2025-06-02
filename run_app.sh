#!/bin/bash

# AI Voice News Scraper - Run Script
echo "🔊 AI Voice News Scraper"
echo "========================"

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
else
    echo "⚠️  No virtual environment detected. Consider activating one:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate  # On macOS/Linux"
    echo "   venv\\Scripts\\activate     # On Windows"
    echo ""
fi

# Check if .env file exists
if [ -f ".env" ]; then
    echo "✅ .env file found"
else
    echo "❌ .env file not found!"
    echo "   Please create a .env file with your API keys"
    echo "   Copy .env.example to .env and fill in your credentials"
    exit 1
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip install -r requirements.txt --quiet

# Run the application
echo "🚀 Starting AI Voice News Scraper..."
python main_fixed.py "$@"
