import os

CONFIG = {
    "system": {
        "name": "ULTRATHINK Pricing Intelligence System",
        "version": "1.0.1",
        "timezone": "UTC",
        "run_hour": 8,
        "cache_ttl_hours": 24
    },
    "credentials": {
        "reddit": {
            "client_id": os.getenv("REDDIT_CLIENT_ID"),
            "client_secret": os.getenv("REDDIT_CLIENT_SECRET"),
            "user_agent": os.getenv("REDDIT_USER_AGENT")
        },
        "google": {
            "api_key": os.getenv("GOOGLE_API_KEY"),
            "cse_id": os.getenv("GOOGLE_CSE_ID")
        },
        "openai": {
            "api_key": os.getenv("OPENAI_API_KEY")
        },
        "email": {
            "smtp_host": os.getenv("SMTP_HOST"),
            "smtp_port": int(os.getenv("SMTP_PORT", 587)),
            "smtp_user": os.getenv("SMTP_USER"),
            "smtp_password": os.getenv("SMTP_PASSWORD"),
            "from_email": os.getenv("FROM_EMAIL")
        },
        "linkedin": {
            "username": os.getenv("LINKEDIN_USERNAME"),
            "password": os.getenv("LINKEDIN_PASSWORD")
        },
        "twitter": {
            "bearer_token": os.getenv("TWITTER_BEARER_TOKEN")
        }
    },
    "keywords": {
        "pricing": [
            "pricing update", "cost increase", "price increase", "vendor discount", "licensing change",
            "margin compression", "cybersecurity budget", "cloud pricing", "software inflation",
            "hardware surcharge", "tool rationalization", "contract renewal", "subscription pricing",
            "enterprise discount"
        ],
        "urgency_indicators": [
            "immediate", "urgent", "critical", "time-sensitive", "deadline", "expires", "limited time", "act now"
        ]
    },
    "vendors": {
        "hardware": ["Dell", "Dell Technologies", "HPE", "HP Enterprise", "Cisco", "Cisco Systems"],
        "software": ["Microsoft", "Oracle", "SAP", "Salesforce", "Adobe", "VMware"],
        "security": ["Palo Alto Networks", "CrowdStrike", "SentinelOne", "Zscaler", "Fortinet", "Okta", "Check Point", "TrendMicro", "Arctic Wolf", "Sophos", "Splunk", "Rapid7", "Tenable"],
        "distributors": ["TD SYNNEX", "CDW", "Insight", "Ingram Micro", "SHI", "Connection", "PCM"]
    },
    "sources": {
        "reddit": {
            "enabled": True,
            "subreddits": ["sysadmin", "msp", "cybersecurity", "ITManagers", "procurement", "enterprise", "cloudcomputing", "aws", "azure"],
            "post_limit": 50,
            "comment_limit": 20
        },
        "twitter": {
            "enabled": True,
            "handles": ["@crowdstrike", "@fortinet", "@paloaltontwks", "@Cisco", "@IngramMicro", "@tdsynnex", "@CDWCorp", "@TrendMicro", "@CheckPointSW", "@Zscaler", "@SentinelOne", "@OktaDev", "@sophos"],
            "hashtags": ["#enterprisepricing", "#vendorpricing", "#ITbudget", "#cybersecuritypricing", "#softwarelicensing"],
            "max_tweets": 100
        },
        "linkedin": {
            "enabled": True,
            "companies": ["Dell Technologies", "Microsoft", "Cisco", "Fortinet", "CrowdStrike", "Palo Alto Networks", "Zscaler", "TD SYNNEX", "Ingram Micro", "CDW", "Insight"],
            "post_limit": 20
        },
        "google": {
            "enabled": True,
            "queries": ["enterprise software pricing increase 2024", "cybersecurity vendor price changes", "IT distributor margin compression", "cloud pricing updates AWS Azure", "hardware vendor surcharge"],
            "results_per_query": 10,
            "date_restriction": "d7"
        }
    },
    "summarization": {
        "model": "gpt-4-turbo-preview",
        "max_tokens": 2000,
        "temperature": 0.3
    },
    "email": {
        "enabled": True,
        "subject_template": "[ULTRATHINK] Pricing Intelligence Digest - {date}",
        "send_time": "09:00",
        "test_recipients": ["test@example.com"],
        "employee_csv": "config/employees.csv"
    },
    "scoring": {
        "urgency_weight": 2.0,
        "vendor_weight": 1.5,
        "keyword_weight": 1.0,
        "recency_weight": 0.5,
        "high_score_threshold": 7.0,
        "medium_score_threshold": 4.0
    }
}
