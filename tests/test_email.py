"""
Tests for email functionality
"""

import pytest
from pathlib import Path
import pandas as pd

from email.template import EmailTemplate
from email.sender import EmailSender


@pytest.fixture
def test_config():
    """Test configuration"""
    return {
        'email': {
            'enabled': True,
            'subject_template': 'Test Subject - {date}',
            'employee_csv': 'test_employees.csv',
            'test_recipients': ['test@example.com']
        },
        'credentials': {
            'email': {
                'smtp_host': 'localhost',
                'smtp_port': 1025,
                'smtp_user': 'test',
                'smtp_password': 'test',
                'from_email': 'test@example.com'
            }
        }
    }


@pytest.fixture
def sample_summary():
    """Sample summary for testing"""
    return {
        'role': 'Pricing Analyst',
        'focus': 'Direct pricing changes',
        'summary': 'Test summary content',
        'key_insights': ['Insight 1', 'Insight 2'],
        'top_vendors': [
            {'vendor': 'Microsoft', 'mentions': 5},
            {'vendor': 'Dell', 'mentions': 3}
        ],
        'sources': {'reddit': 10, 'twitter': 5}
    }


class TestEmailTemplate:
    """Test email template"""
    
    def test_render_template(self, sample_summary):
        """Test template rendering"""
        template = EmailTemplate()
        
        html = template.render(
            sample_summary,
            {'high': 5, 'medium': 10, 'low': 20},
            35
        )
        
        assert 'Pricing Analyst' in html
        assert 'Test summary content' in html
        assert 'Microsoft' in html
        assert '35' in html  # total items


class TestEmailSender:
    """Test email sender"""
    
    def test_load_employees(self, test_config, tmp_path):
        """Test employee loading"""
        # Create test CSV
        csv_path = tmp_path / 'test_employees.csv'
        df = pd.DataFrame([
            {
                'name': 'Test User',
                'email': 'test@example.com',
                'role': 'pricing_analyst',
                'active': True,
                'keywords': 'microsoft,azure'
            }
        ])
        df.to_csv(csv_path, index=False)
        
        test_config['email']['employee_csv'] = str(csv_path)
        
        sender = EmailSender(test_config)
        assert len(sender.employees) == 1
        assert sender.employees.iloc[0]['email'] == 'test@example.com'
    
    def test_personalize_summary(self, test_config, sample_summary):
        """Test summary personalization"""
        sender = EmailSender(test_config)
        
        employee = {
            'keywords': 'microsoft,azure'
        }
        
        personalized = sender._personalize_summary(sample_summary, employee['keywords'])
        
        # Should highlight Microsoft vendor
        assert any(v.get('highlighted') for v in personalized['top_vendors'] 
                  if v['vendor'] == 'Microsoft')