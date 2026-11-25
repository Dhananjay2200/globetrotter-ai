"""
FastAPI Routes for Article Quality Evaluation and Revision Routing.
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Article
from app.graph.nodes.quality_check import evaluate_and_route_article

router = APIRouter(prefix="/evaluate", tags=["Article Quality Evaluation"])


class EvaluationResponse(BaseModel):
    article_id: int
    status: str
    quality_score: float
    threshold_used: float
    passes_threshold: bool
    attempts_made: int
    dimension_scores: Dict[str, float]
    strengths: List[str]
    deficiencies: List[str]
    revision_recommendations: List[str]


@router.post("/{article_id}", response_model=EvaluationResponse, status_code=status.HTTP_200_OK)
def trigger_quality_evaluation(
    article_id: int,
    threshold: Optional[float] = Query(None, ge=1.0, le=10.0, description="Optional custom quality threshold (1.0 - 10.0)"),
    db: Session = Depends(get_db),
):
    """
    Triggers the Quality Evaluation Agent:
    Evaluates the article against the 11-point rubric, executes automated revision
    if below threshold, and updates status to 'quality_passed' or 'needs_review'.
    """
    try:
        result = evaluate_and_route_article(
            db=db,
            article_id=article_id,
            max_retries=1,
            threshold=threshold,
        )
        return EvaluationResponse(**result)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quality evaluation failed: {str(exc)}",
        )


@router.get("/{article_id}")
def get_article_quality_status(
    article_id: int,
    db: Session = Depends(get_db),
):
    """Retrieves current quality score and publication status for an article."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} was not found",
        )

    return {
        "article_id": article.id,
        "title": article.title,
        "status": article.status,
        "quality_score": article.quality_score,
        "is_approved_for_publishing": article.status == "quality_passed",
    }
