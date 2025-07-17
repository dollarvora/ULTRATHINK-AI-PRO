# 🔧 ULTRATHINK-AI-PRO Troubleshooting Guide

## Table of Contents
- [Quick Diagnostics](#quick-diagnostics)
- [Common Issues](#common-issues)
- [API-Related Problems](#api-related-problems)
- [Performance Issues](#performance-issues)
- [Configuration Problems](#configuration-problems)
- [Data Quality Issues](#data-quality-issues)
- [System Administration](#system-administration)
- [Debug Tools](#debug-tools)
- [Getting Help](#getting-help)

## Quick Diagnostics

### Health Check Command

```bash
# Run comprehensive health check
python -c "
from utils.health_checker import HealthChecker
health = HealthChecker()
result = health.check_all()
print('System Status:', '✅ HEALTHY' if result['healthy'] else '❌ ISSUES')
for issue in result.get('issues', []):
    print(f'  - {issue}')
"
```

### Test System Components

```bash
# Test basic functionality
python test_production_system.py

# Run full test suite
python run_tests.py --quiet

# Test specific component
python run_tests.py --component gpt_summarizer
```

### Check System Status

```bash
# Check Python environment
python --version
pip list | grep -E "(openai|praw|requests)"

# Check environment variables
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

required_vars = ['OPENAI_API_KEY', 'REDDIT_CLIENT_ID', 'GOOGLE_API_KEY']
missing = [var for var in required_vars if not os.getenv(var)]
if missing:
    print(f'❌ Missing env vars: {missing}')
else:
    print('✅ All required environment variables set')
"
```

## Common Issues

### 1. "ModuleNotFoundError" Errors

**Symptoms:**
```
ModuleNotFoundError: No module named 'openai'
ModuleNotFoundError: No module named 'praw'
```

**Diagnosis:**
```bash
# Check if virtual environment is activated
which python
pip list
```

**Solutions:**
```bash
# Activate virtual environment
source ultrathink_env/bin/activate  # Linux/macOS
# ultrathink_env\Scripts\activate   # Windows

# Install missing dependencies
pip install -r requirements_minimal.txt

# Upgrade existing packages
pip install --upgrade openai praw requests
```

### 2. "Invalid API Key" Errors

**Symptoms:**
```
openai.error.AuthenticationError: Invalid API key provided
praw.exceptions.ResponseException: CLIENT_ID_DOES_NOT_EXIST
```

**Diagnosis:**
```bash
# Check environment variables
echo $OPENAI_API_KEY
echo $REDDIT_CLIENT_ID

# Verify .env file
cat .env | grep -E "(OPENAI|REDDIT|GOOGLE)"
```

**Solutions:**
```bash
# Update .env file with correct credentials
nano .env

# Test API connectivity
python -c "
import openai
import os
openai.api_key = os.getenv('OPENAI_API_KEY')
try:
    models = openai.Model.list()
    print('✅ OpenAI API working')
except Exception as e:
    print(f'❌ OpenAI API error: {e}')
"
```

### 3. "Rate Limit Exceeded" Errors

**Symptoms:**
```
openai.error.RateLimitError: Rate limit reached
HTTP 429 errors in logs
```

**Diagnosis:**
```bash
# Check API usage frequency
grep -i "rate limit" logs/*.log | tail -10
```

**Solutions:**
```python
# Reduce request frequency in config/config.py
CONFIG = {
    "sources": {
        "reddit": {
            "post_limit": 25,  # Reduce from 50
            "comment_limit": 10  # Reduce from 20
        },
        "google": {
            "results_per_query": 5,  # Reduce from 10
        }
    },
    "summarization": {
        "max_tokens": 500,  # Reduce from 800
    }
}
```

### 4. "No Content Found" Issues

**Symptoms:**
```
No insights generated
Empty HTML reports
No vendor mentions detected
```

**Diagnosis:**
```bash
# Check if sources are accessible
python -c "
from fetchers.reddit_fetcher import RedditFetcher
from config.config import CONFIG

fetcher = RedditFetcher()
content = fetcher.fetch_content(CONFIG)
print(f'Reddit content items: {len(content)}')

for item in content[:3]:
    print(f'  - {item.get(\"title\", \"No title\")}')
"
```

**Solutions:**
```python
# Adjust source configuration
CONFIG = {
    "sources": {
        "reddit": {
            "subreddits": [
                "sysadmin", "msp", "cybersecurity", 
                "vmware", "aws", "azure"  # Add more specific subreddits
            ],
            "post_limit": 50,  # Increase limit
        }
    }
}
```

### 5. HTML Generation Failures

**Symptoms:**
```
HTML file not created
Broken HTML output
Missing CSS styling
```

**Diagnosis:**
```bash
# Test HTML generation
python -c "
from html_generator import EnhancedHTMLGenerator
generator = EnhancedHTMLGenerator(debug=True)

sample_insights = ['Test insight for troubleshooting']
sample_content = [{'title': 'Test', 'content': 'Test', 'source': 'test'}]
sample_vendor_analysis = {'top_vendors': [], 'total_vendors': 0, 'vendor_mentions': {}}

html = generator.generate_html_report(
    insights=sample_insights,
    all_content=sample_content,
    vendor_analysis=sample_vendor_analysis,
    config={'system': {'name': 'Test'}}
)

print(f'HTML length: {len(html)} characters')
print('Contains viewport tag:', 'viewport' in html)
"
```

## API-Related Problems

### OpenAI API Issues

#### Problem: GPT Response Parsing Errors
```python
# Debug GPT responses
import json
from summarizer.gpt_summarizer import GPTSummarizer

def debug_gpt_response():
    summarizer = GPTSummarizer(debug=True)
    
    # Check recent debug files
    import os
    debug_files = [f for f in os.listdir('output') if f.startswith('gpt_input_content_')]
    if debug_files:
        latest = sorted(debug_files)[-1]
        print(f"Latest GPT input file: output/{latest}")
        
    # Check raw responses
    raw_files = [f for f in os.listdir('output') if f.startswith('raw_openai_response_')]
    if raw_files:
        latest = sorted(raw_files)[-1]
        print(f"Latest GPT response file: output/{latest}")

debug_gpt_response()
```

#### Problem: Token Limit Exceeded
```python
# Adjust token limits
CONFIG = {
    "summarization": {
        "model": "gpt-4o-mini",
        "max_tokens": 500,  # Reduce from 800
        "temperature": 0.3
    }
}
```

### Reddit API Issues

#### Problem: Subreddit Access Denied
```python
# Test subreddit accessibility
import praw
import os

reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent=os.getenv('REDDIT_USER_AGENT')
)

subreddits_to_test = ['sysadmin', 'msp', 'cybersecurity']
for sub_name in subreddits_to_test:
    try:
        subreddit = reddit.subreddit(sub_name)
        posts = list(subreddit.hot(limit=1))
        print(f"✅ {sub_name}: accessible ({len(posts)} posts)")
    except Exception as e:
        print(f"❌ {sub_name}: {e}")
```

#### Problem: No Recent Posts
```python
# Adjust time window for posts
from datetime import datetime, timedelta

# In reddit_fetcher.py, extend time window
time_threshold = datetime.now() - timedelta(days=7)  # Increase from 1 day
```

### Google API Issues

#### Problem: Custom Search Not Working
```bash
# Test Google Custom Search
python -c "
import requests
import os

api_key = os.getenv('GOOGLE_API_KEY')
cse_id = os.getenv('GOOGLE_CSE_ID')

url = f'https://www.googleapis.com/customsearch/v1'
params = {
    'key': api_key,
    'cx': cse_id,
    'q': 'microsoft pricing',
    'num': 1
}

try:
    response = requests.get(url, params=params)
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'Results: {len(data.get(\"items\", []))}')
    else:
        print(f'Error: {response.text}')
except Exception as e:
    print(f'Error: {e}')
"
```

## Performance Issues

### Slow Execution

#### Diagnosis
```bash
# Profile system performance
python -c "
from utils.performance_monitor import PerformanceMonitor
import time

monitor = PerformanceMonitor('performance_test', debug=True)
start = time.time()

# Simulate operations
operation = monitor.start_operation('test_operation')
time.sleep(1)  # Simulate work
monitor.complete_operation(operation, success=True)

end = time.time()
print(f'Total time: {end - start:.2f}s')

# Print performance report
monitor.print_performance_report()
"
```

#### Solutions
```python
# Optimize configuration for speed
CONFIG = {
    "sources": {
        "reddit": {
            "post_limit": 25,        # Reduce data volume
            "comment_limit": 5       # Reduce processing
        },
        "google": {
            "results_per_query": 5   # Fewer results
        }
    },
    "summarization": {
        "max_tokens": 400           # Faster GPT processing
    }
}
```

### Memory Issues

#### Diagnosis
```bash
# Monitor memory usage
python -c "
import psutil
import os

process = psutil.Process(os.getpid())
memory_info = process.memory_info()
print(f'Memory usage: {memory_info.rss / 1024 / 1024:.1f} MB')

# Check system memory
print(f'System memory: {psutil.virtual_memory().percent}% used')
"
```

#### Solutions
```python
# Reduce memory usage
def process_content_in_batches(content, batch_size=10):
    """Process content in smaller batches"""
    for i in range(0, len(content), batch_size):
        batch = content[i:i+batch_size]
        yield batch

# Use in your code
for batch in process_content_in_batches(large_content_list):
    process_batch(batch)
```

## Configuration Problems

### Environment Variable Issues

#### Missing .env File
```bash
# Create .env from template
cp .env.example .env

# Set proper permissions
chmod 600 .env

# Edit with your credentials
nano .env
```

#### Incorrect Configuration Format
```python
# Validate configuration
from config.config import CONFIG
import json

def validate_config():
    """Validate configuration structure"""
    required_sections = ['system', 'credentials', 'sources', 'summarization']
    
    for section in required_sections:
        if section not in CONFIG:
            print(f"❌ Missing config section: {section}")
        else:
            print(f"✅ Found config section: {section}")
    
    # Check credentials
    creds = CONFIG.get('credentials', {})
    for service in ['openai', 'reddit', 'google']:
        if service in creds:
            print(f"✅ {service} credentials configured")
        else:
            print(f"❌ {service} credentials missing")

validate_config()
```

### Keywords Configuration

#### Problem: No Vendor Detection
```python
# Check vendor aliases
from utils.company_alias_matcher import get_company_matcher

matcher = get_company_matcher(debug=True)
print(f"Total companies: {len(matcher.company_mappings)}")
print(f"Total aliases: {sum(len(aliases) for aliases in matcher.company_mappings.values())}")

# Test specific vendor
test_text = "Microsoft Azure pricing update"
result = matcher.find_companies_in_text(test_text)
print(f"Detected: {result.matched_companies}")
```

## Data Quality Issues

### Low-Quality Insights

#### Diagnosis
```python
# Analyze insight quality
def analyze_insights(insights):
    """Analyze quality of generated insights"""
    quality_metrics = {
        'total': len(insights),
        'with_vendors': 0,
        'with_numbers': 0,
        'with_urgency': 0,
        'generic': 0
    }
    
    for insight in insights:
        # Check for vendor mentions
        if any(vendor.lower() in insight.lower() 
               for vendor in ['microsoft', 'vmware', 'cisco', 'dell']):
            quality_metrics['with_vendors'] += 1
        
        # Check for quantified data
        if any(char in insight for char in ['$', '%', '€', '£']):
            quality_metrics['with_numbers'] += 1
        
        # Check for urgency indicators
        if any(word in insight.lower() 
               for word in ['urgent', 'critical', 'immediate', 'breaking']):
            quality_metrics['with_urgency'] += 1
        
        # Check for generic content
        if any(phrase in insight.lower() 
               for phrase in ['general', 'various', 'multiple']):
            quality_metrics['generic'] += 1
    
    return quality_metrics

# Example usage
sample_insights = ["Sample insight for testing"]
metrics = analyze_insights(sample_insights)
print(f"Quality metrics: {metrics}")
```

#### Solutions
```python
# Improve GPT prompts for better quality
# In gpt_summarizer.py, enhance prompt engineering:

def _build_enhanced_prompt(self, roles, content):
    """Enhanced prompt for better insight quality"""
    prompt_additions = [
        "CRITICAL: Only extract insights with specific financial data or vendor names",
        "PRIORITY: Focus on quantified information ($ amounts, % changes, dates)",
        "REJECT: Generic statements without specific vendor or pricing details"
    ]
    
    # Add to existing prompt...
```

### Duplicate Content

#### Problem: Same insights repeated
```python
# Implement deduplication
def deduplicate_insights(insights):
    """Remove duplicate insights"""
    seen = set()
    unique_insights = []
    
    for insight in insights:
        # Normalize insight for comparison
        normalized = insight.lower().strip()
        normalized = re.sub(r'[🔴🟡🟢]', '', normalized)  # Remove priority indicators
        
        if normalized not in seen:
            seen.add(normalized)
            unique_insights.append(insight)
        else:
            print(f"Duplicate removed: {insight[:50]}...")
    
    return unique_insights
```

## System Administration

### Log Management

#### Log Rotation Setup
```bash
# Create logrotate configuration
sudo tee /etc/logrotate.d/ultrathink << EOF
/opt/ultrathink-ai-pro/logs/*.log {
    daily
    rotate 30
    compress
    missingok
    notifempty
    create 0644 ultrathink ultrathink
    postrotate
        # Optional: restart service
        # systemctl reload ultrathink-service
    endscript
}
EOF
```

#### Log Analysis
```bash
# Common log analysis commands
tail -f logs/system.log                    # Follow live logs
grep -i error logs/*.log | tail -20       # Find recent errors
grep -i "rate limit" logs/*.log           # Find rate limiting
grep -i timeout logs/*.log                # Find timeouts

# Analyze performance
grep "execution time" logs/*.log | awk '{print $NF}' | sort -n
```

### Automated Monitoring

#### Health Check Script
```bash
#!/bin/bash
# health_monitor.sh

LOG_FILE="/var/log/ultrathink_health.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] Starting health check" >> $LOG_FILE

# Check if service is running
if pgrep -f "ultrathink" > /dev/null; then
    echo "[$TIMESTAMP] ✅ Service running" >> $LOG_FILE
else
    echo "[$TIMESTAMP] ❌ Service not running" >> $LOG_FILE
    # Restart service or send alert
fi

# Check disk space
DISK_USAGE=$(df -h /opt/ultrathink-ai-pro | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "[$TIMESTAMP] ⚠️ Disk usage high: ${DISK_USAGE}%" >> $LOG_FILE
fi

# Check recent errors
ERROR_COUNT=$(grep -c "ERROR" /opt/ultrathink-ai-pro/logs/system.log | tail -100)
if [ $ERROR_COUNT -gt 5 ]; then
    echo "[$TIMESTAMP] ⚠️ High error count: $ERROR_COUNT" >> $LOG_FILE
fi

echo "[$TIMESTAMP] Health check complete" >> $LOG_FILE
```

### Backup and Recovery

#### Backup Script
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/ultrathink-$(date +%Y%m%d_%H%M%S)"
SOURCE_DIR="/opt/ultrathink-ai-pro"

mkdir -p "$BACKUP_DIR"

# Backup configuration
cp -r "$SOURCE_DIR/config" "$BACKUP_DIR/"

# Backup recent outputs
find "$SOURCE_DIR/output" -name "*.html" -mtime -7 -exec cp {} "$BACKUP_DIR/" \;

# Backup logs (last 3 days)
find "$SOURCE_DIR/logs" -name "*.log" -mtime -3 -exec cp {} "$BACKUP_DIR/" \;

# Create archive
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

echo "Backup created: $BACKUP_DIR.tar.gz"
```

## Debug Tools

### Debug Mode Activation

```python
# Enable debug mode globally
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable component-specific debugging
from summarizer.gpt_summarizer import GPTSummarizer
from utils.company_alias_matcher import get_company_matcher

summarizer = GPTSummarizer(debug=True)
matcher = get_company_matcher(debug=True)
```

### Content Analysis Tools

```python
# Analyze content before processing
def analyze_content_quality(content):
    """Analyze content for quality indicators"""
    analysis = {
        'total_items': len(content),
        'with_pricing_keywords': 0,
        'with_vendor_mentions': 0,
        'average_length': 0,
        'sources': set()
    }
    
    pricing_keywords = ['price', 'cost', 'pricing', 'license', 'subscription']
    vendor_keywords = ['microsoft', 'vmware', 'cisco', 'dell', 'aws']
    
    total_length = 0
    for item in content:
        text = f"{item.get('title', '')} {item.get('content', '')}".lower()
        
        if any(keyword in text for keyword in pricing_keywords):
            analysis['with_pricing_keywords'] += 1
        
        if any(vendor in text for vendor in vendor_keywords):
            analysis['with_vendor_mentions'] += 1
        
        total_length += len(text)
        analysis['sources'].add(item.get('source', 'unknown'))
    
    analysis['average_length'] = total_length / len(content) if content else 0
    analysis['sources'] = list(analysis['sources'])
    
    return analysis

# Usage
content_quality = analyze_content_quality(your_content)
print(f"Content analysis: {content_quality}")
```

### Network Testing

```python
# Test all external API endpoints
def test_network_connectivity():
    """Test connectivity to all required services"""
    import requests
    import os
    
    endpoints = [
        ('OpenAI', 'https://api.openai.com/v1/models'),
        ('Reddit', 'https://www.reddit.com'),
        ('Google', 'https://www.googleapis.com/customsearch/v1'),
    ]
    
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=10)
            print(f"✅ {name}: {response.status_code}")
        except requests.exceptions.Timeout:
            print(f"⏱️ {name}: Timeout")
        except requests.exceptions.ConnectionError:
            print(f"❌ {name}: Connection failed")
        except Exception as e:
            print(f"❌ {name}: {e}")

test_network_connectivity()
```

## Getting Help

### Information to Provide

When seeking help, please provide:

1. **System Information**
   ```bash
   python --version
   pip list | grep -E "(openai|praw|requests)"
   uname -a  # Linux/macOS
   ```

2. **Error Messages**
   ```bash
   # Full error traceback
   # Recent log entries
   tail -50 logs/system.log
   ```

3. **Configuration**
   ```bash
   # Sanitized configuration (remove API keys)
   cat config/config.py | grep -v "secret\|key\|password"
   ```

4. **Test Results**
   ```bash
   python run_tests.py --quiet
   ```

### Support Channels

1. **Documentation**
   - [Deployment Guide](DEPLOYMENT.md)
   - [API Documentation](API.md)
   - System logs and debug files

2. **Self-Service Diagnostics**
   ```bash
   # Run comprehensive diagnostics
   python -c "
   from utils.health_checker import HealthChecker
   health = HealthChecker()
   health.run_comprehensive_diagnostics()
   "
   ```

3. **Community Resources**
   - Check existing issues in repository
   - Review configuration examples
   - Consult API documentation

---

**Remember:** Always sanitize logs and configuration files before sharing, removing any sensitive information like API keys, passwords, or personal data.