#!/bin/bash
# Setup script for SP-404 MK2 Toolkit

echo "🎛️ SP-404 MK2 Toolkit Setup"
echo "=========================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if command -v pip3 &> /dev/null; then
    # Try regular install first
    if pip3 install -r requirements.txt 2>/dev/null; then
        echo "✅ Dependencies installed successfully"
    else
        # If that fails, try with --break-system-packages (for some environments)
        echo "⚠️  Standard install failed, trying with --break-system-packages..."
        if pip3 install -r requirements.txt --break-system-packages; then
            echo "✅ Dependencies installed with --break-system-packages"
        else
            echo "❌ Failed to install dependencies. You may need to:"
            echo "   1. Create a virtual environment: python3 -m venv venv && source venv/bin/activate"
            echo "   2. Or install system packages: apt install python3-flask python3-werkzeug"
            echo "   3. Or run: pip3 install -r requirements.txt --break-system-packages"
        fi
    fi
elif command -v pip &> /dev/null; then
    pip install -r requirements.txt
else
    echo "❌ pip not found. Please install pip and run: pip install -r requirements.txt"
    exit 1
fi

# Make scripts executable
echo "🔧 Setting up executable permissions..."
chmod +x sp404_toolkit.py
chmod +x pattern_editor.py
chmod +x web_interface.py
chmod +x bin/hex_diff.sh
chmod +x firmware/*.sh

# Create uploads directory for web interface
mkdir -p uploads

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Quick Start:"
echo "  CLI Tool:       ./sp404_toolkit.py --help"
echo "  Pattern Editor: ./pattern_editor.py pattern/PTN00001-01.BIN --summary"
echo "  Web Interface:  ./web_interface.py"
echo ""
echo "📖 Examples:"
echo "  # Get pad info"
echo "  ./sp404_toolkit.py padconf info padconf/PADCONF001.BIN --pad 1"
echo ""
echo "  # Set pad BPM"
echo "  ./sp404_toolkit.py padconf set-bpm padconf/PADCONF001.BIN --pad 1 --bpm 120.0"
echo ""
echo "  # Analyze pattern"
echo "  ./pattern_editor.py pattern/PTN00001-01.BIN --timeline"
echo ""
echo "  # Start web interface"
echo "  ./web_interface.py"
echo ""