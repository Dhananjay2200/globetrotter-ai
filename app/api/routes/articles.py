"""
FastAPI Routes for Travel Article Management and Generation.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Article, Topic, ResearchSource
from app.graph.nodes.writer import write_article_for_topic

router = APIRouter(prefix="/articles", tags=["Article Writer & Management"])


class ArticleSummaryResponse(BaseModel):
    id: int
    topic_id: int
    title: str
    slug: str
    summary: Optional[str]
    word_count: int
    status: str
    quality_score: Optional[float]
    published_at: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


class ArticleDetailResponse(BaseModel):
    id: int
    topic_id: int
    destination: str
    country: str
    category: str
    title: str
    slug: str
    summary: Optional[str]
    body_markdown: str
    word_count: int
    status: str
    quality_score: Optional[float]
    created_at: str
    citations_count: int

    class Config:
        from_attributes = True


@router.post("/generate/{topic_id}", response_model=ArticleSummaryResponse, status_code=status.HTTP_201_CREATED)
def generate_article(
    topic_id: int,
    db: Session = Depends(get_db),
):
    """
    Triggers the Article Writer Agent for a specific topic ID:
    generates 12-section outline, long-form Markdown article, links sources,
    and commits to PostgreSQL.
    """
    try:
        article = write_article_for_topic(db=db, topic_id=topic_id)
        return ArticleSummaryResponse(
            id=article.id,
            topic_id=article.topic_id,
            title=article.title,
            slug=article.slug,
            summary=article.summary,
            word_count=article.word_count,
            status=article.status,
            quality_score=article.quality_score,
            created_at=article.created_at.isoformat(),
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Article generation failed: {str(exc)}",
        )


@router.get("", response_model=List[ArticleSummaryResponse])
def list_articles(
    status: Optional[str] = Query(None, description="Filter by status (draft, quality_passed, published)"),
    limit: int = Query(250, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Retrieves paginated travel articles."""
    query = db.query(Article)
    if status:
        query = query.filter(Article.status == status)

    articles = query.order_by(Article.created_at.desc()).offset(offset).limit(limit).all()
    return [
        ArticleSummaryResponse(
            id=a.id,
            topic_id=a.topic_id,
            title=a.title,
            slug=a.slug,
            summary=a.summary,
            word_count=a.word_count,
            status=a.status,
            quality_score=a.quality_score,
            published_at=a.published_at.isoformat() if a.published_at else None,
            created_at=a.created_at.isoformat(),
        )
        for a in articles
    ]


@router.get("/{article_id}", response_model=ArticleDetailResponse)
def get_article_detail(article_id: int, db: Session = Depends(get_db)):
    """Retrieves full article details including complete Markdown content and citation counts."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} was not found",
        )

    topic = db.query(Topic).filter(Topic.id == article.topic_id).first()
    citations_count = db.query(ResearchSource).filter(ResearchSource.article_id == article.id).count()

    return ArticleDetailResponse(
        id=article.id,
        topic_id=article.topic_id,
        destination=topic.destination if topic else "Unknown Destination",
        country=topic.country if topic else "Global",
        category=topic.category if topic else "Travel",
        title=article.title,
        slug=article.slug,
        summary=article.summary,
        body_markdown=article.body_markdown,
        word_count=article.word_count,
        status=article.status,
        quality_score=article.quality_score,
        created_at=article.created_at.isoformat(),
        citations_count=citations_count,
    )


@router.delete("/{article_id}", status_code=status.HTTP_200_OK)
def delete_article(article_id: int, db: Session = Depends(get_db)):
    """
    Deletes an article and cascades to its research sources, image assets,
    and publishing jobs.
    """
    from app.services.cache_service import blog_cache

    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} was not found",
        )

    title = article.title
    slug = article.slug
    db.delete(article)
    db.commit()

    # Flush feed and post cache
    blog_cache.invalidate_prefix("feed:")
    if slug:
        blog_cache.invalidate_prefix(f"post:{slug}")

    return {
        "status": "success",
        "message": f"Article ID {article_id} ('{title}') successfully deleted.",
    }
