#!/usr/bin/env python3
import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def get_commit_info():
    try:
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%H|%s|%an|%ad'],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT)
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split('|')
            if len(parts) >= 4:
                return {
                    'hash': parts[0],
                    'short_hash': parts[0][:8],
                    'subject': parts[1],
                    'author': parts[2],
                    'date': parts[3]
                }
    except Exception as e:
        print(f"Error: {e}")
    return None

def main():
    print(f"Test update... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    info = get_commit_info()
    if info:
        print(f"Commit: {info['short_hash']} - {info['subject']}")
        print("SUCCESS")
        return 0
    else:
        print("FAILURE")
        return 1

if __name__ == "__main__":
    sys.exit(main())
