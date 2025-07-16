#\!/bin/bash

echo "🚀 Starting ULTRATHINK Hybrid System (Option B Implementation)..."
echo "🔧 Using proven original ultrathink logic with enhancements"
echo "✅ Multi-role analysis  < /dev/null |  Higher token limits | No aggressive filtering"
echo ""

# Activate virtual environment if available
if [ -f "../ultrathink/venv/bin/activate" ]; then
    echo "🔧 Activating original ultrathink virtual environment..."
    source ../ultrathink/venv/bin/activate
    echo "✅ Using proven working environment"
else
    echo "🔧 Using current environment"
fi

echo "🎯 Loading environment variables from .env file..."
# Load environment variables properly for the shell, fixing problematic lines
export $(cat .env | grep -v '^#' | grep -v '^$' | grep -v 'FROM_EMAIL' | sed 's/REDDIT_USER_AGENT=ULTRATHINK\/1.0 by dollarvora/REDDIT_USER_AGENT="ULTRATHINK\/1.0 by dollarvora"/' | xargs)
# Set the FROM_EMAIL separately with proper quoting
export FROM_EMAIL="ULTRATHINK <dollar3191@gmail.com>"

# Verify key environment variables are loaded
echo "✅ OpenAI API Key: $(echo $OPENAI_API_KEY | cut -c1-20)..."
echo "✅ Google API Key: $(echo $GOOGLE_API_KEY | cut -c1-20)..."
echo "✅ Reddit Client ID: $REDDIT_CLIENT_ID"

echo "✅ Environment loaded - Running ULTRATHINK Hybrid System..."
python3 run_hybrid_system.py

echo ""
echo "✅ System completed! Check output folder for results."
