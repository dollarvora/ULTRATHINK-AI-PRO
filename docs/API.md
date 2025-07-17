# 📚 ULTRATHINK-AI-PRO API Documentation

## Table of Contents
- [Overview](#overview)
- [Core Components](#core-components)
- [GPT Summarizer API](#gpt-summarizer-api)
- [Company Alias Matcher API](#company-alias-matcher-api)
- [HTML Generator API](#html-generator-api)
- [Fetchers API](#fetchers-api)
- [Configuration API](#configuration-api)
- [Performance Monitoring API](#performance-monitoring-api)
- [Integration Examples](#integration-examples)
- [Error Handling](#error-handling)

## Overview

ULTRATHINK-AI-PRO provides a comprehensive API for B2B pricing intelligence analysis. The system is designed with modular components that can be used independently or together for complete pricing intelligence workflows.

### Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   Processing    │    │     Output      │
│                 │    │                 │    │                 │
│ • Reddit API    │───▶│ • GPT Analysis  │───▶│ • HTML Reports  │
│ • Google Search │    │ • Alias Matcher │    │ • Email Alerts  │
│ • LinkedIn      │    │ • Performance   │    │ • JSON Data     │
│ • Twitter       │    │   Monitor       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Features

- **Multi-source data aggregation** from Reddit, Google, LinkedIn, Twitter
- **Advanced GPT-4o-mini analysis** with anti-hallucination measures
- **Company alias matching** with 64+ vendors and 300+ aliases
- **Mobile-responsive HTML reporting** with accessibility features
- **Performance monitoring** and health checks
- **Role-based analysis** for different business functions

## Core Components

### GPTSummarizer

The core intelligence engine that processes content and generates pricing insights.

```python
from summarizer.gpt_summarizer import GPTSummarizer

# Initialize
summarizer = GPTSummarizer(debug=True)

# Generate insights
insights = summarizer.generate_insights(content, role='pricing_profitability_team')
```

### CompanyAliasMatcher

Advanced vendor detection with extensive alias support.

```python
from utils.company_alias_matcher import get_company_matcher

# Initialize
matcher = get_company_matcher(debug=True)

# Find companies in text
result = matcher.find_companies_in_text("Microsoft Azure pricing update")
```

### EnhancedHTMLGenerator

Mobile-responsive, accessible HTML report generation.

```python
from html_generator import generate_and_save_report

# Generate report
html_file = generate_and_save_report(
    insights=insights,
    all_content=content,
    vendor_analysis=vendor_stats,
    config=CONFIG
)
```

## GPT Summarizer API

### Class: `GPTSummarizer`

#### Constructor

```python
def __init__(self, debug: bool = False)
```

**Parameters:**
- `debug` (bool): Enable debug logging and enhanced output

**Example:**
```python
summarizer = GPTSummarizer(debug=True)
```

#### Methods

##### `generate_summary(content_by_source, config)`

Generates comprehensive pricing intelligence summary from multi-source content.

**Parameters:**
- `content_by_source` (Dict[str, List[Dict]]): Content organized by source
- `config` (Dict): System configuration

**Returns:**
- `Dict`: Structured summary with role-based insights

**Example:**
```python
content_by_source = {
    'reddit': [
        {
            'title': 'Microsoft pricing update',
            'content': 'Office 365 prices increasing 15%',
            'url': 'https://reddit.com/r/sysadmin/...',
            'created_at': '2024-06-15',
            'source': 'reddit'
        }
    ]
}

config = {
    'summarization': {
        'model': 'gpt-4o-mini',
        'max_tokens': 800,
        'temperature': 0.3
    }
}

result = summarizer.generate_summary(content_by_source, config)
```

**Response Structure:**
```json
{
  "role_summaries": {
    "pricing_profitability_team": {
      "role": "Pricing Profitability Team",
      "summary": "Analysis of vendor pricing strategies...",
      "key_insights": [
        "🔴 Microsoft Office 365 pricing increased 15%",
        "🟡 VMware licensing changes driving migration"
      ],
      "top_vendors": [
        {"vendor": "Microsoft", "mentions": 3, "highlighted": true}
      ],
      "sources": ["Reddit", "Google"],
      "confidence_score": 8.5
    }
  },
  "by_urgency": {"high": 2, "medium": 3, "low": 1},
  "total_items": 6
}
```

##### `generate_role_based_summary(content_by_source, target_role)`

Generates summary targeted for specific business role.

**Parameters:**
- `content_by_source` (Dict): Content organized by source
- `target_role` (str): Target role ('pricing_analyst', 'procurement_manager', 'bi_strategy')

**Returns:**
- `Dict`: Role-specific analysis

**Example:**
```python
procurement_summary = summarizer.generate_role_based_summary(
    content_by_source, 
    'procurement_manager'
)
```

##### `get_analysis_keywords()`

Returns all keywords and criteria used for analysis.

**Returns:**
- `Dict`: Categorized keywords and indicators

**Example:**
```python
keywords = summarizer.get_analysis_keywords()
print(keywords['pricing_indicators'])
print(keywords['urgency_keywords'])
```

### Advanced Features

#### Vendor Tier System

The GPT Summarizer uses a tier-based vendor prioritization system:

```python
# Tier 1 (Highest Priority): Major vendors
tier1_vendors = ['Microsoft', 'VMware', 'Cisco', 'Dell', 'HPE', 'Oracle', 'Broadcom']

# Tier 2 (High Priority): Security/Cloud vendors  
tier2_vendors = ['CrowdStrike', 'Fortinet', 'Palo Alto Networks', 'Zscaler', 'AWS']

# Tier 3 (Medium Priority): Distributors
tier3_vendors = ['TD SYNNEX', 'Ingram Micro', 'CDW', 'Insight', 'SHI']
```

#### Confidence Scoring

Insights receive confidence scores based on multiple factors:

- **High Confidence**: 3+ sources + quantified data ($ amounts, percentages)
- **Medium Confidence**: 2+ sources OR specific vendor + pricing details
- **Low Confidence**: Single source with general information

#### Anti-Hallucination Measures

- 7 specific rules preventing fictional pricing scenarios
- Content-based validation requirements
- Rejection of stock market data in favor of vendor pricing
- Mandatory source attribution for all insights

## Company Alias Matcher API

### Class: `CompanyAliasMatcher`

#### Constructor

```python
def __init__(self, debug: bool = False)
```

#### Methods

##### `find_companies_in_text(text, min_confidence=0.5)`

Finds all companies mentioned in text using alias matching.

**Parameters:**
- `text` (str): Text to analyze
- `min_confidence` (float): Minimum confidence threshold (0.0-1.0)

**Returns:**
- `AliasMatchResult`: Comprehensive match results

**Example:**
```python
text = "Microsoft Azure and VMware vSphere pricing updates"
result = matcher.find_companies_in_text(text)

print(f"Companies found: {result.matched_companies}")
print(f"Alias hits: {result.alias_hits}")
print(f"Confidence: {result.confidence_score}")
```

**Response Structure:**
```python
AliasMatchResult(
    matched_companies={'microsoft', 'vmware'},
    alias_hits={
        'microsoft': ['azure'],
        'vmware': ['vsphere']
    },
    total_matches=2,
    confidence_score=0.85
)
```

##### `normalize_company_name(company_input)`

Normalizes company name or alias to standard form.

**Parameters:**
- `company_input` (str): Company name or alias

**Returns:**
- `str` or `None`: Normalized company name

**Example:**
```python
normalized = matcher.normalize_company_name('azure')
print(normalized)  # Output: 'microsoft'
```

##### `expand_keyword_list(keywords)`

Expands keyword list to include all relevant aliases.

**Parameters:**
- `keywords` (List[str]): Original keywords

**Returns:**
- `List[str]`: Expanded keywords with aliases

**Example:**
```python
keywords = ['microsoft', 'vmware']
expanded = matcher.expand_keyword_list(keywords)
# Output: ['microsoft', 'vmware', 'azure', 'office365', 'vsphere', 'vcenter', ...]
```

##### `get_company_relevance_score(text, target_companies)`

Calculates relevance scores for specific companies in text.

**Parameters:**
- `text` (str): Text to analyze
- `target_companies` (List[str]): Companies to score

**Returns:**
- `Dict[str, float]`: Company relevance scores (0.0-1.0)

**Example:**
```python
text = "Microsoft Office 365 pricing increased 15%"
companies = ['microsoft', 'vmware', 'cisco']
scores = matcher.get_company_relevance_score(text, companies)
# Output: {'microsoft': 0.95, 'vmware': 0.0, 'cisco': 0.0}
```

### Supported Vendors

The system supports 64+ major technology vendors with 300+ aliases:

#### Major Cloud & Software Vendors
- Microsoft (azure, office365, teams, sharepoint, m365, o365)
- Google Cloud (gcp, google workspace, gsuite, bigquery)
- AWS (amazon web services, ec2, s3, lambda, rds)
- Oracle (oracle cloud, oci, oracle database)

#### Hardware & Infrastructure  
- Dell (emc, dell emc, poweredge, isilon, unity)
- Cisco (webex, meraki, umbrella, duo, catalyst)
- HP/HPE (hewlett packard, proliant, greenlake)
- VMware (vsphere, vcenter, esxi, nsx, workspace one)

#### Cybersecurity
- CrowdStrike (falcon, cs falcon)
- Fortinet (fortigate, fortianalyzer, fortisandbox)
- Palo Alto Networks (pan-os, cortex xdr, prisma cloud)
- Zscaler (zpa, zia, zscaler internet access)

#### Distributors & Resellers
- TD SYNNEX (tech data, synnex)
- Ingram Micro (ingram, ingramcloud)
- CDW (cdw corporation, cdwg)
- Insight (insight global, insight enterprises)

## HTML Generator API

### Class: `EnhancedHTMLGenerator`

#### Constructor

```python
def __init__(self, debug: bool = False)
```

#### Methods

##### `generate_html_report(insights, all_content, vendor_analysis, config, performance_metrics=None)`

Generates comprehensive HTML report with mobile responsiveness and accessibility.

**Parameters:**
- `insights` (List[str]): Generated insights
- `all_content` (List[Dict]): All analyzed content
- `vendor_analysis` (Dict): Vendor statistics
- `config` (Dict): System configuration
- `performance_metrics` (Dict, optional): Performance data

**Returns:**
- `str`: Complete HTML content

**Example:**
```python
generator = EnhancedHTMLGenerator(debug=True)

html_content = generator.generate_html_report(
    insights=insights,
    all_content=content,
    vendor_analysis=vendor_stats,
    config=CONFIG,
    performance_metrics=performance_data
)
```

##### `save_html_report(html_content, output_dir="output")`

Saves HTML report to timestamped file.

**Parameters:**
- `html_content` (str): HTML content to save
- `output_dir` (str): Output directory

**Returns:**
- `str`: Path to saved file

**Example:**
```python
html_file = generator.save_html_report(html_content, "reports")
print(f"Report saved: {html_file}")
```

### Accessibility Features

The HTML generator includes comprehensive accessibility features:

- **Semantic HTML**: Proper use of `<main>`, `<header>`, `<section>`, `<article>`
- **ARIA Labels**: Screen reader support with `aria-label`, `role` attributes
- **Keyboard Navigation**: Focus styles and proper tab order
- **Visual Accessibility**: High contrast mode and reduced motion support
- **Mobile Responsiveness**: Viewport meta tags and responsive CSS

### Mobile Responsiveness

Responsive breakpoints:
- **Desktop**: 1024px+ (full layout)
- **Tablet**: 768px-1023px (adjusted spacing)
- **Mobile**: 480px-767px (stacked layout)
- **Small Mobile**: <480px (minimal spacing)

## Fetchers API

### Reddit Fetcher

```python
from fetchers.reddit_fetcher import RedditFetcher

fetcher = RedditFetcher()
content = fetcher.fetch_content(config)
```

### Google Fetcher

```python
from fetchers.google_fetcher import GoogleFetcher

fetcher = GoogleFetcher()
content = fetcher.fetch_content(config)
```

### Async Support

```python
from fetchers.reddit_fetcher import AsyncRedditFetcher
import asyncio

async def fetch_data():
    fetcher = AsyncRedditFetcher(config)
    return await fetcher.fetch_content()

content = asyncio.run(fetch_data())
```

## Configuration API

### Loading Configuration

```python
from config.config import CONFIG, load_keywords

# Access configuration
system_config = CONFIG['system']
credentials = CONFIG['credentials']
keywords = CONFIG['keywords']
```

### Environment Variables

Required environment variables:

```bash
OPENAI_API_KEY=sk-...
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
GOOGLE_API_KEY=...
GOOGLE_CSE_ID=...
```

## Performance Monitoring API

### Class: `PerformanceMonitor`

```python
from utils.performance_monitor import PerformanceMonitor

# Initialize
monitor = PerformanceMonitor("system_name", debug=True)

# Start operation tracking
operation = monitor.start_operation("data_fetch")

# Complete operation
monitor.complete_operation(operation, success=True, data_size=150)

# Get performance summary
summary = monitor.get_enhanced_performance_summary()
```

## Integration Examples

### Complete Workflow

```python
#!/usr/bin/env python3
"""
Complete ULTRATHINK-AI-PRO workflow example
"""
import asyncio
from config.config import CONFIG
from summarizer.gpt_summarizer import GPTSummarizer
from fetchers.reddit_fetcher import RedditFetcher
from fetchers.google_fetcher import GoogleFetcher
from html_generator import generate_and_save_report
from utils.performance_monitor import PerformanceMonitor

async def main():
    # Initialize components
    monitor = PerformanceMonitor("workflow_example", debug=True)
    summarizer = GPTSummarizer(debug=True)
    reddit_fetcher = RedditFetcher()
    google_fetcher = GoogleFetcher()
    
    # Fetch data
    print("📡 Fetching data...")
    reddit_content = reddit_fetcher.fetch_content(CONFIG)
    google_content = google_fetcher.fetch_content(CONFIG)
    
    # Combine content
    all_content = reddit_content + google_content
    content_by_source = {
        'reddit': reddit_content,
        'google': google_content
    }
    
    # Generate insights
    print("🧠 Analyzing content...")
    insights = summarizer.generate_summary(content_by_source, CONFIG)
    
    # Generate report
    print("📄 Generating report...")
    html_file = generate_and_save_report(
        insights=insights['role_summaries']['pricing_profitability_team']['key_insights'],
        all_content=all_content,
        vendor_analysis={},
        config=CONFIG,
        performance_metrics=monitor.get_enhanced_performance_summary()
    )
    
    print(f"✅ Complete! Report saved: {html_file}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Custom Analysis

```python
"""
Custom analysis for specific vendors
"""
from utils.company_alias_matcher import get_company_matcher
from summarizer.gpt_summarizer import GPTSummarizer

def analyze_vendor_sentiment(text, target_vendor):
    """Analyze sentiment for specific vendor"""
    matcher = get_company_matcher()
    summarizer = GPTSummarizer()
    
    # Check if vendor is mentioned
    result = matcher.find_companies_in_text(text)
    normalized_vendor = matcher.normalize_company_name(target_vendor)
    
    if normalized_vendor in result.matched_companies:
        # Generate targeted analysis
        content = [{'title': 'Analysis', 'content': text, 'source': 'custom'}]
        summary = summarizer.generate_role_based_summary(
            {'custom': content}, 
            'pricing_analyst'
        )
        return summary
    
    return None

# Example usage
text = "Microsoft Azure pricing increased 25% causing budget concerns"
analysis = analyze_vendor_sentiment(text, "microsoft")
```

## Error Handling

### Common Exceptions

```python
from summarizer.gpt_summarizer import GPTSummarizer
import openai

try:
    summarizer = GPTSummarizer()
    result = summarizer.generate_summary(content, config)
except openai.error.RateLimitError:
    print("API rate limit exceeded")
except openai.error.AuthenticationError:
    print("Invalid API key")
except openai.error.APIError as e:
    print(f"OpenAI API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Graceful Degradation

The system includes automatic fallback mechanisms:

1. **GPT Failures**: Returns structured fallback summary
2. **Network Issues**: Retries with exponential backoff
3. **API Limits**: Reduces request frequency automatically
4. **Parsing Errors**: JSON recovery and repair mechanisms

### Health Checks

```python
from utils.health_checker import HealthChecker

health = HealthChecker()
status = health.check_all()

if not status['healthy']:
    print("System issues detected:")
    for issue in status['issues']:
        print(f"- {issue}")
```

---

**Need Help?**
- Check the [Deployment Guide](DEPLOYMENT.md)
- Review [Troubleshooting Guide](TROUBLESHOOTING.md)
- Contact system administrators