#!/usr/bin/env python3
"""
Cron-friendly wrapper script for schedule scraper.
Runs without any user interaction and logs all output.

Usage:
  # Full scrape + sync
  python cron_run.py

  # Scrape only, no calendar sync
  python cron_run.py --no-sync

  # Sync only (use existing events.json)
  python cron_run.py --sync-only

Exit codes:
  0 - Success
  1 - Error occurred
"""

import sys
import os

# Change to script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Import and run main
try:
    import main
except Exception as e:
    print(f"FATAL ERROR: {e}", file=sys.stderr)
    sys.exit(1)

