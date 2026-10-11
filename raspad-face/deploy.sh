#!/bin/bash

# Deployment script for Magic Screen on RasPad
# Run this on the physical Raspberry Pi to set up everything

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "╔════════════════════════════════════════════════════════╗"
echo "║   🎤 PEE-WEE'S MAGIC SCREEN - DEPLOYMENT              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "⚠️  WARNING: Not running on a Raspberry Pi"
    echo "   This script is designed for RasPad hardware"
    echo "   Continuing anyway..."
    echo ""
fi

echo "📍 Checking prerequisites..."
echo ""

# Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install it first:"
    echo "   sudo apt update && sudo apt install -y python3 python3-pip python3-venv"
    exit 1
fi
echo "✅ Python 3: $(python3 --version)"

# pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found. Install it first:"
    echo "   sudo apt install -y python3-pip"
    exit 1
fi
echo "✅ pip3: $(pip3 --version)"

# Git
if ! command -v git &> /dev/null; then
    echo "⚠️  Git not found. Installing..."
    sudo apt update && sudo apt install -y git
fi
echo "✅ Git: $(git --version)"

echo ""
echo "📦 Setting up Python virtual environment..."

# Create venv
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Created new virtual environment"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Activate venv
source venv/bin/activate

echo ""
echo "📦 Installing Python dependencies..."
pip install -q -r requirements.txt
echo "✅ Dependencies installed"

echo ""
echo "📝 Configuration Summary:"
echo "  • Avatar Interface: http://<raspad-ip>:5000"
echo "  • Split Screen: http://<raspad-ip>:5000/split (with Home Assistant)"
echo "  • Agent Routing: Pyramid Gateway (local + Tailscale fallback)"
echo "  • Push-to-Talk: Spacebar (keyboard) or M5Stack device"
echo "  • Web Speech API: Browser microphone + speaker"
echo ""

echo "🎤 M5STACK DEVICE SETUP (Optional)"
echo "──────────────────────────────────"
echo ""
echo "You can use M5Stack devices for:"
echo "  • Physical push-to-talk button"
echo "  • Status display (showing avatar state, device status)"
echo "  • Voice feedback speaker"
echo ""
echo "See M5STACK-SETUP.md for integration details."
echo ""

echo "🚀 Starting Magic Screen..."
echo "   Press Ctrl+C to stop"
echo ""
echo "════════════════════════════════════════════════════════"
echo ""

# Run orchestrator
python orchestrator.py
