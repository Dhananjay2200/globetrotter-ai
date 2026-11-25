"""
FastAPI Routes for Topic Discovery and Management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Topic, Destination
from app.database.topic_store import list_topics
from app.services.discovery_service import (
    discover_topics,
    TopicProposal,
    TOURISM_CATEGORIES,
    GLOBAL_REGIONS,
)
from app.graph.nodes.duplicate_check import evaluate_and_persist_topic
from app.utils.logging import logger

router = APIRouter(prefix="/topics", tags=["Topic Discovery & Management"])


class DiscoverRequest(BaseModel):
    count: int = Field(default=5, ge=1, le=20, description="Number of topics to discover (1-20)")
    target_region: Optional[str] = Field(default=None, description="Optional continent or region filter")
    target_category: Optional[str] = Field(default=None, description="Optional tourism category filter")


class TopicItemResponse(BaseModel):
    id: int
    canonical_key: str
    destination: str
    country: str
    category: str
    proposed_title: str
    unique_angle: str
    discovery_source: str
    status: str
    created_at: str

    class Config:
        from_attributes = True


class RejectionItem(BaseModel):
    destination: str
    country: str
    proposed_title: str
    reason: str


class DiscoverResponse(BaseModel):
    discovered_count: int
    saved_count: int
    rejected_count: int
    saved_topics: List[TopicItemResponse]
    rejections: List[RejectionItem]


@router.get("/metadata", tags=["Topic Discovery & Management"])
def get_discovery_metadata():
    """Returns available tourism categories and global regions for targeting."""
    return {
        "tourism_categories": TOURISM_CATEGORIES,
        "global_regions": GLOBAL_REGIONS,
    }


@router.post("/discover", response_model=DiscoverResponse, status_code=status.HTTP_201_CREATED)
def trigger_topic_discovery(
    request: DiscoverRequest,
    db: Session = Depends(get_db),
):
    """
    Triggers autonomous AI discovery of worldwide tourism topics.
    Validates candidates through Level 1 & Level 2 duplicate detection
    and commits approved unique topics to the database.
    """
    logger.info(f"Triggering topic discovery: count={request.count}, region={request.target_region}, cat={request.target_category}")
    try:
        candidates = discover_topics(
            db=db,
            count=request.count,
            target_region=request.target_region,
            target_category=request.target_category,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Topic discovery failed communicating with LLM: {str(exc)}",
        )

    saved_topics: List[TopicItemResponse] = []
    rejections: List[RejectionItem] = []

    for candidate in candidates:
        # Check or create associated Destination record
        dest = db.query(Destination).filter(
            Destination.name == candidate.destination,
            Destination.country == candidate.country,
        ).first()

        if not dest:
            dest = Destination(
                name=candidate.destination,
                country=candidate.country,
                region=candidate.region,
                destination_type=candidate.category,
                description=candidate.unique_angle,
            )
            db.add(dest)
            db.commit()
            db.refresh(dest)

        topic_record, is_approved, eval_msg = evaluate_and_persist_topic(
            db=db,
            candidate=candidate,
            destination_id=dest.id,
        )

        if is_approved and topic_record:
            saved_topics.append(
                TopicItemResponse(
                    id=topic_record.id,
                    canonical_key=topic_record.canonical_key,
                    destination=topic_record.destination,
                    country=topic_record.country,
                    category=topic_record.category,
                    proposed_title=topic_record.proposed_title,
                    unique_angle=topic_record.unique_angle,
                    discovery_source=topic_record.discovery_source,
                    status=topic_record.status,
                    created_at=topic_record.created_at.isoformat(),
                )
            )
        else:
            rejections.append(
                RejectionItem(
                    destination=candidate.destination,
                    country=candidate.country,
                    proposed_title=candidate.proposed_title,
                    reason=eval_msg,
                )
            )

    return DiscoverResponse(
        discovered_count=len(candidates),
        saved_count=len(saved_topics),
        rejected_count=len(rejections),
        saved_topics=saved_topics,
        rejections=rejections,
    )


@router.get("", response_model=List[TopicItemResponse])
def get_topics(
    status: Optional[str] = Query(None, description="Filter by status (discovered, researching, written, published)"),
    country: Optional[str] = Query(None, description="Filter by country substring"),
    category: Optional[str] = Query(None, description="Filter by tourism category"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Retrieves paginated topics stored in the database."""
    query = db.query(Topic)
    if status:
        query = query.filter(Topic.status == status)
    if country:
        query = query.filter(Topic.country.ilike(f"%{country}%"))
    if category:
        query = query.filter(Topic.category.ilike(f"%{category}%"))

    topics = query.order_by(Topic.created_at.desc()).offset(offset).limit(limit).all()
    return [
        TopicItemResponse(
            id=t.id,
            canonical_key=t.canonical_key,
            destination=t.destination,
            country=t.country,
            category=t.category,
            proposed_title=t.proposed_title,
            unique_angle=t.unique_angle,
            discovery_source=t.discovery_source,
            status=t.status,
            created_at=t.created_at.isoformat(),
        )
        for t in topics
    ]


@router.get("/{topic_id}", response_model=TopicItemResponse)
def get_topic_by_id(topic_id: int, db: Session = Depends(get_db)):
    """Retrieves a single topic by ID."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic with ID {topic_id} was not found",
        )
    return TopicItemResponse(
        id=topic.id,
        canonical_key=topic.canonical_key,
        destination=topic.destination,
        country=topic.country,
        category=topic.category,
        proposed_title=topic.proposed_title,
        unique_angle=topic.unique_angle,
        discovery_source=topic.discovery_source,
        status=topic.status,
        created_at=topic.created_at.isoformat(),
    )
