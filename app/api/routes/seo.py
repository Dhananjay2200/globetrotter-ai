"""
FastAPI Routes for SEO Metadata Optimization and Inspection.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Article
from app.graph.nodes.seo import optimize_article_seo
from app.services.seo_service import SEOMetadata

router = APIRouter(prefix="/seo", tags=["SEO Optimization Agent"])


class SEOResponse(BaseModel):
    article_id: int
    seo_title: str
    meta_description: str
    slug: str
    main_keyword: str
    secondary_keywords: List[str]
    summary: str
    tags: List[str]
    image_alt_text_suggestions: List[str]


@router.post("/optimize/{article_id}", response_model=SEOResponse, status_code=status.HTTP_200_OK)
def trigger_seo_optimization(
    article_id: int,
    db: Session = Depends(get_db),
):
    """
    Triggers the SEO Optimization Agent for a specific article ID:
    generates SEO title, meta description, clean URL slug, keywords, tags,
    and alt text recommendations, updating the database record.
    """
    try:
        article, seo = optimize_article_seo(db=db, article_id=article_id)
        return SEOResponse(
            article_id=article.id,
            seo_title=seo.seo_title,
            meta_description=seo.meta_description,
            slug=seo.slug,
            main_keyword=seo.main_keyword,
            secondary_keywords=seo.secondary_keywords,
            summary=seo.summary,
            tags=seo.tags,
            image_alt_text_suggestions=seo.image_alt_text_suggestions,
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SEO optimization failed: {str(exc)}",
        )


@router.get("/{article_id}", response_model=SEOResponse)
def get_article_seo(
    article_id: int,
    db: Session = Depends(get_db),
):
    """Retrieves the stored SEO configuration and metadata for an article."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} was not found",
        )

    return SEOResponse(
        article_id=article.id,
        seo_title=article.seo_title or article.title,
        meta_description=article.seo_description or (article.summary[:155] if article.summary else ""),
        slug=article.slug,
        main_keyword=article.main_keyword or "Travel Guide",
        secondary_keywords=[],
        summary=article.summary or "",
        tags=[],
        image_alt_text_suggestions=[],
    )
