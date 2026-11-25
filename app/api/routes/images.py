"""
FastAPI Routes for Image Discovery, Licensing Verification, and Media Management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Article, ImageAsset
from app.graph.nodes.image_search import discover_and_attach_images

router = APIRouter(prefix="/images", tags=["Image Discovery & Media Management"])


class ImageAssetResponse(BaseModel):
    id: int
    article_id: int
    image_url: str
    local_path: Optional[str]
    provider: str
    creator: Optional[str]
    license_name: str
    attribution: Optional[str]
    alt_text: Optional[str]
    is_featured: bool
    created_at: str

    class Config:
        from_attributes = True


@router.post("/discover/{article_id}", response_model=List[ImageAssetResponse], status_code=status.HTTP_201_CREATED)
def trigger_image_discovery(
    article_id: int,
    count: int = Query(3, ge=1, le=8, description="Number of images to discover"),
    db: Session = Depends(get_db),
):
    """
    Triggers media discovery for an article:
    Searches permitted image providers (Wikimedia Commons, Unsplash, Pexels),
    verifies usage licenses, establishes creator attributions, and commits to database.
    """
    try:
        assets = discover_and_attach_images(db=db, article_id=article_id, target_count=count)
        return [
            ImageAssetResponse(
                id=a.id,
                article_id=a.article_id,
                image_url=a.image_url,
                local_path=a.local_path,
                provider=a.provider,
                creator=a.creator,
                license_name=a.license_name,
                attribution=a.attribution,
                alt_text=a.alt_text,
                is_featured=a.is_featured,
                created_at=a.created_at.isoformat(),
            )
            for a in assets
        ]
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image discovery failed: {str(exc)}",
        )


@router.get("/article/{article_id}", response_model=List[ImageAssetResponse])
def get_article_images(
    article_id: int,
    db: Session = Depends(get_db),
):
    """Retrieves all attached images, creator attributions, and license details for an article."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} was not found",
        )

    assets = (
        db.query(ImageAsset)
        .filter(ImageAsset.article_id == article_id)
        .order_by(ImageAsset.is_featured.desc(), ImageAsset.id.asc())
        .all()
    )

    return [
        ImageAssetResponse(
            id=a.id,
            article_id=a.article_id,
            image_url=a.image_url,
            local_path=a.local_path,
            provider=a.provider,
            creator=a.creator,
            license_name=a.license_name,
            attribution=a.attribution,
            alt_text=a.alt_text,
            is_featured=a.is_featured,
            created_at=a.created_at.isoformat(),
        )
        for a in assets
    ]
