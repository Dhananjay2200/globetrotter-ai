"""
GlobeTrotter AI - LangGraph Image Discovery Node.
Orchestrates media discovery from permitted repositories, verifies usage licenses,
formats attribution statements, and commits ImageAsset records to PostgreSQL.
"""

from typing import List
from sqlalchemy.orm import Session
from app.database.models import Article, Topic, ImageAsset
from app.services.image_service import discover_article_images, DiscoveredImage
from app.utils.logging import logger


def discover_and_attach_images(
    db: Session,
    article_id: int,
    target_count: int = 3,
) -> List[ImageAsset]:
    """
    Executes media discovery pipeline for an article:
    1. Loads article and destination details.
    2. Searches permitted image repositories (Wikimedia Commons, Unsplash, Pexels).
    3. Validates license permissions and builds legal attributions.
    4. Selects 1 featured image and supporting gallery images.
    5. Commits ImageAsset records to PostgreSQL.
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise ValueError(f"Article with ID {article_id} does not exist.")

    topic = db.query(Topic).filter(Topic.id == article.topic_id).first()
    if not topic:
        raise ValueError(f"Topic associated with Article ID {article_id} not found.")

    logger.info(f"[*] Starting Image Discovery for Article ID {article.id}: '{topic.destination}' ({topic.country})")

    # Extract keywords and alt suggestions from article metadata
    keywords = [article.main_keyword] if article.main_keyword else [topic.category]
    alt_suggestions = [
        f"Featured panoramic view of {topic.destination} in {topic.country}",
        f"Historic architecture and landmark of {topic.destination}",
        f"Cultural atmosphere and landscape at {topic.destination}",
    ]

    discovered_images: List[DiscoveredImage] = discover_article_images(
        destination=topic.destination,
        country=topic.country,
        keywords=keywords,
        alt_suggestions=alt_suggestions,
        target_count=target_count,
    )

    if not discovered_images:
        logger.warning(f"No legally permitted images found for '{topic.destination}'.")
        return []

    # Clear existing assets for this article if re-running
    existing_assets = db.query(ImageAsset).filter(ImageAsset.article_id == article.id).all()
    if existing_assets:
        for old_asset in existing_assets:
            db.delete(old_asset)
        db.commit()

    saved_assets: List[ImageAsset] = []
    for img in discovered_images:
        asset = ImageAsset(
            article_id=article.id,
            image_url=img.image_url,
            local_path=None,
            provider=img.provider,
            creator=img.creator,
            license_name=img.license_name,
            attribution=img.attribution,
            alt_text=img.alt_text,
            is_featured=img.is_featured,
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)
        saved_assets.append(asset)

    logger.info(
        f"[+] Successfully saved {len(saved_assets)} image assets for Article ID {article.id}. "
        f"Featured Image ID: {saved_assets[0].id if saved_assets else 'None'}"
    )

    return saved_assets
