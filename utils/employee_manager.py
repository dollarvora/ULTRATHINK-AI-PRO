"""
Enhanced Employee Manager for ULTRATHINK
Handles weighted keyword consolidation and role-specific intelligence
"""

import csv
import logging
from typing import Dict, List, Set, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from collections import defaultdict

from .company_alias_matcher import get_company_matcher
from config.utils import is_valid_email

logger = logging.getLogger(__name__)


@dataclass
class Employee:
    """Enhanced employee data structure"""
    name: str
    email: str
    role: str
    vendors: List[str]
    manufacturers: List[str]
    distributors: List[str]
    topics: List[str]
    active: bool
    combined_keywords: List[str]  # Weighted & deduplicated
    role_weight: float = 1.0


@dataclass
class ConsolidatedKeywords:
    """Result of keyword consolidation across all employees"""
    all_keywords: Set[str]
    weighted_keywords: Dict[str, float]
    role_distribution: Dict[str, List[str]]
    expansion_stats: Dict[str, int]


class EmployeeManager:
    """Advanced employee management with intelligent keyword consolidation"""
    
    def __init__(self, csv_path: str, debug: bool = False):
        self.csv_path = Path(csv_path)
        self.debug = debug
        self.company_matcher = get_company_matcher(debug=debug)
        
        # Keyword weighting system
        self.keyword_weights = {
            'topics': 1.0,        # Highest priority - job function focus
            'vendors': 0.9,       # High priority - direct relationships  
            'manufacturers': 0.7, # Medium priority - product focus
            'distributors': 0.6   # Lower priority - channel relationships
        }
        
        # Role-specific configurations
        self.role_contexts = {
            'pricing_analyst': {
                'focus': 'margin impacts, pricing elasticity, competitive pricing',
                'output_style': 'quantitative insights with specific percentages',
                'key_metrics': ['margin_impact', 'price_change_percentage', 'discount_depth'],
                'priority_categories': ['vendors', 'topics', 'distributors']
            },
            'procurement_manager': {
                'focus': 'vendor relationships, contract optimization, compliance',
                'output_style': 'actionable procurement recommendations',
                'key_metrics': ['cost_savings_opportunity', 'vendor_risk', 'contract_terms'],
                'priority_categories': ['vendors', 'manufacturers', 'topics']
            },
            'bi_strategy': {
                'focus': 'market trends, competitive positioning, revenue forecasting',
                'output_style': 'strategic insights with trend analysis',
                'key_metrics': ['market_share_shift', 'trend_direction', 'forecast_variance'],
                'priority_categories': ['topics', 'vendors', 'manufacturers']
            },
            'default': {
                'focus': 'general business intelligence and market awareness',
                'output_style': 'balanced insights with actionable recommendations',
                'key_metrics': ['business_impact', 'relevance_score', 'urgency_level'],
                'priority_categories': ['topics', 'vendors']
            }
        }
        
        self.employees = []
        self.consolidated_keywords = None
        self._load_employees()
    
    def _load_employees(self) -> None:
        """Load and process employee data from CSV"""
        try:
            if not self.csv_path.exists():
                logger.error(f"❌ Employee CSV not found: {self.csv_path}")
                return
            
            with open(self.csv_path, 'r') as f:
                reader = csv.DictReader(f)
                
                # Validate CSV schema
                required_fields = ['name', 'email', 'role', 'vendors', 'manufacturers', 'distributors', 'topics', 'active']
                if not all(field in reader.fieldnames for field in required_fields):
                    missing = [f for f in required_fields if f not in reader.fieldnames]
                    logger.error(f"❌ Missing CSV fields: {missing}")
                    return
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        employee = self._process_employee_row(row, row_num)
                        if employee:
                            self.employees.append(employee)
                    except Exception as e:
                        logger.warning(f"⚠️  Skipping employee row {row_num}: {e}")
            
            logger.info(f"✅ Loaded {len(self.employees)} active employees")
            
            # Consolidate keywords across all employees
            self.consolidated_keywords = self._consolidate_all_keywords()
            
        except Exception as e:
            logger.error(f"❌ Failed to load employees: {e}")
    
    def _process_employee_row(self, row: Dict[str, str], row_num: int) -> Optional[Employee]:
        """Process a single employee row with validation and enhancement"""
        # Check if employee is active
        if row.get('active', '').lower() != 'true':
            if self.debug:
                logger.debug(f"Skipping inactive employee: {row.get('name', 'Unknown')}")
            return None
        
        # Validate email
        email = row.get('email', '').strip()
        if not is_valid_email(email):
            logger.warning(f"Invalid email for {row.get('name', 'Unknown')}: {email}")
            return None
        
        # Parse keyword fields
        vendors = self._parse_keyword_field(row.get('vendors', ''))
        manufacturers = self._parse_keyword_field(row.get('manufacturers', ''))
        distributors = self._parse_keyword_field(row.get('distributors', ''))
        topics = self._parse_keyword_field(row.get('topics', ''))
        
        # Generate combined keywords with weighting
        combined_keywords = self._generate_weighted_keywords(
            vendors, manufacturers, distributors, topics
        )
        
        # Create employee object
        employee = Employee(
            name=row.get('name', '').strip(),
            email=email,
            role=row.get('role', '').strip(),
            vendors=vendors,
            manufacturers=manufacturers,
            distributors=distributors,
            topics=topics,
            active=True,
            combined_keywords=combined_keywords
        )
        
        if self.debug:
            logger.debug(f"👤 Processed employee: {employee.name} ({employee.role})")
            logger.debug(f"   Keywords: {len(combined_keywords)} total")
        
        return employee
    
    def _parse_keyword_field(self, field_value: str) -> List[str]:
        """Parse comma-separated keyword field with smart cleaning"""
        if not field_value:
            return []
        
        # Remove quotes and split on commas
        clean_value = field_value.strip().strip('"\'')
        keywords = [kw.strip().lower() for kw in clean_value.split(',') if kw.strip()]
        
        # Normalize company names using alias matcher
        normalized_keywords = []
        for keyword in keywords:
            normalized = self.company_matcher.normalize_company_name(keyword)
            if normalized:
                normalized_keywords.append(normalized)
            else:
                normalized_keywords.append(keyword)
        
        return normalized_keywords
    
    def _generate_weighted_keywords(self, vendors: List[str], manufacturers: List[str], 
                                   distributors: List[str], topics: List[str]) -> List[str]:
        """Generate weighted and expanded keyword list"""
        keyword_categories = {
            'topics': topics,
            'vendors': vendors, 
            'manufacturers': manufacturers,
            'distributors': distributors
        }
        
        # Build weighted keyword set
        weighted_keywords = {}
        
        for category, keywords in keyword_categories.items():
            weight = self.keyword_weights.get(category, 0.5)
            
            # Expand keywords with company aliases
            expanded_keywords = self.company_matcher.expand_keyword_list(keywords)
            
            for keyword in expanded_keywords:
                if keyword in weighted_keywords:
                    # Keep highest weight if keyword appears in multiple categories
                    weighted_keywords[keyword] = max(weighted_keywords[keyword], weight)
                else:
                    weighted_keywords[keyword] = weight
        
        # Sort by weight (descending) then alphabetically
        sorted_keywords = sorted(weighted_keywords.items(), 
                               key=lambda x: (-x[1], x[0]))
        
        return [keyword for keyword, weight in sorted_keywords]
    
    def _consolidate_all_keywords(self) -> ConsolidatedKeywords:
        """Consolidate keywords across all employees for unified processing"""
        all_keywords = set()
        weighted_keywords = defaultdict(float)
        role_distribution = defaultdict(list)
        
        # Collect keywords from all employees
        for employee in self.employees:
            for keyword in employee.combined_keywords:
                all_keywords.add(keyword)
                role_distribution[employee.role].append(keyword)
                
                # Track maximum weight across all employees
                # Find weight for this keyword in this employee's categories
                keyword_weight = self._get_keyword_weight_for_employee(keyword, employee)
                weighted_keywords[keyword] = max(weighted_keywords[keyword], keyword_weight)
        
        # Calculate expansion statistics
        original_count = sum(len(emp.vendors) + len(emp.manufacturers) + 
                           len(emp.distributors) + len(emp.topics) 
                           for emp in self.employees)
        expanded_count = len(all_keywords)
        
        expansion_stats = {
            'original_keywords': original_count,
            'expanded_keywords': expanded_count,
            'expansion_ratio': expanded_count / max(original_count, 1),
            'unique_roles': len(set(emp.role for emp in self.employees))
        }
        
        logger.info(f"🔗 Keyword consolidation complete:")
        logger.info(f"   Original: {original_count} → Expanded: {expanded_count}")
        logger.info(f"   Expansion ratio: {expansion_stats['expansion_ratio']:.2f}x")
        
        return ConsolidatedKeywords(
            all_keywords=all_keywords,
            weighted_keywords=dict(weighted_keywords),
            role_distribution=dict(role_distribution),
            expansion_stats=expansion_stats
        )
    
    def _get_keyword_weight_for_employee(self, keyword: str, employee: Employee) -> float:
        """Get the weight of a keyword for a specific employee"""
        # Check which category this keyword belongs to for this employee
        if keyword in employee.topics:
            return self.keyword_weights['topics']
        elif keyword in employee.vendors:
            return self.keyword_weights['vendors']
        elif keyword in employee.manufacturers:
            return self.keyword_weights['manufacturers']
        elif keyword in employee.distributors:
            return self.keyword_weights['distributors']
        else:
            # Keyword was added through alias expansion
            return 0.5  # Default weight for expanded aliases
    
    def get_active_employees(self) -> List[Employee]:
        """Get all active employees"""
        return [emp for emp in self.employees if emp.active]
    
    def get_employees_by_role(self, role: str) -> List[Employee]:
        """Get employees by role"""
        return [emp for emp in self.employees if emp.role == role and emp.active]
    
    def get_all_keywords(self) -> List[str]:
        """Get consolidated keyword list for all employees"""
        if self.consolidated_keywords:
            return list(self.consolidated_keywords.all_keywords)
        return []
    
    def get_weighted_keywords(self) -> Dict[str, float]:
        """Get weighted keyword dictionary"""
        if self.consolidated_keywords:
            return self.consolidated_keywords.weighted_keywords
        return {}
    
    def get_role_context(self, role: str) -> Dict[str, any]:
        """Get role-specific context configuration"""
        return self.role_contexts.get(role, self.role_contexts['default'])
    
    def get_employee_by_email(self, email: str) -> Optional[Employee]:
        """Get employee by email address"""
        return next((emp for emp in self.employees if emp.email == email), None)
    
    def save_debug_report(self, filepath: str) -> None:
        """Save comprehensive debug report"""
        import json
        from datetime import datetime
        
        debug_data = {
            'timestamp': datetime.now().isoformat(),
            'employee_statistics': {
                'total_employees': len(self.employees),
                'active_employees': len(self.get_active_employees()),
                'roles': list(set(emp.role for emp in self.employees)),
                'role_distribution': {
                    role: len(self.get_employees_by_role(role)) 
                    for role in set(emp.role for emp in self.employees)
                }
            },
            'keyword_statistics': self.consolidated_keywords.expansion_stats if self.consolidated_keywords else {},
            'keyword_weights': self.keyword_weights,
            'role_contexts': self.role_contexts,
            'company_alias_stats': self.company_matcher.get_debug_stats() if self.debug else {}
        }
        
        # Add sample employee data (anonymized)
        debug_data['sample_employees'] = [
            {
                'role': emp.role,
                'keyword_count': len(emp.combined_keywords),
                'vendor_count': len(emp.vendors),
                'manufacturer_count': len(emp.manufacturers),
                'distributor_count': len(emp.distributors),
                'topic_count': len(emp.topics)
            }
            for emp in self.employees[:3]  # First 3 employees as samples
        ]
        
        with open(filepath, 'w') as f:
            json.dump(debug_data, f, indent=2)
        
        logger.info(f"📄 Employee debug report saved to: {filepath}")


# Convenience functions for easy access
def load_employee_manager(csv_path: str = "config/employees.csv", debug: bool = False) -> EmployeeManager:
    """Load employee manager instance"""
    return EmployeeManager(csv_path, debug=debug)