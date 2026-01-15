#!/bin/bash
# OpenSati Installation Script for macOS/Linux
# https://github.com/OpenSati-com/OpenSati

set -e

echo ""
echo "🧘 OpenSati Installer"
echo "====================="
echo ""

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "❌ Python not found. Please install Python 3.10+"
    exit 1
fi

VERSION=$($PYTHON -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
MAJOR=$($PYTHON -c 'import sys; print(sys.version_info.major)')
MINOR=$($PYTHON -c 'import sys; print(sys.version_info.minor)')

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 10 ]); then
    echo "❌ Python 3.10+ required. Found: $VERSION"
    exit 1
fi

echo "✅ Python $VERSION detected"

# Check if in virtualenv
if [ -z "$VIRTUAL_ENV" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment created"
else
    echo "✅ Using existing virtual environment"
fi

# Install dependencies
echo "📦 Installing OpenSati..."
pip install --upgrade pip
pip install -e .

# Check for audio support
echo ""
read -p "Install audio support for breathing detection? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Installing audio dependencies..."
    pip install -e ".[audio]"
fi

# Check for Ollama
echo ""
echo "🤖 Checking for Ollama..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama detected"
    
    read -p "Download AI models? (llama3 + llava, ~8GB) (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📥 Downloading llama3..."
        ollama pull llama3
        echo "📥 Downloading llava..."
        ollama pull llava
        echo "✅ AI models ready"
    fi
else
    echo "⚠️  Ollama not found. AI features will be disabled."
    echo "   Install from: https://ollama.ai/"
fi

# Create default config if needed
if [ ! -f config.yaml ]; then
    echo "📝 Creating default config..."
    cp config.yaml.example config.yaml 2>/dev/null || true
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "To run OpenSati:"
echo "  source venv/bin/activate"
echo "  opensati"
echo ""
echo "Or simply:"
echo "  make run"
echo ""
