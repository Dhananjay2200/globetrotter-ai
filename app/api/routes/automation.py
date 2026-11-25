"""
GlobeTrotter AI - Automation & Scaling API Router.
Provides administrative endpoints to start, stop, monitor, and trigger
the autonomous 200 articles/day publishing engine.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field

from app.services.scheduler_service import automation_manager
from app.utils.logging import logger

router = APIRouter(prefix="/automation", tags=["Automation & Scaling"])


class AutomationStartRequest(BaseModel):
    """Payload to start the autonomous daemon."""
    interval_seconds: Optional[int] = Field(
        432, 
        ge=60, 
        le=86400, 
        description="Seconds between article generations (432s = 7.2 mins = 200/day)"
    )
    daily_target: Optional[int] = Field(
        200, 
        ge=1, 
        le=1000, 
        description="Target number of published articles per 24 hours"
    )


class AutomationStatusResponse(BaseModel):
    """Telemetry response describing daemon health and daily progress."""
    is_running: bool
    interval_seconds: int
    interval_minutes: float
    daily_target: int
    articles_generated_today: int
    total_articles: Optional[int] = 0
    total_published: Optional[int] = 0
    progress_percent: float
    current_cycle_date: Optional[str] = None
    seconds_until_reset: Optional[int] = None
    total_runs: int
    successful_runs: int
    failed_runs: int
    started_at: Optional[str] = None
    last_run_at: Optional[str] = None
    next_run_at: Optional[str] = None
    seconds_until_next_run: Optional[int] = None
    recent_logs: List[str] = []


@router.get("/status", response_model=AutomationStatusResponse)
def get_automation_status():
    """
    Returns the real-time status, pacing, and 200-articles/day progress of the autonomous engine.
    """
    return automation_manager.get_status()


@router.post("/start")
def start_automation_daemon(request: Optional[AutomationStartRequest] = None):
    """
    Starts the continuous 24/7 background generator.
    Defaults to 1 article every 7.2 minutes to hit exactly 200 articles/day.
    """
    interval = request.interval_seconds if request else 432
    target = request.daily_target if request else 200

    started = automation_manager.start(interval_seconds=interval, daily_target=target)
    if not started:
        raise HTTPException(
            status_code=400, 
            detail="Automation daemon is already running. Check /status."
        )

    return {
        "message": "Autonomous 200 articles/day engine started successfully.",
        "interval_seconds": interval,
        "interval_minutes": round(interval / 60, 2),
        "daily_target": target,
        "status": automation_manager.get_status(),
    }


@router.post("/stop")
def stop_automation_daemon():
    """
    Pauses or stops the continuous background generation loop.
    """
    stopped = automation_manager.stop()
    if not stopped:
        raise HTTPException(
            status_code=400, 
            detail="Automation daemon is not currently active."
        )

    return {
        "message": "Autonomous generation engine stopped successfully.",
        "status": automation_manager.get_status(),
    }


@router.post("/trigger-single")
def trigger_single_run(background_tasks: BackgroundTasks):
    """
    Triggers an immediate autonomous generation iteration in the background
    without interrupting or modifying the recurring schedule.
    """
    background_tasks.add_task(automation_manager.execute_single_autonomous_iteration)
    return {
        "message": "Immediate autonomous generation task dispatched to background worker.",
        "timestamp": automation_manager.get_status()["last_run_at"],
    }
