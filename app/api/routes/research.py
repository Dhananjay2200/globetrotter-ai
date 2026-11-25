"""
FastAPI Routes for Research and Evidence Collection.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Topic, ResearchSource
from app.graph.nodes.research import conduct_topic_research

router = APIRouter(prefix="/research", tags=["Research & Evidence Collection"])


class ResearchSourceResponse(BaseModel):
    id: int
    topic_id: Optional[int]
    article_id: Optional[int]
    url: str
    publisher: Optional[str]
    title: Optional[str]
    evidence_excerpt: Optional[str]
    retrieved_at: str

    class Config:
        from_attributes = True


class ResearchExecutionResponse(BaseModel):
    topic_id: int
    destination: str
    country: str
    status: str
    total_sources: int
    source_ids: List[int]
    evidence: dict


@router.post("/{topic_id}", response_model=ResearchExecutionResponse, status_code=status.HTTP_200_OK)
def trigger_topic_research(
    topic_id: int,
    db: Session = Depends(get_db),
):
    """
    Triggers multi-source web and knowledge research for a specific topic ID.
    Extracts structured factual evidence and saves citations to the database.
    """
    try:
        result = conduct_topic_research(db=db, topic_id=topic_id)
        return ResearchExecutionResponse(**result)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Research processing failed: {str(exc)}",
        )


@router.get("/{topic_id}/sources", response_model=List[ResearchSourceResponse])
def get_topic_sources(
    topic_id: int,
    db: Session = Depends(get_db),
):
    """Retrieves all persisted reference citations and evidence excerpts for a topic."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic with ID {topic_id} was not found",
        )

    sources = (
        db.query(ResearchSource)
        .filter(ResearchSource.topic_id == topic_id)
        .order_by(ResearchSource.retrieved_at.desc())
        .all()
    )

    return [
        ResearchSourceResponse(
            id=s.id,
            topic_id=s.topic_id,
            article_id=s.article_id,
            url=s.url,
            publisher=s.publisher,
            title=s.title,
            evidence_excerpt=s.evidence_excerpt,
            retrieved_at=s.retrieved_at.isoformat(),
        )
        for s in sources
    ]
