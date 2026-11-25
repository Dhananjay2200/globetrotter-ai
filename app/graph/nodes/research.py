"""
GlobeTrotter AI - LangGraph Research Node.
Orchestrates research gathering, factual evidence extraction, source citation,
and PostgreSQL persistence for discovered topics.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models import Topic, ResearchSource
from app.services.research_service import (
    gather_multi_source_data,
    synthesize_factual_evidence,
    StructuredEvidence,
)
from app.utils.logging import logger


def conduct_topic_research(
    db: Session,
    topic_id: int,
) -> Dict[str, Any]:
    """
    Executes end-to-end research for a given topic ID:
    1. Retrieves topic metadata from database.
    2. Gathers external evidence from Tavily and Wikipedia APIs.
    3. Synthesizes structured, fact-checked evidence points.
    4. Persists each individual source citation into the 'research_sources' table.
    5. Advances topic status to 'researched'.
    """
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise ValueError(f"Topic with ID {topic_id} does not exist.")

    logger.info(f"[*] Starting research for Topic ID {topic.id}: '{topic.proposed_title}' ({topic.destination}, {topic.country})")
    topic.status = "researching"
    db.commit()

    # Step 1: Collect multi-source reference documents
    raw_sources = gather_multi_source_data(
        destination=topic.destination,
        country=topic.country,
        unique_angle=topic.unique_angle,
    )

    if not raw_sources:
        topic.status = "discovered"  # Revert status
        db.commit()
        raise RuntimeError(f"Could not retrieve reliable research sources for '{topic.destination}'.")

    # Step 2: Synthesize structured evidence using LLM
    evidence: StructuredEvidence = synthesize_factual_evidence(
        destination=topic.destination,
        country=topic.country,
        category=topic.category,
        unique_angle=topic.unique_angle,
        raw_sources=raw_sources,
    )

    # Step 3: Persist citations in research_sources table
    persisted_source_ids = []
    for src in raw_sources:
        # Avoid duplicate source URLs for the same topic
        existing_src = db.query(ResearchSource).filter(
            ResearchSource.topic_id == topic.id,
            ResearchSource.url == src.url,
        ).first()

        if not existing_src:
            db_source = ResearchSource(
                topic_id=topic.id,
                article_id=None,  # Linked later during article writing (Phase 5)
                url=src.url,
                publisher=src.publisher,
                title=src.title,
                evidence_excerpt=src.content[:2000],
            )
            db.add(db_source)
            db.commit()
            db.refresh(db_source)
            persisted_source_ids.append(db_source.id)
        else:
            persisted_source_ids.append(existing_src.id)

    # Step 4: Advance topic status
    topic.status = "researched"
    db.commit()
    db.refresh(topic)

    logger.info(
        f"[+] Completed research for Topic ID {topic.id}. "
        f"Persisted {len(persisted_source_ids)} citations. Status updated to 'researched'."
    )

    return {
        "topic_id": topic.id,
        "destination": topic.destination,
        "country": topic.country,
        "status": topic.status,
        "evidence": evidence.model_dump(),
        "total_sources": len(persisted_source_ids),
        "source_ids": persisted_source_ids,
    }
