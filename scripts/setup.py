#!/usr/bin/env python3
"""
Setup script for ULTRATHINK
Initializes the system and creates necessary directories
"""

import os
import sys
import shutil
from pathlib import Path
import subprocess


def setup_directories():
    """Create necessary directories"""
    dirs = [
        'logs',
        'output', 
        'cache',
        'cache/playwright',
        'previews',
        'test_data',
        'config'
    ]
    
    for dir_name in dirs:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created {dir_name}/")
    
    # Create .gitkeep files
    for dir_name in ['logs', 'output', 'cache', 'previews']:
        gitkeep = Path(dir_name) / '.gitkeep'
        gitkeep.touch()


def setup_config():
    """Setup configuration files"""
    # Copy example env if not exists
    if not Path('.env').exists() and Path('config/.env.example').exists():
        shutil.copy('config/.env.example', '.env')
        print("✓ Created .env from example")
        print("  ⚠️  Please edit .env with your API keys!")
    
    # Check for config.json
    if not Path('config/config.json').exists():
        print("✗ config/config.json not found!")
        return False
    
    # Check for employees.csv
    if not Path('config/employees.csv').exists():
        print("⚠️  config/employees.csv not found - creating example")
        with open('config/employees.csv', 'w') as f:
            f.write("name,email,role,active,keywords\n")
            f.write('Test User,test@example.com,pricing_analyst,false,"test"\n')
    
    return True


def install_playwright():
    """Install Playwright browsers"""
    print("\nInstalling Playwright browsers...")
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True
        )
        print("✓ Playwright browsers installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install Playwright: {e}")
        return False


def check_dependencies():
    """Check if all Python dependencies are installed"""
    print("\nChecking Python dependencies...")
    
    try:
        import praw
        import snscrape
        import playwright
        import openai
        import pandas
        print("✓ All core dependencies installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("  Run: pip install -r requirements.txt")
        return False


def main():
    """Main setup function"""
    print("ULTRATHINK Setup Script")
    print("======================\n")
    
    # Setup directories
    print("Setting up directories...")
    setup_directories()
    
    # Setup config
    print("\nSetting up configuration...")
    if not setup_config():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Install Playwright
    install_playwright()
    
    print("\n✓ Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env with your API keys")
    print("2. Update config/employees.csv with your team")
    print("3. Run: python manage.py validate")
    print("4. Test: python run.py --test --once")


if __name__ == '__main__':
    main()