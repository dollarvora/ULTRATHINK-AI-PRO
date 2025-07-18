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
    acquisition_mappings: Dict[str, str]  # acquired company -> parent company


class CompanyAliasMatcher:
    """Advanced company alias matching system for ULTRATHINK"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.company_mappings = self._get_expanded_company_mappings()
        self.acquisition_mappings = self._get_acquisition_mappings()
        self.reverse_mappings = self._build_reverse_mappings()
        self.compiled_patterns = self._compile_regex_patterns()
        
        # Debug tracking
        self.match_stats = defaultdict(int)
        self.alias_hit_counter = Counter()
        
        logger.info(f"✅ Company Alias Matcher initialized with {len(self.company_mappings)} companies")
        logger.info(f"📊 Total aliases: {sum(len(aliases) for aliases in self.company_mappings.values())}")
        logger.info(f"🔗 Acquisition mappings: {len(self.acquisition_mappings)} tracked")
    
    def _get_expanded_company_mappings(self) -> Dict[str, List[str]]:
        """Expanded company alias mapping covering enterprise IT ecosystem with 2024-2025 enhancements"""
        return {
            # Major Cloud & Software Vendors
            'microsoft': ['msft', 'azure', 'office365', 'teams', 'sharepoint', 'dynamics365', 'm365', 'o365', 'hyper-v'],
            'google cloud': ['gcp', 'google workspace', 'gsuite', 'bigquery', 'google drive', 'gemini'],
            'aws': ['amazon web services', 'ec2', 's3', 'lambda', 'rds', 'aws cloud', 'amazon bedrock'],
            'oracle': ['oracle cloud', 'oci', 'oracle database', 'fusion apps', 'mysql'],
            'sap': ['sap hana', 'sap s4 hana', 'sap ariba', 'sap cloud', 'concur'],
            'salesforce': ['sfdc', 'sales cloud', 'service cloud', 'marketing cloud', 'tableau', 'slack'],

            # Hardware & Infrastructure  
            'dell': ['emc', 'dell emc', 'poweredge', 'isilon', 'unity', 'vxrail', 'dell technologies'],
            'hp': ['hewlett packard', 'hp enterprise', 'hpe', 'proliant', 'hp inc'],
            'lenovo': ['thinkpad', 'ideapad', 'lenovo servers', 'infinidat'],
            'cisco': ['webex', 'meraki', 'umbrella', 'duo', 'anyconnect', 'catalyst', 'snapattack'],
            'juniper': ['juniper networks', 'mist', 'qfx', 'contrail'],
            'arista': ['arista switches', 'arista eos', 'arista networks'],
            'netapp': ['ontap', 'aff', 'netapp storage', 'cloud volumes'],
            'hpe': ['nimble storage', 'aruba networks', 'synergy', 'greenlake', 'hpe alletra'],

            # Cybersecurity (Enhanced with 2024-2025 acquisitions)
            'crowdstrike': ['falcon', 'crowdstrike falcon', 'cs falcon', 'edr'],
            'zscaler': ['zpa', 'zscaler internet access', 'zia', 'zsuite'],
            'fortinet': ['fortigate', 'fortianalyzer', 'fortisandbox', 'fortinet security', 'fortios'],
            'palo alto': ['pan-os', 'cortex xdr', 'prisma cloud', 'palo alto networks'],
            'sentinelone': ['singularity xdr', 'sentinel one', 'singularity'],
            'proofpoint': ['email protection', 'threat response', 'proofpoint tap'],
            'trend micro': ['deep security', 'cloud one', 'trend vision one'],
            'mcafee': ['mvision', 'mcafee endpoint', 'mcafee enterprise'],
            'check point': ['checkpoint', 'sandblast', 'harmony', 'infinity'],
            'wiz': ['wiz cloud security', 'wiz platform', 'dazz', 'gem security', 'raftt'],
            'sophos': ['sophos intercept x', 'sophos cloud', 'secureworks', 'sophos xdr'],
            'jamf': ['jamf pro', 'jamf now', 'identity automation'],
            'jumpcloud': ['jumpcloud directory', 'vaultone'],
            'hornetsecurity': ['hornetsecurity cloud', 'altospam'],

            # AI & Emerging Technologies (2024-2025 focus)
            'anthropic': ['claude', 'claude ai', 'anthropic ai'],
            'openai': ['chatgpt', 'gpt-4', 'openai api', 'windsurf', 'io'],
            'nvidia': ['cuda', 'tensorrt', 'nvidia ai', 'dgx', 'h100'],
            'coreweave': ['coreweave cloud', 'core scientific'],
            'moveworks': ['moveworks ai', 'moveworks platform'],
            'neural magic': ['neural magic ai', 'deepsparse'],
            'databricks': ['databricks lakehouse', 'mlflow'],
            'snowflake': ['snowflake cloud', 'snowpark'],
            'datadog': ['datadog apm', 'datadog logs'],
            'hashicorp': ['terraform', 'vault', 'consul', 'nomad'],
            'github': ['github actions', 'github copilot', 'github enterprise'],
            'gitlab': ['gitlab ci', 'gitlab runner', 'gitlab ultimate'],
            'docker': ['docker hub', 'docker desktop', 'docker enterprise'],

            # SaaS, Productivity, & DevOps
            'vmware': ['vsphere', 'vcenter', 'esxi', 'nsx', 'workspace one', 'tanzu', 'vsan'],
            'adobe': ['creative cloud', 'acrobat', 'adobe sign', 'adobe experience'],
            'citrix': ['citrix workspace', 'virtual apps', 'xenserver', 'netscaler'],
            'atlassian': ['jira', 'confluence', 'bitbucket', 'trello'],
            'slack': ['slack huddles', 'slack enterprise', 'slack connect'],
            'zoom': ['zoom meetings', 'zoom phone', 'zoom webinar'],
            'workday': ['workday hcm', 'workday payroll', 'workday financials'],
            'servicenow': ['now platform', 'itsm', 'hr service delivery', 'servicenow ai'],
            'symantec': ['endpoint protection', 'symantec cloud', 'broadcom security'],
            'fireeye': ['mandiant', 'nx series', 'mandiant advantage'],
            'okta': ['okta identity', 'okta workforce', 'okta customer'],
            'ping identity': ['pingfederate', 'pingaccess', 'pingone'],
            'splunk': ['splunk enterprise', 'splunk cloud', 'splunk security'],

            # Distributors, Resellers & Competitors
            'td synnex': ['tech data', 'synnex', 'synnex corporation'],
            'ingram micro': ['ingram', 'ingramcloud', 'ingram micro cloud'],
            'arrow electronics': ['arrow', 'arrow cloud', 'arrow ecs'],
            'avnet': ['avnet electronics', 'avnet technology'],
            'softchoice': ['softchoice corporation', 'softchoice inc'],
            'cdw': ['cdw corporation', 'cdwg', 'cdw government'],
            'insight': ['insight global', 'insight enterprises', 'insight direct'],
            'computacenter': ['computacenter plc', 'computacenter inc'],
            'shi': ['shi international', 'shi cloud', 'shi government'],
            'zones': ['zones llc', 'zones inc'],
            'carahsoft': ['carahsoft technology', 'carahsoft solutions'],
            'connection': ['connection inc', 'pc connection'],

            # Storage & Infrastructure
            'pure storage': ['pure flash', 'pure1', 'flasharray'],
            'cohesity': ['cohesity dataplatform', 'cohesity backup'],
            'rubrik': ['rubrik backup', 'rubrik cloud'],
            'veeam': ['veeam backup', 'veeam replication'],
            'commvault': ['commvault complete', 'commvault backup'],
            'nutanix': ['nutanix cloud', 'nutanix hci', 'acropolis'],
            'scale computing': ['scale hc3', 'scale edge'],

            # Telecommunications & Networking
            'broadcom': ['broadcom inc', 'ca technologies', 'vmware acquisition'],
            'marvell': ['marvell technology', 'marvell semiconductors'],
            'qualcomm': ['qualcomm snapdragon', 'qualcomm technologies'],
            'ericsson': ['ericsson cloud', 'ericsson radio'],
            'nokia': ['nokia networks', 'nokia bell labs'],
            'f5': ['f5 networks', 'f5 big-ip', 'nginx'],
            'silver peak': ['silver peak sd-wan', 'aruba sd-wan'],
            'velocloud': ['velocloud sd-wan', 'vmware sd-wan'],

            # Emerging Security & AI Companies
            'vectra': ['vectra ai', 'vectra cognito'],
            'darktrace': ['darktrace ai', 'darktrace immune'],
            'cybereason': ['cybereason defense', 'cybereason ngav'],
            'illumio': ['illumio core', 'illumio edge'],
            'lacework': ['lacework cloud', 'lacework security'],
            'aqua security': ['aqua cloud', 'aqua cspm'],
            'orca security': ['orca cloud', 'orca platform'],
            'sysdig': ['sysdig secure', 'sysdig monitor'],
            'snyk': ['snyk code', 'snyk container'],
            'netskope': ['netskope cloud', 'netskope sse'],
            'trellix': ['trellix security', 'trellix endpoint'],
            'rapid7': ['rapid7 insight', 'metasploit'],
            'tenable': ['tenable io', 'nessus'],
            'qualys': ['qualys cloud', 'qualys vmdr']
        }
    
    def _get_acquisition_mappings(self) -> Dict[str, str]:
        """Track recent acquisitions and M&A activity for better vendor intelligence"""
        return {
            # 2024-2025 Major Acquisitions
            'wiz': 'google cloud',  # Google acquired Wiz for $32B
            'dazz': 'wiz',  # Wiz acquired Dazz for $450M
            'gem security': 'wiz',  # Wiz acquired Gem Security
            'raftt': 'wiz',  # Wiz acquired Raftt for $50M
            'moveworks': 'servicenow',  # ServiceNow acquired Moveworks for $2.85B
            'neural magic': 'red hat',  # Red Hat acquired Neural Magic
            'secureworks': 'sophos',  # Sophos acquired Secureworks for $859M
            'identity automation': 'jamf',  # Jamf acquired Identity Automation for $215M
            'vaultone': 'jumpcloud',  # JumpCloud acquired VaultOne
            'altospam': 'hornetsecurity',  # Hornetsecurity acquired Altospam
            'infinidat': 'lenovo',  # Lenovo acquiring Infinidat for $1.6B
            'snapattack': 'cisco',  # Cisco acquired SnapAttack
            'core scientific': 'coreweave',  # CoreWeave acquired Core Scientific
            'windsurf': 'openai',  # OpenAI acquired Windsurf
            'io': 'openai',  # OpenAI acquired IO
            
            # Established Acquisitions (still relevant)
            'emc': 'dell',  # Dell acquired EMC
            'vmware': 'broadcom',  # Broadcom acquired VMware
            'tech data': 'td synnex',  # TD Synnex acquired Tech Data
            'synnex': 'td synnex',  # Part of TD Synnex merger
            'mandiant': 'google cloud',  # Google acquired Mandiant
            'ca technologies': 'broadcom',  # Broadcom acquired CA Technologies
            'symantec enterprise': 'broadcom',  # Broadcom acquired Symantec Enterprise
            'red hat': 'ibm',  # IBM acquired Red Hat
            'github': 'microsoft',  # Microsoft acquired GitHub
            'linkedin': 'microsoft',  # Microsoft acquired LinkedIn
            'tableau': 'salesforce',  # Salesforce acquired Tableau
            'slack': 'salesforce',  # Salesforce acquired Slack
            'docker': 'mirantis',  # Mirantis acquired Docker Enterprise
            'nginx': 'f5',  # F5 acquired NGINX
            'silver peak': 'hpe',  # HPE acquired Silver Peak
            'velocloud': 'vmware',  # VMware acquired VeloCloud
            'nimble storage': 'hpe',  # HPE acquired Nimble Storage
            'aruba networks': 'hpe',  # HPE acquired Aruba Networks
            'mist': 'juniper',  # Juniper acquired Mist
            'duo': 'cisco',  # Cisco acquired Duo
            'umbrella': 'cisco',  # Cisco acquired Umbrella
            'anyconnect': 'cisco',  # Cisco product
            'webex': 'cisco',  # Cisco acquired WebEx
            'meraki': 'cisco',  # Cisco acquired Meraki
            'workspace one': 'vmware',  # VMware product
            'tanzu': 'vmware',  # VMware Tanzu
            'vsan': 'vmware',  # VMware vSAN
            'fireeye': 'mandiant',  # FireEye became Mandiant
            'mcafee enterprise': 'trellix',  # McAfee Enterprise became Trellix
            'unity': 'dell',  # Dell EMC Unity
            'isilon': 'dell',  # Dell EMC Isilon
            'vxrail': 'dell',  # Dell EMC VxRail
            'poweredge': 'dell',  # Dell PowerEdge
            'proliant': 'hp',  # HP ProLiant
            'greenlake': 'hpe',  # HPE GreenLake
            'synergy': 'hpe',  # HPE Synergy
            'alletra': 'hpe',  # HPE Alletra
        }
    
    def _build_reverse_mappings(self) -> Dict[str, str]:
        """Build reverse mapping from alias to main company name with acquisition intelligence"""
        reverse = {}
        for company, aliases in self.company_mappings.items():
            # Map company name to itself
            reverse[company.lower()] = company
            
            # Map each alias to the main company
            for alias in aliases:
                reverse[alias.lower()] = company
        
        # Add acquisition mappings to reverse lookup
        for acquired, parent in self.acquisition_mappings.items():
            # If the acquired company is not already in company_mappings, add it
            if acquired not in reverse:
                reverse[acquired] = parent
                
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
        """Find all companies mentioned in text using alias matching with enhanced M&A intelligence"""
        if not text:
            return AliasMatchResult(set(), {}, 0, 0.0, {})
        
        text_lower = text.lower()
        matched_companies = set()
        alias_hits = defaultdict(list)
        total_matches = 0
        relevant_acquisitions = {}
        
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
                    
                    # Check if this alias represents an acquisition
                    if match.lower() in self.acquisition_mappings:
                        parent_company = self.acquisition_mappings[match.lower()]
                        relevant_acquisitions[match.lower()] = parent_company
                
                self.match_stats[company] += len(matches)
        
        # Enhanced confidence scoring with multiple factors
        word_count = len(text.split())
        char_count = len(text)
        
        # Factor 1: Match density (how many vendor mentions per word)
        match_density = total_matches / max(word_count, 1)
        
        # Factor 2: Company diversity (how many different companies mentioned)
        diversity_score = len(matched_companies) / max(len(self.company_mappings), 1)
        
        # Factor 3: Text richness (longer text with multiple mentions is more confident)
        text_richness = min(1.0, char_count / 500)  # Normalize to 500 chars
        
        # Factor 4: Acquisition intelligence bonus (M&A mentions boost confidence)
        acquisition_boost = 0.1 if relevant_acquisitions else 0.0
        
        # Factor 5: Specific product/service mentions boost confidence
        specific_terms = ['pricing', 'license', 'cost', 'acquisition', 'merger', 'partnership']
        specificity_boost = 0.1 if any(term in text_lower for term in specific_terms) else 0.0
        
        # Combined confidence score with weighted factors
        base_confidence = min(1.0, (
            match_density * 0.3 +           # 30% weight on match density
            diversity_score * 0.3 +         # 30% weight on company diversity  
            text_richness * 0.2 +           # 20% weight on text richness
            acquisition_boost +             # 10% bonus for M&A intelligence
            specificity_boost               # 10% bonus for specific business terms
        ))
        
        # Apply scaling factor to make scores more realistic for business intelligence
        # Scale from 0.2-1.0 range to 0.4-1.0 range for better practical use
        confidence_score = max(0.2, min(1.0, base_confidence * 1.5))
        
        if self.debug and matched_companies:
            logger.debug(f"🎯 Found companies in text: {matched_companies}")
            logger.debug(f"📊 Alias hits: {dict(alias_hits)}")
            logger.debug(f"🔗 Acquisition mappings: {relevant_acquisitions}")
            logger.debug(f"📈 Confidence components: density={match_density:.2f}, diversity={diversity_score:.2f}, richness={text_richness:.2f}")
        
        return AliasMatchResult(
            matched_companies=matched_companies,
            alias_hits=dict(alias_hits),
            total_matches=total_matches,
            confidence_score=confidence_score,
            acquisition_mappings=relevant_acquisitions
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
    
    def get_acquisition_intelligence(self, text: str) -> Dict[str, Dict[str, str]]:
        """Get acquisition intelligence for companies mentioned in text"""
        result = self.find_companies_in_text(text)
        
        acquisition_intel = {
            'direct_acquisitions': {},  # Companies directly acquired
            'parent_companies': {},     # Parent companies of acquired entities
            'acquisition_chains': {}    # Full acquisition chains
        }
        
        # Process acquisition mappings found in text
        for acquired_company, parent_company in result.acquisition_mappings.items():
            acquisition_intel['direct_acquisitions'][acquired_company] = parent_company
            
            # Check if parent company is also acquired (acquisition chain)
            if parent_company in self.acquisition_mappings:
                ultimate_parent = self.acquisition_mappings[parent_company]
                acquisition_intel['acquisition_chains'][acquired_company] = {
                    'immediate_parent': parent_company,
                    'ultimate_parent': ultimate_parent
                }
            else:
                acquisition_intel['parent_companies'][parent_company] = 'independent'
        
        return acquisition_intel
    
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