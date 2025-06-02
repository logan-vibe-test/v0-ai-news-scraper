#!/bin/bash
# Simple run script for AI Voice News Scraper

echo "🔊 AI Voice News Scraper"
echo "======================="

# Check for .env file
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "📝 Copy .env.example to .env and add your API keys"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run the application
echo "🚀 Starting scraper..."
python main_fixed.py
