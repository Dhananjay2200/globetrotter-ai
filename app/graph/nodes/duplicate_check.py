"""
GlobeTrotter AI - Duplicate Detection System (Level 1 & Level 2).
Enforces:
  Level 1: Exact Canonical Key Deduplication (PostgreSQL unique constraint)
  Level 2: Semantic Similarity Deduplication (Thematic & Keyword Overlap Detection)
"""

import re
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from app.database.models import Topic
from app.database.topic_store import generate_canonical_key, save_topic_if_unique
from app.services.discovery_service import TopicProposal
from app.utils.logging import logger


def tokenize_text(text: str) -> set:
    """Normalizes and extracts significant keywords for token-level overlap scoring."""
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of",
        "with", "by", "from", "up", "about", "into", "over", "after", "is", "are",
        "was", "were", "be", "this", "that", "how", "what", "top", "best", "guide",
        "visit", "travel", "places", "destinations", "things", "exploring", "through"
    }
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    return {w for w in words if w not in stop_words}


def calculate_jaccard_similarity(set_a: set, set_b: set) -> float:
    """Calculates Jaccard similarity coefficient between two word sets."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return round(intersection / union, 3) if union > 0 else 0.0


def check_level1_canonical_duplicate(
    db: Session,
    destination: str,
    category: str,
    unique_angle: str,
) -> Tuple[bool, str]:
    """
    Level 1 Deduplication Check:
    Checks if an identical canonical key exists in the database.
    """
    canonical_key = generate_canonical_key(destination, category, unique_angle)
    existing = db.query(Topic).filter(Topic.canonical_key == canonical_key).first()
    if existing:
        return True, canonical_key
    return False, canonical_key


def check_level2_semantic_duplicate(
    db: Session,
    candidate: TopicProposal,
    threshold: float = 0.40,
) -> Tuple[bool, Optional[str], float]:
    """
    Level 2 Semantic Duplicate Check:
    Detects conceptual and thematic overlap with existing topics for the same destination/country.
    
    Example:
      - Existing: "Spectacular Southern Iceland Waterfalls: Walking Behind Glacial Cascades"
      - Candidate: "Top Iceland Waterfalls to Visit: Glacial Cascades and Southern Wonders"
      -> Flags as semantic duplicate because core intent & destination features overlap.
    """
    # Fetch existing topics matching the destination or country
    existing_topics = (
        db.query(Topic)
        .filter(
            (Topic.destination.ilike(f"%{candidate.destination}%")) |
            (Topic.country.ilike(f"%{candidate.country}%"))
        )
        .all()
    )

    if not existing_topics:
        return False, None, 0.0

    cand_title_tokens = tokenize_text(candidate.proposed_title)
    cand_all_tokens = tokenize_text(f"{candidate.destination} {candidate.proposed_title} {candidate.unique_angle}")

    for existing in existing_topics:
        exist_title_tokens = tokenize_text(existing.proposed_title)
        exist_all_tokens = tokenize_text(f"{existing.destination} {existing.proposed_title} {existing.unique_angle}")

        title_sim = calculate_jaccard_similarity(cand_title_tokens, exist_title_tokens)
        all_sim = calculate_jaccard_similarity(cand_all_tokens, exist_all_tokens)

        # Composite score gives high weight to title overlap and contextual angle overlap
        composite_score = round(0.6 * title_sim + 0.4 * all_sim, 3)

        if composite_score >= threshold or title_sim >= 0.50:
            logger.info(
                f"[Level 2 Semantic Duplicate] Similarity {composite_score} (title: {title_sim}) >= {threshold} "
                f"between '{candidate.proposed_title}' and existing Topic ID {existing.id} ('{existing.proposed_title}')"
            )
            return True, existing.proposed_title, composite_score

    return False, None, 0.0


def evaluate_and_persist_topic(
    db: Session,
    candidate: TopicProposal,
    destination_id: Optional[int] = None,
) -> Tuple[Optional[Topic], bool, str]:
    """
    Two-stage pipeline:
      1. Level 1: Canonical check
      2. Level 2: Semantic duplicate check
      3. Persistence: Inserts novel topic into PostgreSQL with transaction safety.
      
    Returns:
      (topic_record, is_approved_and_saved, evaluation_message)
    """
    # Stage 1: Level 1 Exact Canonical Check
    is_exact_dup, canonical_key = check_level1_canonical_duplicate(
        db=db,
        destination=candidate.destination,
        category=candidate.category,
        unique_angle=candidate.unique_angle,
    )
    if is_exact_dup:
        return None, False, f"Rejected: Level 1 exact canonical duplicate ({canonical_key})"

    # Stage 2: Level 2 Semantic Overlap Check
    is_semantic_dup, matched_title, score = check_level2_semantic_duplicate(
        db=db,
        candidate=candidate,
        threshold=0.40,
    )
    if is_semantic_dup:
        return None, False, f"Rejected: Level 2 semantic duplicate of '{matched_title}' (similarity: {score})"

    # Stage 3: Save to PostgreSQL
    topic, created = save_topic_if_unique(
        db=db,
        destination=candidate.destination,
        country=candidate.country,
        category=candidate.category,
        proposed_title=candidate.proposed_title,
        unique_angle=candidate.unique_angle,
        discovery_source=candidate.discovery_source,
        destination_id=destination_id,
    )

    if created:
        return topic, True, f"Approved & Saved as Topic ID {topic.id}"
    else:
        return topic, False, f"Rejected: Database unique constraint collision ({canonical_key})"
