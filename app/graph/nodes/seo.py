"""
GlobeTrotter AI - LangGraph SEO Agent Node.
Synthesizes SEO titles, meta descriptions, unique slugs, keywords, tags,
and image alt text suggestions, and persists them into PostgreSQL.
"""

from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.database.models import Article, Topic
from app.services.seo_service import generate_seo_metadata, SEOMetadata
from app.utils.logging import logger


def ensure_unique_slug(db: Session, target_slug: str, current_article_id: int) -> str:
    """Ensures slug uniqueness in the database, appending a numeric counter if colliding."""
    base_slug = target_slug
    counter = 1
    slug = base_slug

    while True:
        existing = db.query(Article).filter(
            Article.slug == slug,
            Article.id != current_article_id,
        ).first()
        if not existing:
            return slug
        counter += 1
        slug = f"{base_slug}-{counter}"


def optimize_article_seo(
    db: Session,
    article_id: int,
) -> Tuple[Article, SEOMetadata]:
    """
    Executes the SEO optimization pipeline for an article:
    1. Fetches article and topic from database.
    2. Uses NVIDIA NIM to analyze content and synthesize SEO metadata.
    3. Resolves and commits slug, seo_title, seo_description, main_keyword, and summary.
    4. Returns updated Article record and complete SEOMetadata package.
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise ValueError(f"Article with ID {article_id} does not exist.")

    topic = db.query(Topic).filter(Topic.id == article.topic_id).first()
    if not topic:
        raise ValueError(f"Associated Topic for Article ID {article_id} not found.")

    logger.info(f"[*] Optimizing SEO metadata for Article ID {article.id}: '{article.title}'")

    # Step 1: Synthesize SEO Metadata
    seo: SEOMetadata = generate_seo_metadata(
        destination=topic.destination,
        country=topic.country,
        category=topic.category,
        article_title=article.title,
        body_markdown=article.body_markdown,
        unique_angle=topic.unique_angle,
    )

    # Step 2: Ensure slug uniqueness
    unique_slug = ensure_unique_slug(db, seo.slug, article.id)

    # Step 3: Update Article in PostgreSQL
    article.seo_title = seo.seo_title
    article.seo_description = seo.meta_description
    article.main_keyword = seo.main_keyword
    article.slug = unique_slug
    article.summary = seo.summary

    db.commit()
    db.refresh(article)

    logger.info(
        f"[+] SEO metadata saved for Article ID {article.id}. "
        f"SEO Title: '{article.seo_title}' | Slug: '{article.slug}'"
    )

    return article, seo
