#!/usr/bin/env python3
"""
Security Manager for ULTRATHINK-AI-PRO
Handles API key validation, input sanitization, and secure configuration
"""

import os
import re
import logging
import hashlib
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger(__name__)

class SecurityError(Exception):
    """Custom security exception"""
    pass

class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, max_calls: int, time_window: int):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def can_make_call(self) -> bool:
        """Check if a call can be made within rate limits"""
        now = time.time()
        # Remove old calls outside the time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        
        return len(self.calls) < self.max_calls
    
    def record_call(self):
        """Record a successful API call"""
        self.calls.append(time.time())

class SecureCredentialManager:
    """Manages secure handling of API credentials"""
    
    def __init__(self, config=None):
        # Load rate limits from config or use defaults
        if config and 'security' in config and 'rate_limits' in config['security']:
            rate_config = config['security']['rate_limits']
        else:
            # Default rate limits if config not available
            rate_config = {
                'openai': {'max_calls': 60, 'time_window': 60},
                'reddit': {'max_calls': 100, 'time_window': 60},
                'google': {'max_calls': 100, 'time_window': 86400},
                'twitter': {'max_calls': 300, 'time_window': 900}
            }
        
        self.rate_limiters = {}
        for service, limits in rate_config.items():
            self.rate_limiters[service] = RateLimiter(
                max_calls=limits['max_calls'], 
                time_window=limits['time_window']
            )
    
    @staticmethod
    def validate_api_key(service: str, api_key: Optional[str], config=None) -> bool:
        """Validate API key format and existence"""
        if not api_key:
            logger.warning(f"🔒 {service} API key is missing")
            return False
        
        # Load validation patterns from config or use defaults
        if config and 'security' in config and 'api_key_patterns' in config['security']:
            validation_patterns = config['security']['api_key_patterns']
        else:
            # Default validation patterns
            validation_patterns = {
                'openai': r'^sk-[a-zA-Z0-9_-]{20,}$',
                'reddit': r'^[a-zA-Z0-9_-]{10,25}$', 
                'google': r'^[a-zA-Z0-9_-]{30,50}$',
                'twitter': r'^[a-zA-Z0-9]{100,}$'
            }
        
        pattern = validation_patterns.get(service)
        if pattern and not re.match(pattern, api_key):
            logger.warning(f"🔒 {service} API key format appears invalid")
            return False
        
        logger.info(f"✅ {service} API key validation passed")
        return True
    
    @staticmethod
    def mask_credential(credential: str, show_chars: int = 4) -> str:
        """Safely mask credentials for logging"""
        if not credential or len(credential) < show_chars * 2:
            return "***MASKED***"
        
        return f"{credential[:show_chars]}***{credential[-show_chars:]}"
    
    def check_rate_limit(self, service: str) -> bool:
        """Check if service is within rate limits"""
        if service not in self.rate_limiters:
            logger.warning(f"🔒 No rate limiter configured for service: {service}")
            return True
        
        can_call = self.rate_limiters[service].can_make_call()
        if not can_call:
            logger.warning(f"🔒 Rate limit exceeded for {service}")
        
        return can_call
    
    def record_api_call(self, service: str):
        """Record an API call for rate limiting"""
        if service in self.rate_limiters:
            self.rate_limiters[service].record_call()

class InputValidator:
    """Validates and sanitizes external inputs"""
    
    def __init__(self, config=None):
        # Load input validation settings from config
        if config and 'security' in config and 'input_validation' in config['security']:
            self.settings = config['security']['input_validation']
        else:
            # Default settings
            self.settings = {
                'max_text_length': 10000,
                'max_prompt_length': 50000,
                'max_title_length': 500,
                'max_query_length': 200,
                'max_log_length': 100,
                'suspicious_domains': ['bit.ly', 'tinyurl.com', 'short.link', 'suspicious.com']
            }
    
    def sanitize_url(self, url: str) -> Optional[str]:
        """Sanitize and validate URLs"""
        if not url:
            return None
        
        # Remove potentially dangerous characters
        url = re.sub(r'[<>"\']', '', url)
        
        # Validate URL format
        url_pattern = r'^https?:\/\/[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}[\/\w\-\._~:/?#[\]@!\$&\'\(\)\*\+,;%=.]*$'
        if not re.match(url_pattern, url):
            logger.warning(f"🔒 Invalid URL format: {self.truncate_for_log(url)}")
            return None
        
        # Block suspicious domains
        suspicious_domains = self.settings.get('suspicious_domains', [])
        
        for domain in suspicious_domains:
            if domain in url.lower():
                logger.warning(f"🔒 Blocked suspicious domain in URL: {domain}")
                return None
        
        return url
    
    def sanitize_text(self, text: str, max_length: int = None) -> str:
        """Sanitize text input"""
        if not text:
            return ""
        
        # Use config max_length or provided max_length or default
        if max_length is None:
            max_length = self.settings.get('max_text_length', 10000)
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length]
            logger.warning(f"🔒 Text truncated to {max_length} characters")
        
        # Remove potentially dangerous patterns
        # Remove script tags
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove SQL injection patterns (more intelligent detection)
        sql_patterns = [
            r'(\bunion\s+select\b)',                    # UNION SELECT attacks
            r'(\bor\s+1\s*=\s*1\b)',                   # OR 1=1 attacks  
            r'(\bselect\s+\*\s+from\s+\w+)',          # SELECT * FROM table
            r'(\bdrop\s+table\s+\w+)',                # DROP TABLE attacks
            r'(\binsert\s+into\s+\w+)',               # INSERT INTO attacks
            r'(\bdelete\s+from\s+\w+)',               # DELETE FROM attacks
            r'(\bexec\s*\(\s*)',                      # EXEC() attacks
            r'(\bxp_cmdshell\b)',                     # SQL Server command execution
            r'(;\s*drop\s+)',                         # ; DROP attacks
            r'(\'\s*;\s*\w+\s*--)',                   # SQL comment attacks
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning("🔒 Potential SQL injection attempt detected and blocked")
                return ""
        
        return text.strip()
    
    def validate_subreddit_name(self, subreddit: str) -> bool:
        """Validate Reddit subreddit name"""
        if not subreddit:
            return False
        
        # Reddit subreddit name pattern: letters, numbers, underscores
        pattern = r'^[a-zA-Z0-9_]{1,21}$'
        return bool(re.match(pattern, subreddit))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format"""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def truncate_for_log(self, text: str, max_length: int = None) -> str:
        """Safely truncate text for logging"""
        if not text:
            return ""
        
        if max_length is None:
            max_length = self.settings.get('max_log_length', 100)
        
        if len(text) <= max_length:
            return text
        
        return f"{text[:max_length]}... (truncated)"

class SecureConfigLoader:
    """Securely load and validate configuration"""
    
    def __init__(self, config=None):
        self.config = config
        self.credential_manager = SecureCredentialManager(config)
        self.validator = InputValidator(config)
    
    def load_secure_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Load configuration with security validation"""
        logger.info("🔒 Loading configuration with security validation...")
        
        validated_config = config.copy()
        
        # Validate credentials section
        if 'credentials' in config:
            validated_config['credentials'] = self._validate_credentials(config['credentials'])
        
        # Validate sources section
        if 'sources' in config:
            validated_config['sources'] = self._validate_sources(config['sources'])
        
        # Validate email section
        if 'email' in config:
            validated_config['email'] = self._validate_email_config(config['email'])
        
        logger.info("✅ Configuration security validation completed")
        return validated_config
    
    def _validate_credentials(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Validate all credential sections"""
        validated = {}
        
        for service, creds in credentials.items():
            validated[service] = {}
            
            if service == 'openai':
                api_key = creds.get('api_key')
                if self.credential_manager.validate_api_key('openai', api_key, self.config):
                    validated[service]['api_key'] = api_key
                    logger.info(f"✅ OpenAI API key: {self.credential_manager.mask_credential(api_key)}")
                else:
                    logger.error("❌ OpenAI API key validation failed")
                    raise SecurityError("Invalid or missing OpenAI API key")
            
            elif service == 'reddit':
                client_id = creds.get('client_id')
                client_secret = creds.get('client_secret')
                user_agent = creds.get('user_agent')
                
                if self.credential_manager.validate_api_key('reddit', client_id, self.config):
                    validated[service]['client_id'] = client_id
                    validated[service]['client_secret'] = client_secret
                    validated[service]['user_agent'] = user_agent
                    logger.info(f"✅ Reddit credentials: {self.credential_manager.mask_credential(client_id)}")
                else:
                    logger.warning("⚠️ Reddit API credentials validation failed")
            
            elif service == 'google':
                api_key = creds.get('api_key')
                cse_id = creds.get('cse_id')
                
                if self.credential_manager.validate_api_key('google', api_key, self.config):
                    validated[service]['api_key'] = api_key
                    validated[service]['cse_id'] = cse_id
                    logger.info(f"✅ Google API key: {self.credential_manager.mask_credential(api_key)}")
                else:
                    logger.warning("⚠️ Google API credentials validation failed")
            
            elif service == 'twitter':
                bearer_token = creds.get('bearer_token')
                if self.credential_manager.validate_api_key('twitter', bearer_token, self.config):
                    validated[service]['bearer_token'] = bearer_token
                    logger.info(f"✅ Twitter credentials: {self.credential_manager.mask_credential(bearer_token)}")
                else:
                    logger.warning("⚠️ Twitter API credentials validation failed")
            
            else:
                # Pass through other services with basic validation
                validated[service] = creds
        
        return validated
    
    def _validate_sources(self, sources: Dict[str, Any]) -> Dict[str, Any]:
        """Validate source configurations"""
        validated = {}
        
        for source, config in sources.items():
            validated[source] = config.copy()
            
            if source == 'reddit' and 'subreddits' in config:
                # Validate subreddit names
                valid_subreddits = []
                for subreddit in config['subreddits']:
                    if self.validator.validate_subreddit_name(subreddit):
                        valid_subreddits.append(subreddit)
                    else:
                        logger.warning(f"🔒 Invalid subreddit name: {subreddit}")
                
                validated[source]['subreddits'] = valid_subreddits
                logger.info(f"✅ Validated {len(valid_subreddits)} Reddit subreddits")
            
            elif source == 'google' and 'queries' in config:
                # Sanitize search queries
                sanitized_queries = []
                for query in config['queries']:
                    sanitized = self.validator.sanitize_text(query, max_length=200)
                    if sanitized:
                        sanitized_queries.append(sanitized)
                
                validated[source]['queries'] = sanitized_queries
                logger.info(f"✅ Sanitized {len(sanitized_queries)} Google search queries")
        
        return validated
    
    def _validate_email_config(self, email_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate email configuration"""
        validated = email_config.copy()
        
        # Validate email addresses
        if 'test_recipients' in email_config:
            valid_emails = []
            for email in email_config['test_recipients']:
                if self.validator.validate_email(email):
                    valid_emails.append(email)
                else:
                    logger.warning(f"🔒 Invalid email address: {email}")
            
            validated['test_recipients'] = valid_emails
            logger.info(f"✅ Validated {len(valid_emails)} email recipients")
        
        return validated

def secure_api_call(service: str):
    """Decorator for secure API calls with rate limiting"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get credential manager instance
            if hasattr(wrapper, '_credential_manager'):
                cred_manager = wrapper._credential_manager
            else:
                cred_manager = SecureCredentialManager()
                wrapper._credential_manager = cred_manager
            
            # Check rate limits
            if not cred_manager.check_rate_limit(service):
                raise SecurityError(f"Rate limit exceeded for {service}")
            
            try:
                # Make the API call
                result = func(*args, **kwargs)
                
                # Record successful call
                cred_manager.record_api_call(service)
                
                return result
                
            except Exception as e:
                logger.error(f"🔒 Secure API call failed for {service}: {str(e)}")
                raise
        
        return wrapper
    return decorator

# Global security manager instance
_security_manager = None

def get_security_manager(config=None) -> SecureConfigLoader:
    """Get global security manager instance"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecureConfigLoader(config)
    return _security_manager

def validate_and_load_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to validate and load secure configuration"""
    security_manager = get_security_manager(config)
    return security_manager.load_secure_config(config)

# Export main classes and functions
__all__ = [
    'SecureCredentialManager',
    'InputValidator', 
    'SecureConfigLoader',
    'SecurityError',
    'secure_api_call',
    'get_security_manager',
    'validate_and_load_config'
]