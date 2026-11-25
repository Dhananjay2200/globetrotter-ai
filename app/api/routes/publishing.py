"""
GlobeTrotter AI - Publishing API Router.
Exposes endpoints to publish approved articles, run batch publishing,
query publishing job history, and serve the public blog feed for the React website.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Response, Request
from fastapi.responses import Response as FastAPIResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database.session import get_db
from app.database.models import PublishingJob, Article, Topic
from app.services.cache_service import blog_cache
from app.services.publisher_service import (
    publish_article,
    unpublish_article,
    publish_all_pending,
    get_public_feed,
    get_single_published_post_data,
    format_blog_payload,
)

router = APIRouter(prefix="/publish", tags=["Publishing"])


class PublishResponse(BaseModel):
    """Response payload for a successful publishing action."""
    job_id: int
    article_id: int
    status: str
    idempotency_key: str
    website_url: str
    published_at: str
    post: Dict[str, Any]


class BatchPublishResponse(BaseModel):
    """Response payload for batch publishing."""
    total_pending: int
    published_count: int
    published_ids: List[int]
    failed_count: int
    failed_details: List[Dict[str, Any]]


class BatchPublishSelectedRequest(BaseModel):
    """Payload to batch publish user-selected articles."""
    article_ids: List[int]
    force: bool = True


class PublishingJobItem(BaseModel):
    """Summary of a publishing job record."""
    id: int
    article_id: int
    status: str
    attempts: int
    idempotency_key: str
    last_error: Optional[str]
    created_at: str
    updated_at: str


@router.post("/{article_id}", response_model=PublishResponse)
def publish_single_article(
    article_id: int,
    force: bool = Query(True, description="Allow manual admin override for articles below threshold or in review"),
    db: Session = Depends(get_db),
):
    """
    Publishes an individual article that has passed the quality gate,
    or allows manual admin override for articles under review/below threshold.
    Guarantees idempotency: re-publishing returns the existing publication record.
    """
    try:
        job, payload = publish_article(db=db, article_id=article_id, force=force)
        return PublishResponse(
            job_id=job.id,
            article_id=job.article_id,
            status=job.status,
            idempotency_key=job.idempotency_key,
            website_url=payload["website_url"],
            published_at=payload["published_at"],
            post=payload,
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Publishing failed: {str(exc)}")


@router.post("/unpublish/{article_id}")
def unpublish_single_article(
    article_id: int,
    db: Session = Depends(get_db),
):
    """
    Unpublishes an article, sets its status back to 'draft',
    and immediately purges the feed and article cache.
    """
    try:
        art = unpublish_article(db=db, article_id=article_id)
        return {
            "status": "success",
            "message": f"Article ID {article_id} ('{art.title}') successfully unpublished.",
            "article_id": art.id,
            "article_status": art.status,
        }
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unpublishing failed: {str(exc)}")


@router.post("/batch/run", response_model=BatchPublishResponse)
def publish_pending_articles(
    limit: int = Query(50, ge=1, le=200, description="Maximum pending articles to publish"),
    db: Session = Depends(get_db),
):
    """
    Scans for all articles in 'quality_passed' status and publishes them in batch.
    """
    result = publish_all_pending(db=db, limit=limit)
    return BatchPublishResponse(**result)


@router.post("/batch/selected")
def publish_selected_articles(
    payload: BatchPublishSelectedRequest,
    db: Session = Depends(get_db),
):
    """
    Publishes specific articles selected with checkboxes by the administrator.
    Supports force override so drafts/needs_review articles can be batch published.
    """
    published_ids = []
    failed_details = []
    for art_id in payload.article_ids:
        try:
            job, _ = publish_article(db=db, article_id=art_id, force=payload.force)
            published_ids.append(art_id)
        except Exception as exc:
            failed_details.append({"article_id": art_id, "error": str(exc)})

    return {
        "total_selected": len(payload.article_ids),
        "published_count": len(published_ids),
        "published_ids": published_ids,
        "failed_count": len(failed_details),
        "failed_details": failed_details,
    }


@router.get("/jobs", response_model=List[PublishingJobItem])
def list_publishing_jobs(
    status: Optional[str] = Query(None, description="Filter by status (pending, in_progress, published, failed)"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Retrieves the history of publishing jobs and delivery attempts.
    """
    query = db.query(PublishingJob)
    if status:
        query = query.filter(PublishingJob.status == status)

    jobs = query.order_by(PublishingJob.created_at.desc()).offset(offset).limit(limit).all()
    return [
        PublishingJobItem(
            id=j.id,
            article_id=j.article_id,
            status=j.status,
            attempts=j.attempts,
            idempotency_key=j.idempotency_key,
            last_error=j.last_error,
            created_at=j.created_at.isoformat(),
            updated_at=j.updated_at.isoformat(),
        )
        for j in jobs
    ]


@router.get("/feed")
def get_published_feed(
    request: Request,
    response: Response,
    category: Optional[str] = Query(None, description="Filter by category"),
    country: Optional[str] = Query(None, description="Filter by country"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Public blog feed consumed by the React website frontend.
    Returns all published articles formatted with full media and citations.
    Supports microsecond in-memory caching and HTTP 304 ETag short-circuiting.
    """
    feed_data, etag = get_public_feed(db=db, category=category, country=country, limit=limit, offset=offset)

    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["ETag"] = etag
    response.headers["X-Cache-Engine"] = "GlobeTrotter-HighConcurrency-MemoryCache"
    return feed_data


@router.get("/post/{slug}")
def get_single_published_post(
    slug: str,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Public single blog post reader endpoint consumed by React blog post viewer.
    Ultra-low latency microsecond response directly from RAM.
    """
    post_data, etag = get_single_published_post_data(db=db, slug=slug)
    if not post_data:
        raise HTTPException(status_code=404, detail=f"Published post '{slug}' not found.")

    response.headers["Cache-Control"] = "no-cache, must-revalidate"
    response.headers["ETag"] = etag
    response.headers["X-Cache-Engine"] = "GlobeTrotter-HighConcurrency-MemoryCache"
    return post_data


@router.get("/cache/stats")
def get_cache_telemetry():
    """
    Returns live in-memory cache metrics: hit ratio, requests count, and latency stats.
    """
    return blog_cache.get_stats()


@router.post("/cache/flush")
def flush_cache():
    """
    Manually invalidates the high-concurrency memory cache.
    """
    blog_cache.invalidate()
    return {"message": "Memory cache successfully flushed.", "stats": blog_cache.get_stats()}
