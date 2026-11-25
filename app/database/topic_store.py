"""
Topic Storage and Canonical Deduplication Service (Level 1).
Provides canonical key generation and unique constraint enforcement in PostgreSQL.
"""

import re
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database.models import Topic, Destination
from app.utils.logging import logger


def slugify_text(text: str) -> str:
    """Converts a string into a clean lowercase slug stripped of non-alphanumeric chars."""
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


def generate_canonical_key(destination: str, category: str, unique_angle: str) -> str:
    """
    Generates a deterministic canonical key for Level 1 duplicate detection.
    Format: {destination_slug}__{category_slug}__{angle_slug}
    
    Example:
      destination: "Kyoto Historical Temples"
      category: "Heritage"
      unique_angle: "Zen meditation and architectural secrets"
      -> "kyoto-historical-temples__heritage__zen-meditation-and-architectural-secrets"
    """
    dest_slug = slugify_text(destination)
    cat_slug = slugify_text(category)
    # Take first 60 chars of angle slug to keep key concise yet unique
    angle_slug = slugify_text(unique_angle)[:60]
    return f"{dest_slug}__{cat_slug}__{angle_slug}"


def save_topic_if_unique(
    db: Session,
    destination: str,
    country: str,
    category: str,
    proposed_title: str,
    unique_angle: str,
    discovery_source: str = "ai_discovery",
    destination_id: Optional[int] = None,
) -> Tuple[Optional[Topic], bool]:
    """
    Saves a newly discovered topic if it does not already exist.
    Level 1 exact duplicate prevention via canonical_key.
    
    Returns:
      (topic, is_created):
        - If unique: returns (new_topic, True)
        - If duplicate: returns (existing_topic, False)
    """
    canonical_key = generate_canonical_key(destination, category, unique_angle)

    # 1. Check existing before write to avoid unnecessary constraint errors
    existing = db.query(Topic).filter(Topic.canonical_key == canonical_key).first()
    if existing:
        logger.info(f"Duplicate topic rejected [Level 1 - Canonical]: {canonical_key}")
        return existing, False

    # 2. Try inserting new topic with transaction safety
    new_topic = Topic(
        canonical_key=canonical_key,
        destination_id=destination_id,
        destination=destination.strip(),
        country=country.strip(),
        category=category.strip(),
        proposed_title=proposed_title.strip(),
        unique_angle=unique_angle.strip(),
        discovery_source=discovery_source,
        status="discovered",
    )

    try:
        db.add(new_topic)
        db.commit()
        db.refresh(new_topic)
        logger.info(f"Successfully saved unique topic ID {new_topic.id}: '{new_topic.proposed_title}'")
        return new_topic, True
    except IntegrityError:
        db.rollback()
        existing = db.query(Topic).filter(Topic.canonical_key == canonical_key).first()
        logger.info(f"Duplicate caught by database unique constraint: {canonical_key}")
        return existing, False


def list_topics(
    db: Session,
    status: Optional[str] = None,
    country: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> List[Topic]:
    """Retrieves paginated topics with optional filtering."""
    query = db.query(Topic)
    if status:
        query = query.filter(Topic.status == status)
    if country:
        query = query.filter(Topic.country.ilike(f"%{country}%"))
    return query.order_by(Topic.created_at.desc()).offset(offset).limit(limit).all()


def update_topic_status(db: Session, topic_id: int, new_status: str) -> Optional[Topic]:
    """Updates the workflow progress status of a topic."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if topic:
        topic.status = new_status
        db.commit()
        db.refresh(topic)
    return topic
