# ULTRATHINK Enhanced
## Enterprise Pricing Intelligence Platform

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-enabled-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Portfolio](https://img.shields.io/badge/type-portfolio-brightgreen.svg)](https://github.com/dollarvora)
[![License: Proprietary](https://img.shields.io/badge/license-proprietary-red.svg)](./LICENSE)

**ULTRATHINK Enhanced** is an enhanced version of [ULTRATHINK](https://github.com/dollarvora/ultrathink) - an AI-powered enterprise pricing intelligence platform that delivers automated market analysis for IT procurement and distribution professionals.

## Overview

ULTRATHINK Enhanced monitors market discussions, vendor announcements, and pricing changes across technology sectors to deliver actionable intelligence through automated analysis and reporting.

### Key Capabilities

- **Multi-Source Data Collection**: Reddit communities and Google Custom Search
- **AI-Powered Analysis**: GPT-4 powered insights with source attribution  
- **Vendor Intelligence**: 43+ technology vendors with 129+ alias recognition
- **Professional Reporting**: Clean, executive-ready analysis reports
- **Automated Delivery**: Email-based distribution with interactive HTML reports

### Data Sources

- **Reddit Sources (Active)**: 12+ subreddits including r/sysadmin, r/msp, r/cybersecurity
- **Google Search Intelligence (Active)**: Dynamic query generation and trending vendor detection
- **LinkedIn Integration (Framework Ready)**: Available for future activation

## Requirements

- Python 3.11+
- API Keys:
  - Reddit API credentials  
  - Google Custom Search Engine API
  - OpenAI API key
  - SMTP server access

## Quick Start

1. **Clone and Setup**
```bash
git clone https://github.com/dollarvora/ultrathink-enhanced.git
cd ultrathink-enhanced
```

2. **Configure Environment**
Create `.env` file:
```env
# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=ULTRATHINK/1.0

# Google Custom Search
GOOGLE_API_KEY=your_api_key
GOOGLE_CSE_ID=your_cse_id

# OpenAI
OPENAI_API_KEY=your_openai_key

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=ULTRATHINK <your_email@gmail.com>
```

3. **Install Dependencies**
```bash
pip install -r requirements_minimal.txt
```

4. **Configure Employee List**
Edit `config/employees.csv`:
```csv
name,email,role,vendors,manufacturers,distributors,topics,active
John Doe,john@company.com,pricing_analyst,microsoft,dell,cdw,pricing,true
```

5. **Run Analysis**
```bash
chmod +x run_system.sh
./run_system.sh
```

## Configuration

### Core Configuration
- `config/config.py`: Main system settings
- `config/employees.csv`: Team member configuration
- `config/keywords.json`: Keyword tracking settings

### Key Settings
- **Smart Fallback**: 24-hour to 7-day data extension
- **Vendor Coverage**: 43+ technology companies
- **Query Generation**: 20-50 dynamic searches per run
- **Content Filtering**: Advanced deduplication and relevance scoring

## Architecture

```
ultrathink-enhanced/
├── fetchers/              # Data collection modules
│   ├── reddit_fetcher.py
│   ├── google_fetcher.py
│   └── base_fetcher.py
├── summarizer/            # AI analysis engine
│   └── gpt_summarizer.py
├── utils/                 # Core utilities
│   ├── company_alias_matcher.py
│   ├── employee_manager.py
│   └── cache_manager.py
├── emailer/               # Report delivery
│   ├── sender.py
│   └── template.py
├── config/                # Configuration
│   ├── config.py
│   ├── employees.csv
│   └── keywords.json
├── create_real_system.py  # Main application
└── run_system.sh         # Execution script
```

## Vendor Coverage

Current detection includes:

- **Hardware**: Dell, HPE, Lenovo, Cisco, NetApp
- **Cloud Providers**: AWS, Microsoft Azure, Google Cloud
- **Security Vendors**: CrowdStrike, Palo Alto Networks, Fortinet, Zscaler
- **Software**: Microsoft, Oracle, SAP, VMware
- **MSP Tools**: ConnectWise, Kaseya, NinjaOne
- **Distribution**: TD Synnex, Ingram Micro, CDW

## Output

The system generates:
- **HTML Reports**: Interactive analysis with expandable sections
- **Source Attribution**: Clickable footnotes linking to original content
- **Confidence Indicators**: Source-based confidence levels (High/Medium/Moderate)
- **Professional Formatting**: Executive-ready presentation

## Security

- Environment variable based configuration
- No sensitive data in logs or output files
- Secure API key handling
- Professional error handling and logging

## License

⚠️ **ULTRATHINK Enhanced is proprietary software.**

This repository is shared for **demonstration and portfolio purposes only**. 

Use, copying, modification, redistribution, or commercialization is strictly prohibited without express written permission.

See [LICENSE](./LICENSE) for complete terms.

## Support

For configuration and setup questions:
- Review system logs for error details
- Verify API credentials and quotas
- Check network connectivity to data sources
- Ensure SMTP configuration is correct

---

**ULTRATHINK Enhanced v3.0**  
Advanced Market Intelligence Platform