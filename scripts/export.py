#!/usr/bin/env python3
"""
Export script for ULTRATHINK
Exports data in various formats for analysis
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import argparse
from typing import List, Dict, Any


def load_outputs(days: int = 7) -> List[Dict[str, Any]]:
    """Load output files from the last N days"""
    output_dir = Path('output')
    cutoff_date = datetime.now() - timedelta(days=days)
    
    outputs = []
    
    for file in sorted(output_dir.glob('ultrathink_*.json'), reverse=True):
        # Check file date
        file_date = datetime.fromtimestamp(file.stat().st_mtime)
        if file_date < cutoff_date:
            break
        
        # Load file
        with open(file, 'r') as f:
            data = json.load(f)
            data['filename'] = file.name
            data['file_date'] = file_date.isoformat()
            outputs.append(data)
    
    return outputs


def export_to_csv(outputs: List[Dict[str, Any]], output_file: str):
    """Export data to CSV format"""
    all_items = []
    
    for output in outputs:
        file_date = output['file_date']
        
        # Extract items from each source
        for source, items in output['content'].items():
            if source == 'timestamp':
                continue
            
            for item in items:
                # Flatten item data
                flat_item = {
                    'file_date': file_date,
                    'source': source,
                    'id': item.get('id'),
                    'title': item.get('title', item.get('text', '')[:100]),
                    'url': item.get('url'),
                    'author': item.get('author', item.get('company')),
                    'created_at': item.get('created_at'),
                    'relevance_score': item.get('relevance_score'),
                    'urgency': item.get('urgency')
                }
                
                # Add source-specific fields
                if source == 'reddit':
                    flat_item['subreddit'] = item.get('subreddit')
                    flat_item['score'] = item.get('score')
                elif source == 'twitter':
                    flat_item['retweets'] = item.get('retweet_count')
                    flat_item['likes'] = item.get('like_count')
                elif source == 'linkedin':
                    flat_item['company'] = item.get('company')
                    flat_item['reactions'] = item.get('reactions')
                
                all_items.append(flat_item)
    
    # Create DataFrame
    df = pd.DataFrame(all_items)
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"✓ Exported {len(all_items)} items to {output_file}")


def export_summaries(outputs: List[Dict[str, Any]], output_file: str):
    """Export AI summaries to markdown"""
    with open(output_file, 'w') as f:
        f.write("# ULTRATHINK Pricing Intelligence Summaries\n\n")
        
        for output in outputs:
            file_date = datetime.fromisoformat(output['file_date'])
            f.write(f"## {file_date.strftime('%B %d, %Y')}\n\n")
            
            if 'summaries' in output and 'role_summaries' in output['summaries']:
                for role_key, summary in output['summaries']['role_summaries'].items():
                    f.write(f"### {summary['role']}\n\n")
                    f.write(f"**Focus:** {summary['focus']}\n\n")
                    f.write(f"{summary['summary']}\n\n")
                    
                    if summary.get('key_insights'):
                        f.write("**Key Insights:**\n")
                        for insight in summary['key_insights']:
                            f.write(f"- {insight}\n")
                        f.write("\n")
                    
                    if summary.get('top_vendors'):
                        f.write("**Top Vendors:**\n")
                        for vendor in summary['top_vendors'][:5]:
                            f.write(f"- {vendor['vendor']}: {vendor['mentions']} mentions\n")
                        f.write("\n")
                    
                    f.write("---\n\n")
    
    print(f"✓ Exported summaries to {output_file}")


def export_metrics(outputs: List[Dict[str, Any]], output_file: str):
    """Export metrics and statistics"""
    metrics = {
        'period': {
            'start': min(o['file_date'] for o in outputs),
            'end': max(o['file_date'] for o in outputs),
            'days': len(outputs)
        },
        'totals': {
            'items_analyzed': 0,
            'high_priority': 0,
            'medium_priority': 0,
            'low_priority': 0
        },
        'by_source': {},
        'top_vendors': {},
        'daily_counts': []
    }
    
    vendor_mentions = {}
    
    for output in outputs:
        daily_count = {
            'date': output['file_date'],
            'total': 0,
            'by_source': {}
        }
        
        # Count items by source
        for source, items in output['content'].items():
            if source == 'timestamp':
                continue
            
            count = len(items)
            daily_count['by_source'][source] = count
            daily_count['total'] += count
            
            # Update source totals
            if source not in metrics['by_source']:
                metrics['by_source'][source] = 0
            metrics['by_source'][source] += count
            
            # Count urgency levels
            for item in items:
                urgency = item.get('urgency', 'low')
                metrics['totals'][f"{urgency}_priority"] += 1
                metrics['totals']['items_analyzed'] += 1
        
        metrics['daily_counts'].append(daily_count)
        
        # Count vendor mentions from summaries
        if 'summaries' in output:
            for role_summary in output['summaries'].get('role_summaries', {}).values():
                for vendor_data in role_summary.get('top_vendors', []):
                    vendor = vendor_data['vendor']
                    if vendor not in vendor_mentions:
                        vendor_mentions[vendor] = 0
                    vendor_mentions[vendor] += vendor_data['mentions']
    
    # Get top vendors
    metrics['top_vendors'] = dict(
        sorted(vendor_mentions.items(), key=lambda x: x[1], reverse=True)[:10]
    )
    
    # Save metrics
    with open(output_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"✓ Exported metrics to {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Export ULTRATHINK data')
    parser.add_argument('--days', type=int, default=7, help='Number of days to export')
    parser.add_argument('--format', choices=['csv', 'markdown', 'metrics', 'all'], 
                       default='all', help='Export format')
    parser.add_argument('--output-dir', default='exports', help='Output directory')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Load data
    print(f"Loading outputs from last {args.days} days...")
    outputs = load_outputs(args.days)
    
    if not outputs:
        print("No output files found!")
        return
    
    print(f"Found {len(outputs)} output files")
    
    # Export based on format
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if args.format in ['csv', 'all']:
        csv_file = output_dir / f"ultrathink_items_{timestamp}.csv"
        export_to_csv(outputs, csv_file)
    
    if args.format in ['markdown', 'all']:
        md_file = output_dir / f"ultrathink_summaries_{timestamp}.md"
        export_summaries(outputs, md_file)
    
    if args.format in ['metrics', 'all']:
        metrics_file = output_dir / f"ultrathink_metrics_{timestamp}.json"
        export_metrics(outputs, metrics_file)
    
    print(f"\n✓ Export complete! Files saved to {output_dir}/")


if __name__ == '__main__':
    main()