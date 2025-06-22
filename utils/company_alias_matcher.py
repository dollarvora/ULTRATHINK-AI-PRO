"""
Company Alias Matcher for ULTRATHINK
Provides intelligent vendor/manufacturer/distributor matching with extensive alias support
"""

import re
import logging
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict, Counter
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AliasMatchResult:
    """Result of alias matching operation"""
    matched_companies: Set[str]
    alias_hits: Dict[str, List[str]]  # company -> list of aliases that matched
    total_matches: int
    confidence_score: float


class CompanyAliasMatcher:
    """Advanced company alias matching system for ULTRATHINK"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.company_mappings = self._get_expanded_company_mappings()
        self.reverse_mappings = self._build_reverse_mappings()
        self.compiled_patterns = self._compile_regex_patterns()
        
        # Debug tracking
        self.match_stats = defaultdict(int)
        self.alias_hit_counter = Counter()
        
        logger.info(f"✅ Company Alias Matcher initialized with {len(self.company_mappings)} companies")
        logger.info(f"📊 Total aliases: {sum(len(aliases) for aliases in self.company_mappings.values())}")
    
    def _get_expanded_company_mappings(self) -> Dict[str, List[str]]:
        """Expanded company alias mapping covering enterprise IT ecosystem"""
        return {
            # Major Cloud & Software Vendors
            'microsoft': ['msft', 'azure', 'office365', 'teams', 'sharepoint', 'dynamics365', 'm365', 'o365'],
            'google cloud': ['gcp', 'google workspace', 'gsuite', 'bigquery', 'google drive'],
            'aws': ['amazon web services', 'ec2', 's3', 'lambda', 'rds', 'aws cloud'],
            'oracle': ['oracle cloud', 'oci', 'oracle database', 'fusion apps'],
            'sap': ['sap hana', 'sap s4 hana', 'sap ariba', 'sap cloud'],
            'salesforce': ['sfdc', 'sales cloud', 'service cloud', 'marketing cloud'],

            # Hardware & Infrastructure
            'dell': ['emc', 'dell emc', 'poweredge', 'isilon', 'unity', 'vxrail'],
            'hp': ['hewlett packard', 'hp enterprise', 'hpe', 'proliant'],
            'lenovo': ['thinkpad', 'ideapad', 'lenovo servers'],
            'cisco': ['webex', 'meraki', 'umbrella', 'duo', 'anyconnect', 'catalyst'],
            'juniper': ['juniper networks', 'mist', 'qfx'],
            'arista': ['arista switches', 'arista eos'],
            'netapp': ['ontap', 'aff', 'netapp storage'],
            'hpe': ['nimble storage', 'aruba networks', 'synergy', 'greenlake'],

            # Cybersecurity
            'crowdstrike': ['falcon', 'crowdstrike falcon', 'cs falcon'],
            'zscaler': ['zpa', 'zscaler internet access', 'zia'],
            'fortinet': ['fortigate', 'fortianalyzer', 'fortisandbox', 'fortinet security'],
            'palo alto': ['pan-os', 'cortex xdr', 'prisma cloud'],
            'sentinelone': ['singularity xdr', 'sentinel one'],
            'proofpoint': ['email protection', 'threat response'],
            'trend micro': ['deep security', 'cloud one'],
            'mcafee': ['mvision', 'mcafee endpoint'],
            'check point': ['checkpoint', 'sandblast', 'harmony'],

            # SaaS, Productivity, & DevOps
            'vmware': ['vsphere', 'vcenter', 'esxi', 'nsx', 'workspace one'],
            'adobe': ['creative cloud', 'acrobat', 'adobe sign'],
            'citrix': ['citrix workspace', 'virtual apps', 'xenserver'],
            'atlassian': ['jira', 'confluence', 'bitbucket'],
            'slack': ['slack huddles', 'slack enterprise'],
            'zoom': ['zoom meetings', 'zoom phone'],
            'workday': ['workday hcm', 'workday payroll'],
            'servicenow': ['now platform', 'itsm', 'hr service delivery'],
            'symantec': ['endpoint protection', 'symantec cloud'],
            'fireeye': ['mandiant', 'nx series'],

            # Distributors, Resellers & Competitors
            'td synnex': ['tech data', 'synnex'],
            'ingram micro': ['ingram', 'ingramcloud'],
            'arrow electronics': ['arrow', 'arrow cloud'],
            'avnet': ['avnet electronics'],
            'softchoice': ['softchoice corporation'],
            'cdw': ['cdw corporation', 'cdwg'],
            'insight': ['insight global', 'insight enterprises'],
            'computacenter': ['computacenter plc'],
            'shi': ['shi international', 'shi cloud'],
            'zones': ['zones llc']
        }
    
    def _build_reverse_mappings(self) -> Dict[str, str]:
        """Build reverse mapping from alias to main company name"""
        reverse = {}
        for company, aliases in self.company_mappings.items():
            # Map company name to itself
            reverse[company.lower()] = company
            
            # Map each alias to the main company
            for alias in aliases:
                reverse[alias.lower()] = company
        
        return reverse
    
    def _compile_regex_patterns(self) -> Dict[str, Any]:
        """Compile regex patterns for efficient matching"""
        patterns = {}
        
        for company, aliases in self.company_mappings.items():
            # Create pattern that matches company name or any alias
            all_terms = [company] + aliases
            
            # Escape special regex characters and create word boundary patterns
            escaped_terms = [re.escape(term) for term in all_terms]
            pattern_str = r'\b(?:' + '|'.join(escaped_terms) + r')\b'
            
            patterns[company] = re.compile(pattern_str, re.IGNORECASE)
        
        return patterns
    
    def find_companies_in_text(self, text: str, min_confidence: float = 0.5) -> AliasMatchResult:
        """Find all companies mentioned in text using alias matching"""
        if not text:
            return AliasMatchResult(set(), {}, 0, 0.0)
        
        text_lower = text.lower()
        matched_companies = set()
        alias_hits = defaultdict(list)
        total_matches = 0
        
        # Check each company pattern
        for company, pattern in self.compiled_patterns.items():
            matches = pattern.findall(text)
            
            if matches:
                matched_companies.add(company)
                total_matches += len(matches)
                
                # Track which specific aliases matched
                for match in matches:
                    alias_hits[company].append(match)
                    self.alias_hit_counter[f"{company}:{match.lower()}"] += 1
                
                self.match_stats[company] += len(matches)
        
        # Calculate confidence based on match density and uniqueness
        word_count = len(text.split())
        match_density = total_matches / max(word_count, 1)
        uniqueness_score = len(matched_companies) / max(len(self.company_mappings), 1)
        confidence_score = min(1.0, (match_density * 2) + (uniqueness_score * 0.5))
        
        if self.debug and matched_companies:
            logger.debug(f"🎯 Found companies in text: {matched_companies}")
            logger.debug(f"📊 Alias hits: {dict(alias_hits)}")
        
        return AliasMatchResult(
            matched_companies=matched_companies,
            alias_hits=dict(alias_hits),
            total_matches=total_matches,
            confidence_score=confidence_score
        )
    
    def normalize_company_name(self, company_input: str) -> Optional[str]:
        """Normalize a company name or alias to the standard form"""
        normalized = self.reverse_mappings.get(company_input.lower())
        if self.debug and normalized:
            logger.debug(f"🔄 Normalized '{company_input}' → '{normalized}'")
        return normalized
    
    def get_all_aliases_for_company(self, company: str) -> List[str]:
        """Get all aliases for a given company"""
        normalized = self.normalize_company_name(company)
        if normalized:
            return self.company_mappings.get(normalized, [])
        return []
    
    def expand_keyword_list(self, keywords: List[str]) -> List[str]:
        """Expand a keyword list to include all relevant aliases"""
        expanded = set(keywords)  # Start with original keywords
        
        for keyword in keywords:
            # Check if this keyword is a company or alias
            normalized = self.normalize_company_name(keyword)
            if normalized:
                # Add all aliases for this company
                aliases = self.company_mappings.get(normalized, [])
                expanded.update(aliases)
                expanded.add(normalized)  # Ensure main name is included
        
        expanded_list = list(expanded)
        
        if self.debug:
            original_count = len(keywords)
            expanded_count = len(expanded_list)
            logger.debug(f"📈 Expanded keywords: {original_count} → {expanded_count}")
        
        return expanded_list
    
    def get_company_relevance_score(self, text: str, target_companies: List[str]) -> Dict[str, float]:
        """Calculate relevance scores for specific companies in text"""
        result = self.find_companies_in_text(text)
        scores = {}
        
        for company in target_companies:
            normalized = self.normalize_company_name(company)
            if normalized and normalized in result.matched_companies:
                # Base score from number of mentions
                mention_count = len(result.alias_hits.get(normalized, []))
                base_score = min(1.0, mention_count / 3.0)  # Cap at 3 mentions = 1.0
                
                # Boost for exact company name matches vs aliases
                exact_matches = sum(1 for hit in result.alias_hits.get(normalized, []) 
                                   if hit.lower() == normalized.lower())
                exact_boost = exact_matches * 0.2
                
                scores[normalized] = min(1.0, base_score + exact_boost)
            else:
                scores[company] = 0.0
        
        return scores
    
    def get_debug_stats(self) -> Dict[str, any]:
        """Get debugging statistics"""
        return {
            'total_companies': len(self.company_mappings),
            'total_aliases': sum(len(aliases) for aliases in self.company_mappings.values()),
            'match_stats': dict(self.match_stats),
            'top_aliases': self.alias_hit_counter.most_common(20),
            'companies_with_most_matches': sorted(self.match_stats.items(), 
                                                 key=lambda x: x[1], reverse=True)[:10]
        }
    
    def save_debug_report(self, filepath: str) -> None:
        """Save comprehensive debug report"""
        import json
        from datetime import datetime
        
        debug_data = {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.get_debug_stats(),
            'company_mappings': self.company_mappings,
            'performance_metrics': {
                'regex_patterns_compiled': len(self.compiled_patterns),
                'reverse_mappings_created': len(self.reverse_mappings)
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(debug_data, f, indent=2)
        
        logger.info(f"📄 Debug report saved to: {filepath}")


# Global instance for easy access
_global_matcher = None

def get_company_matcher(debug: bool = False) -> CompanyAliasMatcher:
    """Get global company matcher instance"""
    global _global_matcher
    if _global_matcher is None:
        _global_matcher = CompanyAliasMatcher(debug=debug)
    return _global_matcher


# Convenience functions
def find_companies_in_text(text: str, debug: bool = False) -> AliasMatchResult:
    """Convenience function to find companies in text"""
    matcher = get_company_matcher(debug=debug)
    return matcher.find_companies_in_text(text)


def normalize_company_name(company: str, debug: bool = False) -> Optional[str]:
    """Convenience function to normalize company name"""
    matcher = get_company_matcher(debug=debug)
    return matcher.normalize_company_name(company)


def expand_company_keywords(keywords: List[str], debug: bool = False) -> List[str]:
    """Convenience function to expand keyword list with company aliases"""
    matcher = get_company_matcher(debug=debug)
    return matcher.expand_keyword_list(keywords)