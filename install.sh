#!/bin/bash
# KaliNova Installer

echo "🚀 Installing KaliNova..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Make main script executable
chmod +x kalinova.py

echo "✅ Installation complete!"
echo "💡 Run: source venv/bin/activate && ./kalinova.py --help"