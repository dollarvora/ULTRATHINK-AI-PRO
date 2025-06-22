#!/bin/bash
# ULTRATHINK Daily Scheduler
# Run this script to set up daily automated emails

echo "🚀 Setting up ULTRATHINK Daily Schedule"
echo "========================================"

# Create the cron job script
cat > /Users/Dollar/Documents/ultrathink-enhanced/daily_run.sh << 'EOF'
#!/bin/bash
# Daily ULTRATHINK execution script

# Set environment
export PYTHONPATH="/Users/Dollar/Documents/ultrathink-enhanced"
cd /Users/Dollar/Documents/ultrathink-enhanced

# Run with logging
python run_live_data.py >> output/logs/daily_$(date +%Y%m%d).log 2>&1

# Optional: Clean old logs (keep last 30 days)
find output/logs -name "daily_*.log" -mtime +30 -delete
EOF

# Make executable
chmod +x /Users/Dollar/Documents/ultrathink-enhanced/daily_run.sh

echo "✅ Daily script created: daily_run.sh"
echo ""
echo "To schedule daily runs at 9 AM, add this to your crontab:"
echo "(Run: crontab -e)"
echo ""
echo "0 9 * * * /Users/Dollar/Documents/ultrathink-enhanced/daily_run.sh"
echo ""
echo "Or run manually anytime with:"
echo "./daily_run.sh"