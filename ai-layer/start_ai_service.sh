#!/bin/bash

# TruChain AI Service Startup Script
# This script activates the virtual environment and starts the AI service

echo "=================================================="
echo "TruChain AI Verification Service"
echo "=================================================="
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  WARNING: .env file not found"
    echo ""
    echo "Please create a .env file with your OpenAI API key:"
    echo "  echo 'OPENAI_API_KEY=sk-your-key-here' > .env"
    echo ""
    echo "Or you can copy from the example:"
    echo "  cp .env.example .env"
    echo ""
    read -p "Press Enter to continue anyway or Ctrl+C to exit..."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if activation was successful
if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    echo "Please run: python3.10 -m venv venv"
    exit 1
fi

echo "✅ Virtual environment activated"
echo ""

# Start the AI service
echo "Starting AI service on http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================="
echo ""

python api_server.py
