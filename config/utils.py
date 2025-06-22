"""
Utility functions for ULTRATHINK configuration management
"""
from typing import List, Dict, Any, Set
import re


def merge_deduplicated_list(existing: List[str], new_items: List[str]) -> List[str]:
    """
    Merge two lists, removing duplicates and sorting alphabetically.
    
    Args:
        existing: Current list of items
        new_items: New items to add
        
    Returns:
        Merged, deduplicated, and sorted list
    """
    # Convert to lowercase for comparison but preserve original case
    seen = {}
    for item in existing + new_items:
        lower_item = item.lower().strip()
        if lower_item not in seen or len(item) > len(seen[lower_item]):
            # Keep the longer version (usually more complete)
            seen[lower_item] = item
    
    return sorted(seen.values(), key=str.lower)


def merge_config_lists(current_config: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge configuration updates into current config, preserving existing values.
    
    Args:
        current_config: Current configuration dictionary
        updates: New configuration values to merge
        
    Returns:
        Merged configuration
    """
    merged = current_config.copy()
    
    for key, value in updates.items():
        if key in merged:
            if isinstance(value, dict) and isinstance(merged[key], dict):
                # Recursively merge dictionaries
                merged[key] = merge_config_lists(merged[key], value)
            elif isinstance(value, list) and isinstance(merged[key], list):
                # Merge lists using deduplication
                merged[key] = merge_deduplicated_list(merged[key], value)
            else:
                # For other types, update only if not None/empty
                if value:
                    merged[key] = value
        else:
            merged[key] = value
    
    return merged


def is_valid_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def extract_vendor_mentions(text: str, vendors: List[str]) -> List[str]:
    """
    Extract vendor mentions from text.
    
    Args:
        text: Text to search
        vendors: List of vendor names to look for
        
    Returns:
        List of found vendor names
    """
    found_vendors = []
    text_lower = text.lower()
    
    for vendor in vendors:
        if vendor.lower() in text_lower:
            found_vendors.append(vendor)
    
    return list(set(found_vendors))


def calculate_relevance_score(content: str, keywords: List[str], vendors: List[str]) -> float:
    """
    Calculate relevance score for content based on keywords and vendors.
    
    Args:
        content: Content to score
        keywords: List of relevant keywords
        vendors: List of relevant vendors
        
    Returns:
        Relevance score (0-10)
    """
    content_lower = content.lower()
    
    # Count keyword matches
    keyword_matches = sum(1 for kw in keywords if kw.lower() in content_lower)
    
    # Count vendor mentions
    vendor_matches = sum(1 for vendor in vendors if vendor.lower() in content_lower)
    
    # Calculate score
    score = (keyword_matches * 1.0) + (vendor_matches * 1.5)
    
    # Normalize to 0-10 scale
    return min(score, 10.0)


def flatten_vendor_list(vendor_dict: Dict[str, List[str]]) -> List[str]:
    """
    Flatten vendor dictionary into a single list.
    
    Args:
        vendor_dict: Dictionary of vendor categories
        
    Returns:
        Flat list of all vendors
    """
    all_vendors = []
    for category, vendors in vendor_dict.items():
        all_vendors.extend(vendors)
    return list(set(all_vendors))