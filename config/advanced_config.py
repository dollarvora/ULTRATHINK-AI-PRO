"""
Advanced Configuration Management for ULTRATHINK
Supports environment-specific configs, validation, and hot reloading
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import logging
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


class SourceConfig(BaseModel):
    """Configuration for a data source"""
    enabled: bool = True
    rate_limit_delay: float = 2.0
    max_retries: int = 3
    timeout_seconds: int = 30
    cache_ttl_hours: int = 24


class RedditConfig(SourceConfig):
    """Reddit-specific configuration"""
    subreddits: List[str] = ["sysadmin", "msp", "cybersecurity"]
    post_limit: int = 50
    comment_limit: int = 20
    min_score: int = 10


class GoogleConfig(SourceConfig):
    """Google Search-specific configuration"""
    queries: List[str] = ["enterprise software pricing"]
    results_per_query: int = 10
    date_restriction: str = "d7"
    trusted_domains: List[str] = ["crn.com", "zdnet.com", "computerworld.com"]


class EmailConfig(BaseModel):
    """Email configuration"""
    enabled: bool = True
    tracking_enabled: bool = True
    tracking_server: str = "https://track.ultrathink.com"
    subject_template: str = "[ULTRATHINK] Pricing Intelligence Digest - {date}"
    employee_csv: str = "config/employees.csv"
    test_recipients: List[str] = []


class SummarizationConfig(BaseModel):
    """AI summarization configuration"""
    model: str = "gpt-4-turbo-preview"
    max_tokens: int = 2000
    temperature: float = 0.3
    few_shot_examples: bool = True
    role_based_prompts: bool = True


class SystemConfig(BaseModel):
    """System-wide configuration"""
    name: str = "ULTRATHINK Pricing Intelligence System"
    version: str = "1.0.2"
    environment: str = "development"
    debug: bool = False
    cache_ttl_hours: int = 24
    log_level: str = "INFO"


class UltraThinkConfig(BaseModel):
    """Main configuration model"""
    system: SystemConfig = SystemConfig()
    sources: Dict[str, SourceConfig] = {
        "reddit": RedditConfig(),
        "google": GoogleConfig()
    }
    email: EmailConfig = EmailConfig()
    summarization: SummarizationConfig = SummarizationConfig()
    
    # Dynamic vendor and keyword lists
    vendors: Dict[str, List[str]] = {
        "hardware": ["Dell", "HPE", "Cisco"],
        "software": ["Microsoft", "Oracle", "SAP"],
        "security": ["CrowdStrike", "Fortinet", "Zscaler"]
    }
    
    keywords: Dict[str, List[str]] = {
        "pricing": ["price increase", "cost increase", "discount"],
        "urgency": ["urgent", "critical", "immediate"]
    }


class AdvancedConfigManager:
    """Advanced configuration manager with validation and hot reloading"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.yaml"
        self.env_config_file = self.config_dir / f"config.{os.getenv('ENVIRONMENT', 'development')}.yaml"
        self.config: Optional[UltraThinkConfig] = None
        self.last_modified = None
        
        self.load_config()
    
    def load_config(self) -> UltraThinkConfig:
        """Load and validate configuration"""
        try:
            # Start with base configuration
            base_config = self._load_config_file(self.config_file)
            
            # Override with environment-specific config if exists
            if self.env_config_file.exists():
                env_config = self._load_config_file(self.env_config_file)
                base_config = self._merge_configs(base_config, env_config)
            
            # Override with environment variables
            base_config = self._apply_env_overrides(base_config)
            
            # Validate configuration
            self.config = UltraThinkConfig(**base_config)
            self.last_modified = max(
                self.config_file.stat().st_mtime if self.config_file.exists() else 0,
                self.env_config_file.stat().st_mtime if self.env_config_file.exists() else 0
            )
            
            logger.info(f"Configuration loaded successfully for environment: {self.config.system.environment}")
            return self.config
            
        except ValidationError as e:
            logger.error(f"Configuration validation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def _load_config_file(self, filepath: Path) -> Dict[str, Any]:
        """Load configuration from YAML or JSON file"""
        if not filepath.exists():
            return {}
        
        with open(filepath, 'r') as f:
            if filepath.suffix.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(f) or {}
            else:
                return json.load(f)
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two configuration dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides"""
        # Map of environment variables to config paths
        env_mappings = {
            'ULTRATHINK_DEBUG': 'system.debug',
            'ULTRATHINK_LOG_LEVEL': 'system.log_level',
            'ULTRATHINK_ENVIRONMENT': 'system.environment',
            'ULTRATHINK_EMAIL_ENABLED': 'email.enabled',
            'ULTRATHINK_TRACKING_ENABLED': 'email.tracking_enabled',
            'ULTRATHINK_MODEL': 'summarization.model',
            'ULTRATHINK_MAX_TOKENS': 'summarization.max_tokens'
        }
        
        for env_var, config_path in env_mappings.items():
            if env_var in os.environ:
                value = os.environ[env_var]
                
                # Convert to appropriate type
                if value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                elif self._is_float(value):
                    value = float(value)
                
                # Set nested configuration value
                self._set_nested_value(config, config_path, value)
        
        return config
    
    def _is_float(self, value: str) -> bool:
        """Check if string can be converted to float"""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def _set_nested_value(self, config: Dict[str, Any], path: str, value: Any) -> None:
        """Set a nested configuration value using dot notation"""
        keys = path.split('.')
        current = config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def reload_if_changed(self) -> bool:
        """Reload configuration if files have been modified"""
        current_modified = max(
            self.config_file.stat().st_mtime if self.config_file.exists() else 0,
            self.env_config_file.stat().st_mtime if self.env_config_file.exists() else 0
        )
        
        if current_modified > self.last_modified:
            logger.info("Configuration files modified, reloading...")
            self.load_config()
            return True
        
        return False
    
    def get_config(self) -> UltraThinkConfig:
        """Get current configuration, reloading if necessary"""
        self.reload_if_changed()
        return self.config
    
    def save_config(self, config: UltraThinkConfig = None) -> None:
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        config_dict = config.dict()
        
        # Save as YAML for better readability
        with open(self.config_file, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        
        logger.info(f"Configuration saved to {self.config_file}")
    
    def validate_credentials(self) -> Dict[str, bool]:
        """Validate that required credentials are available"""
        results = {}
        
        # Check OpenAI
        results['openai'] = bool(os.getenv('OPENAI_API_KEY'))
        
        # Check Reddit
        results['reddit'] = bool(
            os.getenv('REDDIT_CLIENT_ID') and 
            os.getenv('REDDIT_CLIENT_SECRET')
        )
        
        # Check Google
        results['google'] = bool(
            os.getenv('GOOGLE_API_KEY') and 
            os.getenv('GOOGLE_CSE_ID')
        )
        
        # Check Email
        results['email'] = bool(
            os.getenv('SMTP_HOST') and 
            os.getenv('SMTP_USER') and 
            os.getenv('SMTP_PASSWORD')
        )
        
        return results
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get configuration health status"""
        credentials = self.validate_credentials()
        
        return {
            'config_valid': self.config is not None,
            'config_file_exists': self.config_file.exists(),
            'environment': self.config.system.environment if self.config else None,
            'credentials': credentials,
            'missing_credentials': [k for k, v in credentials.items() if not v],
            'last_modified': datetime.fromtimestamp(self.last_modified).isoformat() if self.last_modified else None
        }