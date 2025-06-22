
import json
import os
from typing import Dict, Any
from .utils import merge_config_lists
from .config import CONFIG


def load_config() -> Dict[str, Any]:
    """Load configuration from JSON file and merge with defaults."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    
    # Start with default CONFIG
    final_config = CONFIG.copy()
    
    # If config.json exists, merge it
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            json_config = json.load(f)
            final_config = merge_config_lists(final_config, json_config)
    
    return final_config


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to JSON file."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
