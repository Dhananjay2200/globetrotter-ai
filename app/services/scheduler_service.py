"""
GlobeTrotter AI - Automation & Scaling Scheduler Service.
Target: 200 high-quality, verified travel blog posts per 24 hours.
Pacing: 1 post every 7.2 minutes (432 seconds).
Features:
  - 100% Autonomous worldwide region and category balancing
  - Controlled pacing to stay well within NVIDIA NIM API rate limits
  - Automatic publishing of quality-passed articles
  - Error backoff, retry mechanisms, and live telemetry
"""

import asyncio
import threading
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.database.models import Article, Topic, PublishingJob
from app.graph.workflow import run_globetrotter_pipeline
from app.services.publisher_service import publish_article
from app.utils.logging import logger


class AutomationManager:
    """
    Singleton Manager for the 24/7 autonomous 200 articles/day publishing engine.
    """
    def __init__(self):
        self._is_running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Pacing & Target Configuration
        # 24 hours * 60 mins = 1440 mins / 200 articles = 7.2 mins = 432 seconds
        self.interval_seconds = 432
        self.daily_target = 200
        self.current_day = datetime.now(timezone.utc).date()
        
        # Runtime Statistics & Telemetry
        self.articles_generated_today = 0
        self.total_runs = 0
        self.successful_runs = 0
        self.failed_runs = 0
        self.last_run_at: Optional[datetime] = None
        self.next_run_at: Optional[datetime] = None
        self.started_at: Optional[datetime] = None
        self.logs: List[str] = []
        self._max_logs = 100

    def add_log(self, message: str):
        """Appends timestamped message to recent memory log buffer."""
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        formatted = f"[{now_str}] {message}"
        self.logs.append(formatted)
        if len(self.logs) > self._max_logs:
            self.logs.pop(0)
        logger.info(f"[Automation Daemon] {message}")

    def get_status(self) -> Dict[str, Any]:
        """Returns the current state and telemetry of the automation daemon."""
        seconds_until_next = None
        if self._is_running and self.next_run_at:
            delta = (self.next_run_at - datetime.now(timezone.utc)).total_seconds()
            seconds_until_next = max(0, int(delta))

        # Check 24-hour UTC rollover
        today_date = datetime.now(timezone.utc).date()
        if today_date != self.current_day:
            self.articles_generated_today = 0
            self.current_day = today_date

        # Query database counts: articles published today vs all-time totals
        db: Session = SessionLocal()
        try:
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            today_count = db.query(Article).filter(
                Article.status == "published",
                Article.published_at >= today_start
            ).count()
            total_articles = db.query(Article).count()
            total_published = db.query(Article).filter(Article.status == "published").count()
            current_today = max(self.articles_generated_today, today_count)
        except Exception:
            current_today = self.articles_generated_today
            total_articles = 0
            total_published = 0
        finally:
            db.close()

        # Calculate time until next midnight UTC reset
        now_utc = datetime.now(timezone.utc)
        midnight_utc = (now_utc + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        seconds_until_reset = int((midnight_utc - now_utc).total_seconds())

        return {
            "is_running": self._is_running,
            "interval_seconds": self.interval_seconds,
            "interval_minutes": round(self.interval_seconds / 60, 2),
            "daily_target": self.daily_target,
            "articles_generated_today": current_today,
            "total_articles": total_articles,
            "total_published": total_published,
            "progress_percent": round(min(100.0, (current_today / self.daily_target) * 100), 1),
            "current_cycle_date": today_date.isoformat(),
            "seconds_until_reset": seconds_until_reset,
            "total_runs": self.total_runs,
            "successful_runs": self.successful_runs,
            "failed_runs": self.failed_runs,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "next_run_at": self.next_run_at.isoformat() if self.next_run_at else None,
            "seconds_until_next_run": seconds_until_next,
            "recent_logs": self.logs[-15:],
        }

    def execute_single_autonomous_iteration(self) -> Dict[str, Any]:
        """
        Executes one full autonomous cycle:
          1. Autonomous Topic Discovery (worldwide balanced rotation)
          2. Level 1 & Level 2 Deduplication Check
          3. Multi-source research & citation
          4. 12-section editorial writing
          5. SEO optimization
          6. Permitted image discovery
          7. Quality gate evaluation (>= 8.0)
          8. Automatic publication to React feed
        """
        self.total_runs += 1
        self.last_run_at = datetime.now(timezone.utc)
        self.add_log(f"Starting Autonomous Generation Iteration #{self.total_runs}...")

        try:
            # Step 1: Run full LangGraph pipeline (autonomous discovery mode)
            final_state = run_globetrotter_pipeline(initial_state={
                "quality_threshold": 8.0,
                "max_revisions": 1,
            })

            status = final_state.get("status")

            # Handle duplicate case gracefully
            if status == "duplicate_rejected":
                reason = final_state.get("deduplication_reason", "Topic already exists")
                self.add_log(f"Topic was flagged as duplicate ({reason}). Retrying novel angle on next cycle.")
                return {"success": False, "status": status, "reason": reason}

            article_id = final_state.get("article_id")
            quality_score = final_state.get("quality_score")
            destination = final_state.get("destination")
            country = final_state.get("country")
            title = final_state.get("article_title")

            # Step 2: Quality Gate validation
            if status == "quality_passed" and article_id:
                # Step 3: Automatically Publish to React Feed
                db: Session = SessionLocal()
                try:
                    job, payload = publish_article(db=db, article_id=article_id)
                    self.successful_runs += 1
                    self.articles_generated_today += 1

                    self.add_log(
                        f"SUCCESS! Published Article ID {article_id} ('{destination}', {country}) | "
                        f"Score: {quality_score}/10 | URL: {payload['website_url']} | "
                        f"Today's Progress: {self.articles_generated_today}/{self.daily_target}"
                    )

                    return {
                        "success": True,
                        "status": "published",
                        "article_id": article_id,
                        "title": title,
                        "destination": destination,
                        "country": country,
                        "quality_score": quality_score,
                        "website_url": payload["website_url"],
                        "job_id": job.id,
                    }
                finally:
                    db.close()
            else:
                self.failed_runs += 1
                self.add_log(f"Article ID {article_id} status is '{status}'. Marked for manual review.")
                return {"success": False, "status": status, "article_id": article_id}

        except Exception as exc:
            self.failed_runs += 1
            self.add_log(f"Iteration error: {str(exc)}")
            logger.error(f"[Automation Manager] Pipeline exception: {exc}", exc_info=True)
            return {"success": False, "error": str(exc)}

    def _worker_loop(self):
        """Background thread executing the recurring generation loop."""
        self.add_log(
            f"Worker loop started. Target: {self.daily_target} posts/day. "
            f"Pacing: 1 post every {self.interval_seconds}s ({round(self.interval_seconds / 60, 2)} mins)."
        )

        while not self._stop_event.is_set():
            # Check 24-hour cycle date rollover
            today_date = datetime.now(timezone.utc).date()
            if today_date != self.current_day:
                self.articles_generated_today = 0
                self.current_day = today_date
                self.add_log(f"New 24-hour cycle began for {today_date.isoformat()}. Daily counter reset to 0/{self.daily_target}.")

            # Check if daily target reached
            if self.articles_generated_today >= self.daily_target:
                self.add_log(f"Daily target of {self.daily_target} articles reached! Pausing until midnight UTC.")
                # Sleep until next UTC midnight
                now = datetime.now(timezone.utc)
                tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                wait_seconds = (tomorrow - now).total_seconds()
                self._stop_event.wait(timeout=wait_seconds)
                self.articles_generated_today = 0
                self.current_day = datetime.now(timezone.utc).date()
                self.add_log(f"24-hour cycle rolled over to {self.current_day.isoformat()}. Daily counter reset to 0/{self.daily_target}.")
                continue

            # Execute one iteration
            self.execute_single_autonomous_iteration()

            # Schedule next trigger
            next_time = datetime.now(timezone.utc) + timedelta(seconds=self.interval_seconds)
            self.next_run_at = next_time
            self.add_log(f"Pacing cooldown. Next iteration scheduled at {next_time.strftime('%H:%M:%S UTC')}.")

            # Sleep in small increments to allow responsive shutdown
            slept = 0
            while slept < self.interval_seconds and not self._stop_event.is_set():
                time.sleep(1)
                slept += 1

        self.add_log("Worker loop stopped.")
        self._is_running = False

    def start(self, interval_seconds: Optional[int] = None, daily_target: Optional[int] = None) -> bool:
        """Starts the autonomous generation engine in a background thread."""
        if self._is_running:
            self.add_log("Start requested, but daemon is already active.")
            return False

        if interval_seconds:
            self.interval_seconds = interval_seconds
        if daily_target:
            self.daily_target = daily_target

        self._stop_event.clear()
        self._is_running = True
        self.started_at = datetime.now(timezone.utc)
        self.next_run_at = self.started_at

        self._thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._thread.start()
        self.add_log("Autonomous Engine successfully initiated.")
        return True

    def stop(self) -> bool:
        """Stops the autonomous generation engine gracefully."""
        if not self._is_running:
            self.add_log("Stop requested, but daemon is not running.")
            return False

        self.add_log("Stopping Autonomous Engine gracefully...")
        self._stop_event.set()
        self._is_running = False
        self.next_run_at = None
        return True


# Global Singleton Instance
automation_manager = AutomationManager()
