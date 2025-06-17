#!/usr/bin/env python3
"""
ULTRATHINK Management Script
Utility commands for managing the pricing intelligence system
"""

import click
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import sys

import run


@click.group()
def cli():
    """ULTRATHINK Management Commands"""
    pass


@cli.command()
def validate():
    """Validate configuration and credentials"""
    click.echo("Validating ULTRATHINK configuration...")
    
    # Check config file
    config_path = Path('config/config.json')
    if not config_path.exists():
        click.echo(click.style("✗ config/config.json not found", fg='red'))
        return False
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        click.echo(click.style("✓ Configuration file valid", fg='green'))
    except Exception as e:
        click.echo(click.style(f"✗ Configuration error: {e}", fg='red'))
        return False
    
    # Check environment variables
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'REDDIT_CLIENT_ID',
        'REDDIT_CLIENT_SECRET',
        'GOOGLE_API_KEY',
        'GOOGLE_CSE_ID',
        'OPENAI_API_KEY',
        'SMTP_HOST',
        'SMTP_USER',
        'FROM_EMAIL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        click.echo(click.style(f"✗ Missing environment variables: {', '.join(missing_vars)}", fg='red'))
        click.echo("Please check your .env file")
        return False
    else:
        click.echo(click.style("✓ All required environment variables set", fg='green'))
    
    # Check directories
    dirs = ['logs', 'output', 'cache', 'previews', 'test_data']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    click.echo(click.style("✓ Required directories created", fg='green'))
    
    # Check employees.csv
    emp_path = Path('config/employees.csv')
    if emp_path.exists():
        df = pd.read_csv(emp_path)
        active_count = df[df['active'] == True].shape[0]
        click.echo(click.style(f"✓ Employee list loaded: {active_count} active users", fg='green'))
    else:
        click.echo(click.style("⚠ employees.csv not found - using test recipients", fg='yellow'))
    
    click.echo(click.style("\n✓ Validation complete!", fg='green', bold=True))
    return True


@cli.command()
@click.option('--days', default=7, help='Number of days to show')
def stats():
    """Show system statistics and recent runs"""
    click.echo("ULTRATHINK Statistics\n")
    
    # Check recent outputs
    output_dir = Path('output')
    if output_dir.exists():
        files = sorted(output_dir.glob('ultrathink_*.json'), reverse=True)
        
        if files:
            click.echo(f"Recent runs ({len(files)} total):")
            for f in files[:5]:
                # Get file stats
                stat = f.stat()
                size_kb = stat.st_size / 1024
                modified = datetime.fromtimestamp(stat.st_mtime)
                
                click.echo(f"  • {f.name} - {size_kb:.1f}KB - {modified.strftime('%Y-%m-%d %H:%M')}")
        else:
            click.echo("No output files found")
    
    # Check cache
    cache_dir = Path('cache')
    if cache_dir.exists():
        cache_files = list(cache_dir.glob('*'))
        cache_size = sum(f.stat().st_size for f in cache_files if f.is_file()) / 1024 / 1024
        click.echo(f"\nCache: {len(cache_files)} files, {cache_size:.1f}MB total")
    
    # Check logs
    log_dir = Path('logs')
    if log_dir.exists():
        recent_logs = sorted(log_dir.glob('*.log'), reverse=True)[:3]
        if recent_logs:
            click.echo("\nRecent logs:")
            for log in recent_logs:
                click.echo(f"  • {log.name}")


@cli.command()
@click.option('--source', type=click.Choice(['reddit', 'twitter', 'linkedin', 'google', 'all']), default='all')
def test_fetch(source):
    """Test fetch from a specific source"""
    click.echo(f"Testing fetch from {source}...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    import asyncio
    
    async def run_test():
        ultra = UltraThink(test_mode=True)
        
        if source == 'all':
            results = await ultra.fetch_all_content()
            for src, items in results.items():
                if src != 'timestamp':
                    click.echo(f"\n{src.upper()}: {len(items)} items fetched")
        else:
            fetcher = getattr(ultra, f"{source}_fetcher")
            results = await fetcher.fetch()
            click.echo(f"\n{source.upper()}: {len(results)} items fetched")
            
            # Show sample
            if results:
                click.echo("\nSample item:")
                item = results[0]
                click.echo(json.dumps(item, indent=2)[:500] + "...")
    
    asyncio.run(run_test())


@cli.command()
def clean():
    """Clean old cache and output files"""
    click.echo("Cleaning old files...")
    
    cutoff = datetime.now() - timedelta(days=30)
    removed_count = 0
    
    # Clean cache
    cache_dir = Path('cache')
    if cache_dir.exists():
        for f in cache_dir.glob('*'):
            if f.is_file() and datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
                f.unlink()
                removed_count += 1
    
    # Clean old outputs (keep recent 100)
    output_dir = Path('output')
    if output_dir.exists():
        files = sorted(output_dir.glob('ultrathink_*.json'), 
                      key=lambda f: f.stat().st_mtime,
                      reverse=True)
        for f in files[100:]:
            f.unlink()
            removed_count += 1
    
    # Clean old logs (keep recent 30 days)
    log_dir = Path('logs')
    if log_dir.exists():
        for f in log_dir.glob('*.log'):
            if datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
                f.unlink()
                removed_count += 1
    
    click.echo(f"Removed {removed_count} old files")


@cli.command()
@click.argument('email')
@click.option('--role', type=click.Choice(['pricing_analyst', 'procurement_manager', 'bi_strategy']), 
              default='pricing_analyst')
def add_user(email, role):
    """Add a new user to the system"""
    name = click.prompt("Full name")
    keywords = click.prompt("Keywords (comma-separated)", default="")
    
    emp_path = Path('config/employees.csv')
    
    # Read existing
    if emp_path.exists():
        df = pd.read_csv(emp_path)
    else:
        df = pd.DataFrame(columns=['name', 'email', 'role', 'active', 'keywords'])
    
    # Check if exists
    if email in df['email'].values:
        click.echo(click.style(f"User {email} already exists", fg='red'))
        return
    
    # Add new user
    new_user = pd.DataFrame([{
        'name': name,
        'email': email,
        'role': role,
        'active': True,
        'keywords': keywords
    }])
    
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(emp_path, index=False)
    
    click.echo(click.style(f"✓ Added {name} ({email}) as {role}", fg='green'))


@cli.command()
def install_playwright():
    """Install Playwright browsers for LinkedIn scraping"""
    click.echo("Installing Playwright browsers...")
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install"], check=True)
        click.echo(click.style("✓ Playwright browsers installed", fg='green'))
    except subprocess.CalledProcessError as e:
        click.echo(click.style(f"✗ Installation failed: {e}", fg='red'))


if __name__ == '__main__':
    cli()
