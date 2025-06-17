#!/usr/bin/env python3
"""
Health check script for Docker container
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta


def check_health():
    """Check if the application is healthy"""
    
    # Check if output directory has recent files
    output_dir = Path('/app/output')
    if output_dir.exists():
        latest_file = None
        latest_time = None
        
        for file in output_dir.glob('ultrathink_*.json'):
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            if latest_time is None or mtime > latest_time:
                latest_time = mtime
                latest_file = file
        
        if latest_time:
            # Check if last run was within 25 hours (allowing some buffer)
            if datetime.now() - latest_time < timedelta(hours=25):
                return True, "Healthy: Recent output found"
            else:
                return False, f"Unhealthy: No output since {latest_time}"
    
    return False, "Unhealthy: No output files found"


if __name__ == '__main__':
    healthy, message = check_health()
    print(message)
    sys.exit(0 if healthy else 1)