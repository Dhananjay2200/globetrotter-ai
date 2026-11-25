"""
GlobeTrotter AI - 200 Articles/Day Autonomous Publishing Engine CLI.
Runs the continuous autonomous publisher with live console telemetry,
intelligent worldwide rotation, anti-hallucination research, and auto-publishing.

Usage:
  python run_automation.py                  # Default: 200/day pacing (every 432s / 7.2 mins)
  python run_automation.py --interval 300   # Custom 5-min interval
  python run_automation.py --target 100     # Target 100 articles/day
  python run_automation.py --once           # Execute a single autonomous cycle and exit
"""

import argparse
import sys
import time
from datetime import datetime, timezone
from app.services.scheduler_service import automation_manager
from app.database.session import ensure_database_exists
from app.database.init_db import init_db
from app.utils.logging import logger


def print_banner(interval: int, target: int):
    print("=" * 68)
    print("  🌍  GlobeTrotter AI - Autonomous 200 Articles/Day Publisher  🌍 ")
    print("=" * 68)
    print(f"  [*] Target Production : {target} verified travel articles / 24 hours")
    print(f"  [*] Automated Pacing  : 1 post every {interval}s ({round(interval/60, 2)} minutes)")
    print(f"  [*] Global Scope      : 10 worldwide regions (equal round-robin balance)")
    print(f"  [*] Thematic Depth    : 13 tourism categories (least-covered priority)")
    print(f"  [*] Quality Gate      : Score >= 8.0/10 (11-dimension evaluation rubric)")
    print(f"  [*] Publishing Mode   : Automatic delivery to React website & public feed")
    print("=" * 68)
    print("  Press Ctrl+C to stop the autonomous engine gracefully at any time.")
    print("=" * 68 + "\n")


def main():
    parser = argparse.ArgumentParser(description="GlobeTrotter AI 200 Articles/Day Autonomous Engine")
    parser.add_argument("--interval", type=int, default=432, help="Seconds between runs (default: 432s = 7.2m)")
    parser.add_argument("--target", type=int, default=200, help="Target articles per day (default: 200)")
    parser.add_argument("--once", action="store_true", help="Run a single autonomous cycle and exit")
    args = parser.parse_args()

    # 1. Initialize Database Schema
    ensure_database_exists()
    init_db()

    # 2. Single Run Mode
    if args.once:
        print("[*] Executing single autonomous publishing cycle...")
        result = automation_manager.execute_single_autonomous_iteration()
        if result.get("success"):
            print(f"\n[+] SUCCESS! Published Article ID {result.get('article_id')}:")
            print(f"    Title        : {result.get('title')}")
            print(f"    Destination  : {result.get('destination')}, {result.get('country')}")
            print(f"    Score        : {result.get('quality_score')}/10.0")
            print(f"    Website URL  : {result.get('website_url')}")
            sys.exit(0)
        else:
            print(f"\n[-] Cycle completed with status: {result.get('status')} ({result.get('reason') or result.get('error')})")
            sys.exit(1)

    # 3. Continuous 24/7 Daemon Mode
    print_banner(interval=args.interval, target=args.target)
    automation_manager.start(interval_seconds=args.interval, daily_target=args.target)

    try:
        while True:
            status = automation_manager.get_status()
            today = status["articles_generated_today"]
            target = status["daily_target"]
            pct = status["progress_percent"]
            next_in = status["seconds_until_next_run"]
            successful = status["successful_runs"]
            total = status["total_runs"]

            # Progress bar visualization: [====.......]
            bar_len = 20
            filled = int((pct / 100) * bar_len)
            bar = "#" * filled + "-" * (bar_len - filled)

            status_line = (
                f"\r[*] Progress: [{bar}] {today}/{target} ({pct}%) | "
                f"Runs: {successful}/{total} | "
                f"Next in: {next_in or 0}s   "
            )
            sys.stdout.write(status_line)
            sys.stdout.flush()
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n[*] Ctrl+C received. Gracefully stopping GlobeTrotter AI Autonomous Engine...")
        automation_manager.stop()
        print("[+] Engine stopped cleanly. Have a great day!")
        sys.exit(0)


if __name__ == "__main__":
    main()
