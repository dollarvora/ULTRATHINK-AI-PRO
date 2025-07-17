#!/bin/bash

echo "🚀 Starting ULTRATHINK Enhanced System..."

# Stay in current directory (ULTRATHINK-AI-PRO)
# cd /Users/Dollar/Documents/ultrathink-enhanced

# Use the working virtual environment from ultrathink
echo "🔧 Using working virtual environment from ultrathink..."
WORKING_VENV="/Users/Dollar/Documents/ultrathink/venv"

if [ ! -d "$WORKING_VENV" ]; then
    echo "❌ Working venv not found at $WORKING_VENV"
    exit 1
fi

source "$WORKING_VENV/bin/activate"
echo "✅ Using proven working environment with correct OpenAI version"

# Run the system
echo "🎯 Running ULTRATHINK Enhanced System..."
python create_real_system.py

echo "✅ System completed! Check output folder for results."