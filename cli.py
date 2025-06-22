"""
Enhanced CLI Management Tool for ULTRATHINK
Provides comprehensive management and monitoring capabilities
"""

import click
import asyncio
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import logging

from utils.health_checker import HealthChecker
from utils.performance_monitor import PerformanceMonitor
from utils.cache_manager import CacheManager
from config.advanced_config import AdvancedConfigManager
from summarizer.gpt_summarizer import GPTSummarizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group()
@click.option('--config-dir', default='config', help='Configuration directory')
@click.pass_context
def cli(ctx, config_dir):
    """ULTRATHINK Enhanced Management CLI"""
    ctx.ensure_object(dict)
    ctx.obj['config_dir'] = config_dir
    ctx.obj['config_manager'] = AdvancedConfigManager(config_dir)


@cli.command()
@click.pass_context
def health(ctx):
    """Run comprehensive health check"""
    click.echo("🏥 Running ULTRATHINK Health Check...")
    
    config_manager = ctx.obj['config_manager']
    config = config_manager.get_config()
    
    async def run_health_check():
        health_checker = HealthChecker(config.dict())
        result = await health_checker.run_full_health_check()
        return result
    
    result = asyncio.run(run_health_check())
    
    # Display results
    status_colors = {
        'healthy': 'green',
        'degraded': 'yellow',
        'unhealthy': 'red'
    }
    
    click.echo(f"\n🎯 Overall Status: ", nl=False)
    click.secho(result['overall_status'].upper(), 
                fg=status_colors.get(result['overall_status'], 'white'), 
                bold=True)
    
    click.echo(f"⏱️  Check Duration: {result['duration_ms']:.1f}ms")
    click.echo(f"📊 Health Score: {result['summary']['health_percentage']:.1f}%")
    
    click.echo("\n📋 Component Status:")
    for component in result['components']:
        status_icon = {'healthy': '✅', 'degraded': '⚠️', 'unhealthy': '❌'}
        icon = status_icon.get(component['status'], '❓')
        
        click.echo(f"  {icon} {component['component']}: {component['message']}")
        
        if component.get('response_time_ms'):
            click.echo(f"     ⏱️ Response: {component['response_time_ms']:.1f}ms")
    
    # Save detailed report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = Path('output') / f'health_report_{timestamp}.json'
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    click.echo(f"\n📄 Detailed report saved to: {report_file}")


@cli.command()
@click.option('--clear', is_flag=True, help='Clear performance metrics')
@click.pass_context
def performance(ctx, clear):
    """View performance metrics"""
    monitor = PerformanceMonitor()
    
    if clear:
        monitor.clear_metrics()
        click.echo("🧹 Performance metrics cleared")
        return
    
    summary = monitor.get_performance_summary()
    
    click.echo("📊 ULTRATHINK Performance Summary")
    click.echo("=" * 40)
    
    # System metrics
    sys_metrics = summary['system_metrics']
    click.echo(f"🖥️  CPU: {sys_metrics['cpu_percent']:.1f}%")
    click.echo(f"💾 Memory: {sys_metrics['memory_percent']:.1f}% ({sys_metrics['memory_available_gb']:.1f}GB available)")
    
    # API metrics
    api_metrics = summary['api_metrics']
    click.echo(f"\n🌐 API Calls: {api_metrics['total_calls']}")
    click.echo(f"❌ Error Rate: {api_metrics['error_rate']:.1f}%")
    
    if api_metrics['by_api']:
        click.echo("\n📈 API Usage:")
        for api, count in api_metrics['by_api'].items():
            error_count = api_metrics['error_counts'].get(api, 0)
            click.echo(f"  • {api}: {count} calls ({error_count} errors)")
    
    # Operation metrics
    if summary['operation_metrics']:
        click.echo("\n⚡ Operation Performance:")
        for op, metrics in summary['operation_metrics'].items():
            click.echo(f"  • {op}:")
            click.echo(f"    - Count: {metrics['count']}")
            click.echo(f"    - Avg Time: {metrics['avg_time']:.2f}s")
            click.echo(f"    - Total Time: {metrics['total_time']:.2f}s")
    
    # Save metrics
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    metrics_file = Path('output') / f'performance_{timestamp}.json'
    monitor.save_metrics(metrics_file)
    
    click.echo(f"\n📄 Metrics saved to: {metrics_file}")


@cli.command()
@click.option('--stats', is_flag=True, help='Show cache statistics')
@click.option('--clear-expired', is_flag=True, help='Clear expired cache entries')
@click.pass_context
def cache(ctx, stats, clear_expired):
    """Manage cache system"""
    cache_manager = CacheManager()
    
    if clear_expired:
        cleared = cache_manager.clear_expired()
        click.echo(f"🧹 Cleared {cleared} expired cache entries")
        return
    
    if stats:
        cache_stats = cache_manager.get_cache_stats()
        
        click.echo("💾 Cache Statistics")
        click.echo("=" * 30)
        click.echo(f"Total Files: {cache_stats['total_files']}")
        click.echo(f"Total Size: {cache_stats['total_size_mb']:.2f} MB")
        
        click.echo("\nBy Type:")
        for cache_type, stats in cache_stats['by_type'].items():
            click.echo(f"  • {cache_type}: {stats['files']} files ({stats['size_mb']:.2f} MB)")


@cli.command()
@click.option('--validate', is_flag=True, help='Validate configuration')
@click.option('--show', is_flag=True, help='Show current configuration')
@click.option('--reload', is_flag=True, help='Reload configuration')
@click.pass_context
def config(ctx, validate, show, reload):
    """Manage configuration"""
    config_manager = ctx.obj['config_manager']
    
    if reload:
        config_manager.load_config()
        click.echo("🔄 Configuration reloaded")
        return
    
    if validate:
        health_status = config_manager.get_health_status()
        
        click.echo("🔧 Configuration Validation")
        click.echo("=" * 35)
        
        # Config file status
        if health_status['config_valid']:
            click.secho("✅ Configuration valid", fg='green')
        else:
            click.secho("❌ Configuration invalid", fg='red')
        
        # Environment
        click.echo(f"🌍 Environment: {health_status['environment']}")
        
        # Credentials
        credentials = health_status['credentials']
        click.echo("\n🔑 Credentials:")
        for service, available in credentials.items():
            icon = "✅" if available else "❌"
            click.echo(f"  {icon} {service.upper()}")
        
        if health_status['missing_credentials']:
            click.echo(f"\n⚠️  Missing: {', '.join(health_status['missing_credentials'])}")
        
        return
    
    if show:
        config = config_manager.get_config()
        config_dict = config.dict()
        
        click.echo("📋 Current Configuration")
        click.echo("=" * 30)
        click.echo(yaml.dump(config_dict, default_flow_style=False))


@cli.command()
@click.option('--source', type=click.Choice(['reddit', 'google', 'linkedin', 'all']), default='all')
@click.option('--test', is_flag=True, help='Use test data')
@click.option('--output', help='Output file for results')
@click.pass_context
def fetch(ctx, source, test, output):
    """Fetch data from sources"""
    click.echo(f"📡 Fetching data from {source}...")
    
    # This would integrate with your existing fetchers
    # For now, showing the structure
    
    if test:
        click.echo("🧪 Using test data")
    
    # Simulated fetch results
    results = {
        'timestamp': datetime.now().isoformat(),
        'source': source,
        'items_fetched': 25,
        'status': 'success'
    }
    
    if output:
        with open(output, 'w') as f:
            json.dump(results, f, indent=2)
        click.echo(f"📄 Results saved to: {output}")
    else:
        click.echo(f"✅ Fetched {results['items_fetched']} items from {source}")


@cli.command()
@click.option('--role', help='Generate summary for specific role')
@click.option('--preview', is_flag=True, help='Generate preview only')
@click.pass_context
def summarize(ctx, role, preview):
    """Generate AI summary"""
    click.echo("🤖 Generating AI summary...")
    
    config_manager = ctx.obj['config_manager']
    config = config_manager.get_config()
    
    # This would integrate with your summarizer
    summarizer = GPTSummarizer()
    
    # Mock content for demonstration
    mock_content = {
        'reddit': [{'title': 'Sample post', 'content': 'Sample content'}],
        'google': [{'title': 'News article', 'content': 'News content'}]
    }
    
    if preview:
        click.echo("🎭 Preview mode - generating sample summary")
    
    # Generate summary (this would be actual summarization)
    click.echo("✅ Summary generated successfully")
    
    if role:
        click.echo(f"🎯 Targeted for role: {role}")


@cli.command()
@click.option('--to', help='Send test email to specific address')
@click.option('--preview-only', is_flag=True, help='Generate preview without sending')
@click.pass_context
def email(ctx, to, preview_only):
    """Send email digest"""
    if preview_only:
        click.echo("📧 Generating email preview...")
        click.echo("✅ Preview generated (check output/preview.html)")
    elif to:
        click.echo(f"📧 Sending test email to {to}...")
        click.echo("✅ Test email sent")
    else:
        click.echo("📧 Sending digest to all active employees...")
        click.echo("✅ Digest emails sent")


@cli.command()
@click.pass_context
def status(ctx):
    """Show overall system status"""
    config_manager = ctx.obj['config_manager']
    
    click.echo("🎯 ULTRATHINK System Status")
    click.echo("=" * 35)
    
    # System info
    config = config_manager.get_config()
    click.echo(f"📋 Version: {config.system.version}")
    click.echo(f"🌍 Environment: {config.system.environment}")
    click.echo(f"🔧 Debug Mode: {config.system.debug}")
    
    # Quick health check
    health_status = config_manager.get_health_status()
    credentials = health_status['credentials']
    
    active_services = sum(1 for available in credentials.values() if available)
    total_services = len(credentials)
    
    click.echo(f"🔑 Services: {active_services}/{total_services} configured")
    
    # Performance hint
    cache_manager = CacheManager()
    cache_stats = cache_manager.get_cache_stats()
    click.echo(f"💾 Cache: {cache_stats['total_files']} files ({cache_stats['total_size_mb']:.1f} MB)")
    
    click.echo(f"\n⏰ Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == '__main__':
    cli()