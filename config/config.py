import os
import json
import logging

logger = logging.getLogger(__name__)

def load_keywords():
    """Load keywords from external JSON file"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    keywords_file = os.path.join(current_dir, 'keywords.json')
    
    try:
        with open(keywords_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to basic keywords if file not found
        return {
            "pricing_keywords": ["pricing", "cost", "discount", "margin"],
            "urgency_high": ["urgent", "critical", "immediate"]
        }

CONFIG = {
    "system": {
        "name": "ULTRATHINK-AI-PRO Pricing Intelligence System",
        "version": "3.1.0",
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
    "keywords": load_keywords(),
    "vendors": load_keywords().get("vendors", {}),
    "sources": {
        "reddit": {
            "enabled": True,
            "subreddits": ["sysadmin", "msp", "cybersecurity", "vmware", "AZURE", "aws", "networking", "devops", "homelab", "k8s", "kubernetes", "selfhosted", "DataHoarder", "storage", "linuxadmin", "PowerShell", "ITManagers", "BusinessIntelligence", "enterprise", "ITCareerQuestions", "procurement", "purchasing", "FinancialCareers", "accounting", "analytics", "consulting", "smallbusiness", "startups", "entrepreneur"],
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
            "queries": [
                "enterprise software pricing increase", 
                "cybersecurity vendor price changes", 
                "IT distributor margin compression", 
                "cloud pricing updates AWS Azure", 
                "hardware vendor surcharge", 
                "vendor pricing announcements",
                "partner program changes", 
                "channel program updates", 
                "reseller program modifications",
                "vendor program discontinuation", 
                "partner program shutdown", 
                "channel partner migration",
                "VCSP program changes", 
                "VMware partner program", 
                "Microsoft partner program updates",
                "Cisco partner program changes", 
                "Dell partner program modifications",
                "vendor business model changes", 
                "licensing model changes", 
                "subscription model mandatory",
                "vendor acquisition impact", 
                "merger channel effects", 
                "strategic partnership changes"
            ],
            "results_per_query": 10,
            "date_restriction": "d7"
        }
    },
    "summarization": {
        "model": "gpt-4o-mini",
        "max_tokens": 1200,
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
    },
    "security": {
        "rate_limits": {
            "openai": {"max_calls": 60, "time_window": 60},      # 60 calls per minute
            "reddit": {"max_calls": 100, "time_window": 60},     # 100 calls per minute  
            "google": {"max_calls": 100, "time_window": 86400},  # 100 calls per day
            "twitter": {"max_calls": 300, "time_window": 900}    # 300 calls per 15 min
        },
        "api_key_patterns": {
            "openai": r"^sk-[a-zA-Z0-9_-]{20,}$",
            "reddit": r"^[a-zA-Z0-9_-]{10,25}$", 
            "google": r"^[a-zA-Z0-9_-]{30,50}$",
            "twitter": r"^[a-zA-Z0-9]{100,}$"
        },
        "input_validation": {
            "max_text_length": 10000,
            "max_prompt_length": 50000,
            "max_title_length": 500,
            "max_query_length": 200,
            "max_log_length": 100,
            "suspicious_domains": ["bit.ly", "tinyurl.com", "short.link", "suspicious.com"]
        }
    },
    "performance": {
        "openai": {
            "fallback_model": "text-davinci-003",
            "presence_penalty": 0.1,
            "frequency_penalty": 0.1,
            "stop": None
        },
        "scoring_weights": {
            "company_boost_base": 0.3,
            "keyword_score_weight": 0.2,
            "urgency_high_weight": 0.3,
            "urgency_medium_weight": 0.1,
            "confidence_boost": 0.2
        },
        "reddit": {
            "quality_post_min_score": 3,
            "quality_post_min_comments": 3,
            "max_post_age_days": 30,
            "search_time_window": "week",
            "extended_search_days": 3
        }
    },
    "paths": {
        "output_dir": "output",
        "logs_dir": "logs", 
        "static_dir": "static",
        "config_dir": "config",
        "tests_dir": "tests",
        "css_file": "static/css/report.css"
    }
}

def get_secure_config():
    """Get configuration with security validation"""
    try:
        # Import here to avoid circular imports
        from utils.security_manager import validate_and_load_config
        
        logger.info("🔒 Loading configuration with security validation...")
        secure_config = validate_and_load_config(CONFIG)
        logger.info("✅ Secure configuration loaded successfully")
        return secure_config
        
    except ImportError:
        logger.warning("⚠️ Security manager not available, using basic configuration")
        return CONFIG
    except Exception as e:
        logger.error(f"❌ Security validation failed: {e}")
        raise

# For backward compatibility, expose both configurations
SECURE_CONFIG = None

def get_config(secure: bool = True):
    """Get configuration with optional security validation"""
    global SECURE_CONFIG
    
    if secure:
        if SECURE_CONFIG is None:
            SECURE_CONFIG = get_secure_config()
        return SECURE_CONFIG
    else:
        return CONFIG
