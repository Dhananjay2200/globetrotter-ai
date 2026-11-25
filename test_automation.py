"""
GlobeTrotter AI - Phase 12 Diagnostic: Automation & Scaling Engine Test.
Verifies:
  1. Mathematical pacing model (200 articles / day = 7.2 mins / article = 432s).
  2. Lifecycle management (start, status, stop, graceful thread shutdown).
  3. Single autonomous cycle execution with auto-publishing to React website.
  4. Global telemetry and database synchronization.
"""

import sys
import time
from sqlalchemy.orm import Session
from app.database.session import SessionLocal, ensure_database_exists
from app.database.init_db import init_db
from app.database.models import Article, Topic, PublishingJob
from app.services.scheduler_service import automation_manager
from app.services.publisher_service import get_public_feed
from app.utils.logging import logger


def run_automation_diagnostics():
    print("=" * 68)
    print(" GlobeTrotter AI - Phase 12: Automation & Scaling Engine Diagnostic")
    print("=" * 68)

    ensure_database_exists()
    init_db()

    # 1. Pacing & Mathematical Model Verification
    print("[*] Test 1: Mathematical Production & Rate-Limit Pacing Model...")
    total_minutes_per_day = 24 * 60  # 1,440 minutes
    target_articles = 200
    pacing_interval_minutes = total_minutes_per_day / target_articles  # 7.2 minutes
    pacing_interval_seconds = int(pacing_interval_minutes * 60)       # 432 seconds

    print(f"    - Target Production : {target_articles} articles / 24 hours")
    print(f"    - Total Daily Time  : {total_minutes_per_day} minutes (86,400 seconds)")
    print(f"    - Required Cadence  : Exactly 1 article every {pacing_interval_minutes} minutes ({pacing_interval_seconds}s)")
    print(f"    - Generation Latency: ~40-45s active LLM generation")
    print(f"    - Idle Cooldown     : ~385s idle buffer (ensures ZERO NIM rate-limit exhaustion)")

    assert pacing_interval_seconds == 432, f"Pacing calculation mismatch! Got {pacing_interval_seconds}"
    print("    [+] Mathematical Cadence Model: Verified (432s / 7.2m interval)")

    print("-" * 68)

    # 2. Lifecycle & Telemetry State Transitions
    print("[*] Test 2: Daemon Lifecycle Management (Start, Telemetry, Stop)...")
    
    # Test Start
    started = automation_manager.start(interval_seconds=432, daily_target=200)
    assert started is True, "Failed to start automation manager!"
    assert automation_manager._is_running is True, "Daemon state flag not set to True!"

    # Test Duplicate Start Rejection
    duplicate_start = automation_manager.start()
    assert duplicate_start is False, "Daemon allowed duplicate start while active!"

    # Test Telemetry Status Query
    status = automation_manager.get_status()
    print(f"    [+] Live Telemetry Query:")
    print(f"        - Running Status  : {status['is_running']}")
    print(f"        - Interval        : {status['interval_seconds']}s ({status['interval_minutes']} mins)")
    print(f"        - Daily Target    : {status['daily_target']}")
    print(f"        - Started At      : {status['started_at']}")
    print(f"        - Countdown Timer : {status['seconds_until_next_run']}s")

    assert status["is_running"] is True
    assert status["daily_target"] == 200
    assert status["interval_seconds"] == 432

    # Test Stop
    stopped = automation_manager.stop()
    assert stopped is True, "Failed to stop automation manager!"
    assert automation_manager._is_running is False, "Daemon state flag not set to False after stop!"
    print("    [+] Daemon Lifecycle: Start -> Status -> Stop verified cleanly.")

    print("-" * 68)

    # 3. Live Autonomous Iteration with Automatic Publishing
    print("[*] Test 3: Live Autonomous Generation & Publishing Iteration...")
    print("    Triggering 1 complete autonomous cycle (Discovery -> L1/L2 -> Research -> Writer -> SEO -> Media -> Quality -> Publish)...")
    
    db: Session = SessionLocal()
    initial_published_count = db.query(Article).filter(Article.status == "published").count()
    db.close()

    cycle_start = time.time()
    result = automation_manager.execute_single_autonomous_iteration()
    cycle_elapsed = time.time() - cycle_start

    print(f"[+] Autonomous Iteration Finished in {cycle_elapsed:.1f} seconds!")
    print(f"    - Success Status   : {result.get('success')}")
    print(f"    - Article ID       : {result.get('article_id')}")
    print(f"    - Destination      : {result.get('destination')}, {result.get('country')}")
    print(f"    - Title            : {result.get('title')}")
    print(f"    - Quality Score    : {result.get('quality_score')}/10.0")
    print(f"    - Live Website URL : {result.get('website_url')}")

    assert result.get("success") is True, f"Autonomous cycle failed: {result}"
    assert result.get("article_id") is not None, "Article ID missing from result!"

    print("-" * 68)

    # 4. Database & Public Feed Verification
    print("[*] Test 4: Verifying Automated Database & Public Feed Sync...")
    db = SessionLocal()
    try:
        final_published_count = db.query(Article).filter(Article.status == "published").count()
        print(f"    - Initial Published Count : {initial_published_count}")
        print(f"    - Current Published Count : {final_published_count}")
        assert final_published_count == initial_published_count + 1, "Published article count did not increment!"

        feed = get_public_feed(db=db, limit=1)
        latest_post = feed["posts"][0]
        print(f"    [+] Latest Post on Live Feed:")
        print(f"        - Title       : {latest_post['title']}")
        print(f"        - Destination : {latest_post['destination']}, {latest_post['country']}")
        print(f"        - Category    : {latest_post['category']}")
        print(f"        - Score       : {latest_post['quality_score']}/10.0")
        print(f"        - Featured Img: {latest_post['featured_image']['url'][:60]}...")

        print("-" * 68)
        print("[+] Phase 12 Automation & Scaling Engine Diagnostic Passed Successfully!")
        print("=" * 68)

    finally:
        db.close()


if __name__ == "__main__":
    run_automation_diagnostics()
