# 🚀 ULTRATHINK-AI-PRO Deployment Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Installation Methods](#installation-methods)
- [Configuration](#configuration)
- [Security Setup](#security-setup)
- [Performance Optimization](#performance-optimization)
- [Monitoring & Logging](#monitoring--logging)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)

## Prerequisites

### System Requirements

**Minimum Requirements:**
- **OS**: Linux (Ubuntu 20.04+), macOS (10.15+), Windows 10+
- **Python**: 3.8 or higher
- **Memory**: 2GB RAM
- **Storage**: 1GB free space
- **Network**: Stable internet connection for API calls

**Recommended for Production:**
- **OS**: Ubuntu 22.04 LTS or CentOS 8+
- **Python**: 3.11+
- **Memory**: 4GB+ RAM
- **CPU**: 2+ cores
- **Storage**: 10GB+ SSD
- **Network**: 100Mbps+ connection

### Required API Access

1. **OpenAI API** (Required)
   - GPT-4o-mini access
   - Rate limit: 1000+ requests/day recommended

2. **Reddit API** (Required)
   - Create app at https://www.reddit.com/prefs/apps
   - Client ID and Secret needed

3. **Google Custom Search API** (Required)
   - Google Cloud Console project
   - Custom Search Engine ID

4. **SMTP Email Service** (Optional)
   - Gmail, SendGrid, or corporate SMTP
   - For automated report delivery

## Environment Setup

### 1. Python Environment

```bash
# Check Python version
python3 --version  # Should be 3.8+

# Create virtual environment
python3 -m venv ultrathink_env
source ultrathink_env/bin/activate  # Linux/macOS
# ultrathink_env\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip
```

### 2. Clone and Install

```bash
# Clone repository
git clone https://github.com/your-org/ULTRATHINK-AI-PRO.git
cd ULTRATHINK-AI-PRO

# Install dependencies
pip install -r requirements_minimal.txt

# Install additional production dependencies (optional)
pip install gunicorn supervisor  # For production deployment
```

### 3. Environment Variables

Create `.env` file in project root:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Reddit API (https://www.reddit.com/prefs/apps)
REDDIT_CLIENT_ID=your-reddit-client-id
REDDIT_CLIENT_SECRET=your-reddit-client-secret
REDDIT_USER_AGENT=ULTRATHINK-AI-PRO/3.1.0

# Google Custom Search
GOOGLE_API_KEY=your-google-api-key
GOOGLE_CSE_ID=your-custom-search-engine-id

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=ULTRATHINK-AI-PRO <your-email@gmail.com>

# Security (Production)
DEBUG=false
LOG_LEVEL=INFO
```

## Installation Methods

### Method 1: Standard Installation

```bash
# Basic installation
python create_real_system.py

# Test the system
python test_production_system.py

# Run comprehensive tests
python run_tests.py
```

### Method 2: Docker Installation (Recommended for Production)

```bash
# Build Docker image
docker build -t ultrathink-ai-pro:latest .

# Run with environment file
docker run --env-file .env -v $(pwd)/output:/app/output ultrathink-ai-pro:latest

# Run with docker-compose
docker-compose up -d
```

### Method 3: Automated Deployment

```bash
# Make deployment script executable
chmod +x deploy.sh

# Run automated deployment
./deploy.sh production

# Check deployment status
./deploy.sh status
```

## Configuration

### 1. Employee Configuration

Edit `config/employees.csv` with your team members:

```csv
name,email,role,department,active
John Doe,john.doe@company.com,pricing_analyst,Finance,true
Jane Smith,jane.smith@company.com,procurement_manager,Procurement,true
Bob Johnson,bob.johnson@company.com,bi_strategy,Strategy,true
```

### 2. Keywords Configuration

Customize `config/keywords.json` for your industry:

```json
{
  "vendors": {
    "your_industry": ["vendor1", "vendor2", "vendor3"]
  },
  "pricing_keywords": [
    "custom_keyword_1",
    "custom_keyword_2"
  ]
}
```

### 3. System Configuration

Modify `config/config.py` for your needs:

```python
CONFIG = {
    "system": {
        "name": "Your Company Pricing Intelligence",
        "run_hour": 8,  # Daily run time (24h format)
        "timezone": "America/New_York"
    },
    "sources": {
        "reddit": {
            "subreddits": ["your_industry_subreddit"],
            "post_limit": 25  # Adjust based on needs
        }
    }
}
```

## Security Setup

### 1. API Key Security

```bash
# Set restrictive permissions on .env
chmod 600 .env

# Never commit .env to version control
echo ".env" >> .gitignore

# Use environment-specific files
cp .env .env.production
cp .env .env.staging
```

### 2. Production Security Checklist

- [ ] All API keys stored in environment variables
- [ ] `.env` file has restrictive permissions (600)
- [ ] Debug mode disabled in production
- [ ] Logs don't contain sensitive information
- [ ] Network access restricted (firewall rules)
- [ ] Regular security updates applied
- [ ] Monitoring and alerting configured

### 3. Network Security

```bash
# Example firewall rules (Ubuntu/CentOS)
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 443/tcp     # HTTPS
sudo ufw deny 80/tcp       # HTTP (force HTTPS)
sudo ufw enable

# For cloud deployments, use security groups/NSGs
```

## Performance Optimization

### 1. System Optimization

```bash
# Increase file descriptor limits
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Optimize Python performance
export PYTHONOPTIMIZE=1
export PYTHONDONTWRITEBYTECODE=1
```

### 2. Application Optimization

```python
# config/config.py optimizations
CONFIG = {
    "sources": {
        "reddit": {
            "post_limit": 50,  # Balance between data and performance
            "comment_limit": 10
        },
        "google": {
            "results_per_query": 8,
            "max_concurrent_requests": 5
        }
    },
    "summarization": {
        "max_tokens": 500,  # Reduce for faster processing
        "temperature": 0.3
    }
}
```

### 3. Caching Configuration

```bash
# Enable Redis caching (optional)
sudo apt-get install redis-server
redis-cli config set maxmemory 256mb
redis-cli config set maxmemory-policy allkeys-lru
```

## Monitoring & Logging

### 1. Application Logs

```bash
# Configure log rotation
sudo tee /etc/logrotate.d/ultrathink << EOF
/opt/ultrathink/logs/*.log {
    daily
    rotate 30
    compress
    missingok
    notifempty
    create 0644 ultrathink ultrathink
}
EOF
```

### 2. Performance Monitoring

```python
# Enable performance metrics in config
CONFIG = {
    "monitoring": {
        "enabled": True,
        "metrics_file": "logs/performance.json",
        "alert_thresholds": {
            "runtime": 300,  # seconds
            "success_rate": 0.90,
            "api_errors": 5
        }
    }
}
```

### 3. Health Checks

```bash
# Create health check script
cat > health_check.sh << 'EOF'
#!/bin/bash
cd /opt/ultrathink-ai-pro
python -c "
import sys
sys.path.insert(0, '.')
from utils.health_checker import HealthChecker
health = HealthChecker()
status = health.check_all()
sys.exit(0 if status['healthy'] else 1)
"
EOF

chmod +x health_check.sh
```

### 4. Automated Monitoring Setup

```bash
# Add to crontab for regular health checks
crontab -e

# Add these lines:
# Health check every 15 minutes
*/15 * * * * /opt/ultrathink-ai-pro/health_check.sh || echo "ULTRATHINK health check failed" | mail -s "Alert" admin@company.com

# Daily execution at 8 AM
0 8 * * * cd /opt/ultrathink-ai-pro && python create_real_system.py
```

## Troubleshooting

### Common Issues

#### 1. API Rate Limits

```bash
# Symptoms: HTTP 429 errors in logs
# Solution: Adjust request rates

# config/config.py
CONFIG = {
    "rate_limiting": {
        "requests_per_minute": 10,  # Reduce from default
        "backoff_factor": 2.0
    }
}
```

#### 2. Memory Issues

```bash
# Symptoms: Out of memory errors
# Solution: Reduce content processing

# config/config.py
CONFIG = {
    "sources": {
        "reddit": {
            "post_limit": 25,  # Reduce from 50
            "comment_limit": 5   # Reduce from 20
        }
    }
}
```

#### 3. Network Connectivity

```bash
# Test API connectivity
python -c "
import requests
import os
from dotenv import load_dotenv
load_dotenv()

# Test OpenAI
try:
    response = requests.get('https://api.openai.com/v1/models', 
                           headers={'Authorization': f'Bearer {os.getenv(\"OPENAI_API_KEY\")}'})
    print(f'OpenAI: {response.status_code}')
except Exception as e:
    print(f'OpenAI Error: {e}')

# Test Reddit
try:
    response = requests.get('https://www.reddit.com/api/v1/access_token', 
                           auth=(os.getenv('REDDIT_CLIENT_ID'), os.getenv('REDDIT_CLIENT_SECRET')),
                           data={'grant_type': 'client_credentials'},
                           headers={'User-Agent': os.getenv('REDDIT_USER_AGENT')})
    print(f'Reddit: {response.status_code}')
except Exception as e:
    print(f'Reddit Error: {e}')
"
```

### Log Analysis

```bash
# Common log locations
tail -f logs/system.log           # Application logs
tail -f logs/performance.log      # Performance metrics
tail -f logs/debug.log           # Debug information

# Search for errors
grep -i error logs/*.log | tail -20
grep -i "rate limit" logs/*.log
grep -i "timeout" logs/*.log
```

### Performance Diagnostics

```bash
# Run performance diagnostics
python -c "
from utils.performance_monitor import PerformanceMonitor
monitor = PerformanceMonitor('diagnostic', debug=True)
monitor.diagnose_system()
monitor.print_diagnostic_report()
"
```

## Maintenance

### Daily Tasks
- [ ] Check system logs for errors
- [ ] Verify report generation
- [ ] Monitor API usage quotas
- [ ] Review performance metrics

### Weekly Tasks
- [ ] Update dependencies (if needed)
- [ ] Clean up old log files
- [ ] Backup configuration files
- [ ] Review generated reports quality

### Monthly Tasks
- [ ] Security updates
- [ ] Performance optimization review
- [ ] API key rotation (if required)
- [ ] System resource planning

### Backup Strategy

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/ultrathink-$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Backup configuration
cp -r config/ "$BACKUP_DIR/"

# Backup recent reports
cp -r output/ "$BACKUP_DIR/"

# Backup logs (last 7 days)
find logs/ -name "*.log" -mtime -7 -exec cp {} "$BACKUP_DIR/" \;

# Create archive
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

echo "Backup created: $BACKUP_DIR.tar.gz"
EOF

chmod +x backup.sh
```

## Production Deployment Checklist

### Pre-deployment
- [ ] All tests passing (`python run_tests.py`)
- [ ] Environment variables configured
- [ ] Firewall rules configured
- [ ] Monitoring setup complete
- [ ] Backup strategy implemented

### Deployment
- [ ] Deploy to staging environment first
- [ ] Run smoke tests
- [ ] Deploy to production
- [ ] Verify all services running
- [ ] Test end-to-end functionality

### Post-deployment
- [ ] Monitor logs for 24 hours
- [ ] Verify scheduled jobs running
- [ ] Check report generation
- [ ] Validate email delivery (if configured)
- [ ] Performance baseline established

---

**Need Help?** 
- Check the [API Documentation](API.md)
- Review [Troubleshooting Guide](TROUBLESHOOTING.md)
- Contact system administrators