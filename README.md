# 🧠 ULTRATHINK - AI-Powered Pricing Intelligence

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-supported-brightgreen)](https://www.docker.com/)

ULTRATHINK is a production-grade automated pricing intelligence system that leverages AI to collect, analyze, and deliver actionable pricing insights from multiple data sources to enterprise teams.

## 🚀 Features

- **Multi-Source Intelligence**: Fetches from Reddit, Twitter/X, LinkedIn, and Google News
- **AI-Powered Summarization**: Uses GPT-4 to create role-specific summaries
- **Smart Scoring**: Prioritizes content by urgency, vendor relevance, and keywords
- **Role-Based Delivery**: Customized digests for Pricing Analysts, Procurement Managers, and BI Teams
- **Automated Scheduling**: Daily automated runs with email delivery
- **Docker Support**: Easy deployment with Docker and docker-compose

## 📋 Requirements

- Python 3.11+
- Docker & Docker Compose (optional)
- API Keys:
  - Reddit API credentials
  - Google Custom Search Engine API
  - OpenAI API key
  - SMTP server for email delivery

## 🛠️ Installation

### Local Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/ultrathink.git
cd ultrathink
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
python manage.py install_playwright
```

5. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

6. Validate setup:
```bash
python manage.py validate
```

### Docker Installation

1. Build the image:
```bash
docker-compose build
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Run validation:
```bash
docker-compose run --rm ultrathink python manage.py validate
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following:

```env
# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USER_AGENT=ULTRATHINK/1.0

# Google CSE
GOOGLE_API_KEY=your_api_key
GOOGLE_CSE_ID=your_cse_id

# OpenAI
OPENAI_API_KEY=your_openai_key

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=ULTRATHINK <your_email@gmail.com>

# Optional: LinkedIn
LINKEDIN_USERNAME=your_linkedin_email
LINKEDIN_PASSWORD=your_linkedin_password
```

### Configuration File

Edit `config/config.json` to customize:
- Keywords and vendors to track
- Source-specific settings
- Scoring weights
- Email templates

### Employee List

Update `config/employees.csv` with your team:

```csv
name,email,role,active,keywords
John Doe,john@company.com,pricing_analyst,true,"microsoft,azure"
Jane Smith,jane@company.com,procurement_manager,true,"dell,cisco"
```

## 📦 Usage

### Basic Commands

**Run once and exit:**
```bash
python run.py --once
```

**Run with test data:**
```bash
python run.py --test --once
```

**Preview mode (no emails):**
```bash
python run.py --preview --once
```

**Docker run:**
```bash
docker-compose up
```

**Scheduled mode (Docker):**
```bash
docker-compose --profile scheduler up -d
```

### Management Commands

**Validate configuration:**
```bash
python manage.py validate
```

**View statistics:**
```bash
python manage.py stats
```

**Test specific source:**
```bash
python manage.py test_fetch --source reddit
```

**Add new user:**
```bash
python manage.py add_user john@example.com --role pricing_analyst
```

**Clean old files:**
```bash
python manage.py clean
```

## 📊 Architecture

```
ultrathink/
├── fetchers/          # Content fetchers for each source
│   ├── reddit_fetcher.py
│   ├── linkedin_fetcher.py
│   ├── google_fetcher.py
│   ├── twitter_fetcher.py
│   └── base_fetcher.py
├── summarizer/        # AI summarization
│   └── gpt_summarizer.py
├── emailer/          # Email generation and sending
│   ├── template.py
│   └── sender.py
├── config/           # Configuration files
│   ├── config.json
│   ├── employees.csv
│   └── config.py
├── tests/            # Unit tests
├── scripts/          # Utility scripts
├── test_data/        # Mock data for testing
├── output/           # Generated reports (gitignored)
├── logs/             # Application logs (gitignored)
├── cache/            # Cached data (gitignored)
├── run.py            # Main entry point
└── manage.py         # Management commands
```

## 🔍 Tracked Vendors & Keywords

### Keywords
- Pricing updates, cost increases, vendor discounts
- Licensing changes, margin compression
- Budget impacts, tool rationalization

### Vendors
- **Hardware**: Dell, HPE, Cisco
- **Security**: CrowdStrike, Palo Alto, Fortinet, Zscaler
- **Software**: Microsoft, Oracle, SAP
- **Distributors**: TD SYNNEX, CDW, Ingram Micro

## 📈 Scoring Algorithm

Content is scored based on:
- **Keyword matches** (weight: 1.0)
- **Urgency indicators** (weight: 2.0)
- **Vendor mentions** (weight: 1.5)
- **Recency** (weight: 0.5)

## 🔒 Security Considerations

- Store API keys in environment variables
- Use app-specific passwords for email
- LinkedIn scraping respects rate limits
- Docker runs as non-root user
- Sensitive data is not logged

## 🐛 Troubleshooting

### Common Issues

**LinkedIn fetch fails:**
- Check if LinkedIn credentials are set
- Verify Playwright browsers are installed
- May need to handle 2FA manually first

**No Reddit results:**
- Verify Reddit API credentials
- Check if subreddits are accessible
- Review rate limit status

**Email not sending:**
- Verify SMTP settings
- Check firewall/port access
- Enable "less secure apps" if using Gmail

### Debug Mode

Run with increased logging:
```bash
LOG_LEVEL=DEBUG python run.py --once
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Add tests for new functionality
5. Ensure `python manage.py validate` passes
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📞 Support

For issues or questions:
- Check the [Issues](../../issues) page
- Review logs in `logs/` directory
- Run `python manage.py validate` for configuration validation
- Check our [Troubleshooting](#-troubleshooting) section

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- Reddit API for social media insights
- Google Custom Search for web intelligence
- All contributors and maintainers

---

**Version:** 1.0.0  
**Last Updated:** June 2025