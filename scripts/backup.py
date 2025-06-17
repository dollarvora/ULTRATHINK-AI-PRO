#!/usr/bin/env python3
"""
Backup script for ULTRATHINK
Creates backups of output data and configuration
"""

import os
import shutil
import tarfile
from datetime import datetime
from pathlib import Path
import json


def create_backup():
    """Create a backup of important data"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"ultrathink_backup_{timestamp}"
    backup_dir = Path('backups')
    backup_dir.mkdir(exist_ok=True)
    
    # Create temporary directory
    temp_dir = backup_dir / backup_name
    temp_dir.mkdir()
    
    # Files and directories to backup
    items_to_backup = [
        ('config', 'config'),
        ('output', 'output'),
        ('logs', 'logs'),
        ('.env', '.env')
    ]
    
    backup_manifest = {
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'items': []
    }
    
    for source, dest in items_to_backup:
        source_path = Path(source)
        if source_path.exists():
            dest_path = temp_dir / dest
            
            if source_path.is_dir():
                shutil.copytree(source_path, dest_path)
                file_count = len(list(dest_path.rglob('*')))
                backup_manifest['items'].append({
                    'type': 'directory',
                    'path': dest,
                    'files': file_count
                })
            else:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, dest_path)
                backup_manifest['items'].append({
                    'type': 'file',
                    'path': dest,
                    'size': source_path.stat().st_size
                })
            
            print(f"✓ Backed up {source}")
    
    # Save manifest
    with open(temp_dir / 'manifest.json', 'w') as f:
        json.dump(backup_manifest, f, indent=2)
    
    # Create tarball
    tarball_path = backup_dir / f"{backup_name}.tar.gz"
    with tarfile.open(tarball_path, 'w:gz') as tar:
        tar.add(temp_dir, arcname=backup_name)
    
    # Remove temporary directory
    shutil.rmtree(temp_dir)
    
    # Get backup size
    backup_size = tarball_path.stat().st_size / 1024 / 1024  # MB
    
    print(f"\n✓ Backup created: {tarball_path}")
    print(f"  Size: {backup_size:.1f} MB")
    print(f"  Items: {len(backup_manifest['items'])}")
    
    # Clean old backups (keep last 10)
    cleanup_old_backups(backup_dir)
    
    return tarball_path


def cleanup_old_backups(backup_dir: Path, keep_count: int = 10):
    """Remove old backup files"""
    backups = sorted(
        backup_dir.glob('ultrathink_backup_*.tar.gz'),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    if len(backups) > keep_count:
        for old_backup in backups[keep_count:]:
            old_backup.unlink()
            print(f"  Removed old backup: {old_backup.name}")


def restore_backup(backup_file: str):
    """Restore from a backup file"""
    backup_path = Path(backup_file)
    
    if not backup_path.exists():
        print(f"Error: Backup file not found: {backup_file}")
        return False
    
    print(f"Restoring from: {backup_path}")
    
    # Create restore directory
    restore_dir = Path('restore_temp')
    restore_dir.mkdir(exist_ok=True)
    
    try:
        # Extract backup
        with tarfile.open(backup_path, 'r:gz') as tar:
            tar.extractall(restore_dir)
        
        # Find extracted directory
        extracted = list(restore_dir.iterdir())[0]
        
        # Read manifest
        with open(extracted / 'manifest.json', 'r') as f:
            manifest = json.load(f)
        
        print(f"\nBackup info:")
        print(f"  Created: {manifest['timestamp']}")
        print(f"  Items: {len(manifest['items'])}")
        
        # Confirm restore
        response = input("\nContinue with restore? This will overwrite current data! (y/N): ")
        if response.lower() != 'y':
            print("Restore cancelled")
            return False
        
        # Restore items
        for item in manifest['items']:
            source = extracted / item['path']
            dest = Path(item['path'])
            
            if dest.exists():
                if dest.is_dir():
                    shutil.rmtree(dest)
                else:
                    dest.unlink()
            
            if source.is_dir():
                shutil.copytree(source, dest)
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
            
            print(f"✓ Restored {item['path']}")
        
        print("\n✓ Restore complete!")
        return True
        
    finally:
        # Clean up
        if restore_dir.exists():
            shutil.rmtree(restore_dir)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='ULTRATHINK Backup Tool')
    parser.add_argument('--restore', help='Restore from backup file')
    
    args = parser.parse_args()
    
    if args.restore:
        restore_backup(args.restore)
    else:
        create_backup()