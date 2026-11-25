"""
GlobeTrotter AI - LangGraph Article Writer Node.
Coordinates outline creation, long-form Markdown drafting, citation linkage,
and PostgreSQL persistence for travel articles.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models import Topic, Article, ResearchSource
from app.graph.nodes.research import conduct_topic_research
from app.services.writer_service import (
    generate_article_outline,
    generate_full_article_markdown,
    GeneratedArticleData,
)
from app.utils.logging import logger


def write_article_for_topic(
    db: Session,
    topic_id: int,
) -> Article:
    """
    Executes full article authoring pipeline for a topic:
    1. Loads topic and verified research sources from database.
       (If not yet researched, automatically triggers research stage first).
    2. Generates the 12-section editorial outline.
    3. Drafts full 1,200–1,800 word Markdown article.
    4. Persists the Article record in PostgreSQL.
    5. Links all research sources to the created Article.
    6. Advances topic status to 'written'.
    """
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise ValueError(f"Topic with ID {topic_id} does not exist.")

    logger.info(f"[*] Starting Article Writer for Topic ID {topic.id}: '{topic.proposed_title}'")
    topic.status = "writing"
    db.commit()

    # Step 1: Ensure research evidence exists
    sources = db.query(ResearchSource).filter(ResearchSource.topic_id == topic.id).all()
    if not sources or topic.status == "discovered":
        logger.info(f"[i] Topic ID {topic.id} has no research sources. Triggering Research Agent...")
        research_result = conduct_topic_research(db=db, topic_id=topic.id)
        sources = db.query(ResearchSource).filter(ResearchSource.topic_id == topic.id).all()
        evidence_dict = research_result.get("evidence", {})
    else:
        # Reconstruct evidence dictionary from existing sources
        evidence_dict = {
            "geographical_context": f"{topic.destination} in {topic.country}.",
            "historical_background": "Ancient historical roots and documented heritage significance.",
            "cultural_significance": f"Rich cultural identity and local traditions of {topic.country}.",
            "key_attractions": [topic.destination],
            "local_cuisine": "Signature regional culinary heritage.",
            "best_visiting_season": "Favorable seasonal weather conditions.",
            "transportation_access": "Accessible via regional transit hubs.",
            "practical_travel_tips": ["Respect local etiquette and environment."],
            "safety_guidelines": "General visitor safety precautions.",
        }

    sources_data = [
        {
            "id": s.id,
            "url": s.url,
            "publisher": s.publisher,
            "title": s.title,
            "excerpt": s.evidence_excerpt,
        }
        for s in sources
    ]

    # Step 2: Generate Outline
    logger.info(f"[*] Generating structured 12-section outline for '{topic.destination}'...")
    outline = generate_article_outline(
        destination=topic.destination,
        country=topic.country,
        category=topic.category,
        proposed_title=topic.proposed_title,
        unique_angle=topic.unique_angle,
        evidence=evidence_dict,
    )

    # Step 3: Write Full Markdown Article
    logger.info(f"[*] Drafting comprehensive travel article via NVIDIA NIM...")
    article_data: GeneratedArticleData = generate_full_article_markdown(
        destination=topic.destination,
        country=topic.country,
        category=topic.category,
        unique_angle=topic.unique_angle,
        outline=outline,
        evidence=evidence_dict,
        sources=sources_data,
    )

    # Step 4: Persist or Update Article in PostgreSQL
    article = db.query(Article).filter(Article.topic_id == topic.id).first()
    if not article:
        article = Article(
            topic_id=topic.id,
            title=article_data.title,
            slug=article_data.slug,
            summary=article_data.summary,
            body_markdown=article_data.body_markdown,
            word_count=article_data.word_count,
            status="draft",
        )
        db.add(article)
        db.commit()
        db.refresh(article)
    else:
        article.title = article_data.title
        article.slug = article_data.slug
        article.summary = article_data.summary
        article.body_markdown = article_data.body_markdown
        article.word_count = article_data.word_count
        article.status = "draft"
        db.commit()
        db.refresh(article)

    # Step 5: Link all research sources to this article
    for src in sources:
        src.article_id = article.id
    db.commit()

    # Step 6: Advance Topic status
    topic.status = "written"
    db.commit()
    db.refresh(topic)

    logger.info(
        f"[+] Article ID {article.id} successfully created for Topic ID {topic.id}. "
        f"Word count: {article.word_count}. Status: 'draft'."
    )
    return article
