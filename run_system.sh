#!/bin/bash

echo "🚀 Starting ULTRATHINK Enhanced System..."

# Navigate to the correct directory
cd /Users/Dollar/Documents/ultrathink-enhanced

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements if they haven't been installed
echo "📥 Installing/updating requirements..."
pip install -r requirements_minimal.txt

# Run the system
echo "🎯 Running ULTRATHINK Enhanced System..."
python create_real_system.py

echo "✅ System completed! Check output folder for results."