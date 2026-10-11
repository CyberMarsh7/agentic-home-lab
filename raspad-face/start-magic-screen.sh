#!/bin/bash

# Magic Screen Startup Script
# Starts the voice avatar interface and orchestrator

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🎤 Starting Pee-wee's Magic Screen..."
echo "=" * 60

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install it first."
    exit 1
fi

echo "📦 Checking dependencies..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install/upgrade requirements
echo "Installing requirements..."
pip install -q -r requirements.txt

# Start orchestrator
echo ""
echo "🚀 Starting Orchestrator Service..."
echo "   Flask running on http://0.0.0.0:5000"
echo ""
echo "📍 Avatar interface:"
echo "   http://localhost:5000/interface/voice-avatar.html"
echo ""
echo "Press Ctrl+C to stop"
echo "=" * 60
echo ""

python orchestrator.py
