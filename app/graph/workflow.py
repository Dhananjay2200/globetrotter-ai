"""
GlobeTrotter AI - LangGraph Orchestration Workflow.
Coordinates all autonomous agents across the end-to-end lifecycle:
  1. Topic Discovery (AI or user-specified)
  2. Level 1 & Level 2 Deduplication Gate
  3. Evidence-Backed Research & Citations
  4. 12-Section Editorial Long-Form Writing
  5. Multi-Attribute SEO Optimization
  6. Permitted Media Discovery & Attribution
  7. 11-Dimension Quality Gate & Corrective Revision Loop
"""

import uuid
import re
from typing import Dict, Any, Optional, List
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.database.session import SessionLocal
from app.database.models import Topic, Article, ResearchSource, ImageAsset
from app.graph.state import GlobeTrotterState
from app.services.discovery_service import (
    discover_topics,
    get_next_balanced_region_and_category,
    TopicProposal,
    GLOBAL_REGIONS,
    TOURISM_CATEGORIES,
)
from app.graph.nodes.duplicate_check import evaluate_and_persist_topic
from app.graph.nodes.research import conduct_topic_research
from app.graph.nodes.writer import write_article_for_topic
from app.graph.nodes.seo import optimize_article_seo
from app.graph.nodes.image_search import discover_and_attach_images
from app.services.evaluator_service import (
    evaluate_article_quality,
    revise_article_content,
    QualityEvaluationResult,
)
from app.services.writer_service import count_words
from app.utils.logging import logger


# =====================================================================
# Node 1: Topic Discovery Node
# =====================================================================

def discover_node(state: GlobeTrotterState) -> Dict[str, Any]:
    """
    Initializes topic state. If an existing topic_id or destination parameters
    are provided, adopts them; otherwise invokes the AI Discovery Agent.
    """
    logs = list(state.get("logs", []))
    logs.append("[Node: discover_node] Initializing topic parameters...")

    # Case A: Topic ID provided directly
    topic_id = state.get("topic_id")
    if topic_id:
        db = SessionLocal()
        try:
            topic = db.query(Topic).filter(Topic.id == topic_id).first()
            if topic:
                logs.append(f"[discover_node] Using existing Topic ID {topic.id}: '{topic.proposed_title}'")
                return {
                    "topic_id": topic.id,
                    "destination": topic.destination,
                    "country": topic.country,
                    "category": topic.category,
                    "proposed_title": topic.proposed_title,
                    "unique_angle": topic.unique_angle,
                    "canonical_key": topic.canonical_key,
                    "status": "discovered",
                    "current_node": "discover_node",
                    "logs": logs,
                }
        finally:
            db.close()

    # Case B: Destination and title provided manually
    destination = state.get("destination")
    proposed_title = state.get("proposed_title")
    if destination and proposed_title:
        logs.append(f"[discover_node] Using user-specified topic for: '{destination}'")
        return {
            "destination": destination,
            "country": state.get("country", "Global"),
            "region": state.get("region", "Global"),
            "category": state.get("category", "Historical Monuments & Heritage Sites"),
            "proposed_title": proposed_title,
            "unique_angle": state.get("unique_angle", "Comprehensive travel and cultural guide"),
            "status": "discovered",
            "current_node": "discover_node",
            "logs": logs,
        }

    # Case C: Autonomous AI Topic Discovery
    db = SessionLocal()
    try:
        if not state.get("region") or not state.get("category"):
            balanced_region, balanced_category = get_next_balanced_region_and_category(db)
            region = state.get("region") or balanced_region
            category = state.get("category") or balanced_category
        else:
            region = state["region"]
            category = state["category"]

        logs.append(f"[discover_node] Autonomous Global Rotation: Region='{region}', Category='{category}'...")

        proposals = discover_topics(
            db=db,
            count=1,
            target_region=region,
            target_category=category,
        )

        if not proposals:
            # Fallback proposal
            proposal = TopicProposal(
                destination="Kyoto Historical Temples",
                country="Japan",
                region="East & Southeast Asia",
                category="Historical Monuments & Heritage Sites",
                proposed_title="The Zen Temples of Kyoto: Timeless Architecture and Gardens",
                unique_angle="Exploring 1,200 years of Zen philosophy through historic moss gardens",
                discovery_source="autonomous_workflow",
            )
        else:
            proposal = proposals[0]

        logs.append(f"[discover_node] Discovered: '{proposal.proposed_title}' ({proposal.destination}, {proposal.country})")
        return {
            "destination": proposal.destination,
            "country": proposal.country,
            "region": proposal.region,
            "category": proposal.category,
            "proposed_title": proposal.proposed_title,
            "unique_angle": proposal.unique_angle,
            "status": "discovered",
            "current_node": "discover_node",
            "logs": logs,
        }
    finally:
        db.close()


# =====================================================================
# Node 2: Deduplication Gate Node
# =====================================================================

def deduplicate_node(state: GlobeTrotterState) -> Dict[str, Any]:
    """
    Evaluates candidate topic against Level 1 (Canonical) and Level 2 (Semantic)
    deduplication gates. Rejects duplicates or commits novel topic to PostgreSQL.
    """
    logs = list(state.get("logs", []))
    logs.append("[Node: deduplicate_node] Evaluating candidate for deduplication...")

    # If topic_id already existed and is confirmed, pass through
    topic_id = state.get("topic_id")
    if topic_id:
        logs.append(f"[deduplicate_node] Topic ID {topic_id} already registered. Skipping duplicate check.")
        return {
            "is_duplicate": False,
            "status": "deduplicated",
            "current_node": "deduplicate_node",
            "logs": logs,
        }

    proposal = TopicProposal(
        destination=state["destination"],
        country=state.get("country", "Global"),
        region=state.get("region", "Global"),
        category=state.get("category", "General Tourism"),
        proposed_title=state["proposed_title"],
        unique_angle=state.get("unique_angle", "Comprehensive exploration"),
        discovery_source="workflow_run",
    )

    db = SessionLocal()
    try:
        topic_record, is_approved, eval_msg = evaluate_and_persist_topic(db=db, candidate=proposal)

        if not is_approved:
            logs.append(f"[deduplicate_node] DUPLICATE REJECTED: {eval_msg}")
            return {
                "is_duplicate": True,
                "deduplication_reason": eval_msg,
                "status": "duplicate_rejected",
                "current_node": "deduplicate_node",
                "logs": logs,
            }

        logs.append(f"[deduplicate_node] APPROVED: {eval_msg} (Canonical Key: {topic_record.canonical_key})")
        return {
            "topic_id": topic_record.id,
            "canonical_key": topic_record.canonical_key,
            "is_duplicate": False,
            "status": "deduplicated",
            "current_node": "deduplicate_node",
            "logs": logs,
        }
    finally:
        db.close()


# =====================================================================
# Node 3: Research Agent Node
# =====================================================================

def research_node(state: GlobeTrotterState) -> Dict[str, Any]:
    """
    Gathers multi-source research and factual citations for the approved topic.
    """
    logs = list(state.get("logs", []))
    topic_id = state["topic_id"]
    logs.append(f"[Node: research_node] Conducting factual research for Topic ID {topic_id}...")

    db = SessionLocal()
    try:
        research_result = conduct_topic_research(db=db, topic_id=topic_id)
        evidence = research_result.get("evidence", {})
        source_ids = research_result.get("source_ids", [])

        # Fetch citation summaries
        sources = db.query(ResearchSource).filter(ResearchSource.id.in_(source_ids)).all()
        citations = [
            {"publisher": s.publisher, "title": s.title, "url": s.url}
            for s in sources
        ]

        logs.append(f"[research_node] Gathered {len(citations)} authoritative citations.")
        return {
            "evidence": evidence,
            "source_ids": source_ids,
            "citations": citations,
            "status": "researched",
            "current_node": "research_node",
            "logs": logs,
        }
    finally:
        db.close()


# =====================================================================
# Node 4: Article Writer Node
# =====================================================================

def writer_node(state: GlobeTrotterState) -> Dict[str, Any]:
    """
    Drafts outline and long-form 1,200–1,800 word Markdown article with all 12 sections.
    """
    logs = list(state.get("logs", []))
    topic_id = state["topic_id"]
    logs.append(f"[Node: writer_node] Generating 12-section long-form article for Topic ID {topic_id}...")

    db = SessionLocal()
    try:
        article = write_article_for_topic(db=db, topic_id=topic_id)
        sections = re.findall(r"^##\s+(.+)$", article.body_markdown or "", flags=re.MULTILINE)

        logs.append(
            f"[writer_node] Article ID {article.id} drafted successfully. "
            f"Word count: {article.word_count}. Sections: {len(sections)}."
        )
        return {
            "article_id": article.id,
            "article_title": article.title,
            "slug": article.slug,
            "summary": article.summary,
            "body_markdown": article.body_markdown,
            "word_count": article.word_count,
            "sections_detected": sections,
            "status": "written",
            "current_node": "writer_node",
            "logs": logs,
        }
    finally:
        db.close()


# =====================================================================
# Node 5: SEO Optimization Node
# =====================================================================

def seo_node(state: GlobeTrotterState) -> Dict[str, Any]:
    """
    Optimizes SEO title, meta description, keywords, tags, and ensures clean slug.
    """
    logs = list(state.get("logs", []))
    article_id = state["article_id"]
    logs.append(f"[Node: seo_node] Synthesizing SEO metadata for Article ID {article_id}...")

    db = SessionLocal()
    try:
        article, seo_meta = optimize_article_seo(db=db, article_id=article_id)

        logs.append(
            f"[seo_node] SEO Title: '{article.seo_title}' ({len(article.seo_title)} chars) | "
            f"Slug: '{article.slug}' | Keyword: '{article.main_keyword}'"
        )
        return {
            "seo_metadata": seo_meta.model_dump(),
            "seo_title": article.seo_title,
            "meta_description": article.seo_description,
            "main_keyword": article.main_keyword,
            "secondary_keywords": seo_meta.secondary_keywords,
            "tags": seo_meta.tags,
            "slug": article.slug,
            "summary": article.summary,
            "status": "seo_optimized",
            "current_node": "seo_node",
            "logs": logs,
        }
    finally:
        db.close()


# =====================================================================
# Node 6: Image Discovery & Licensing Node
# =====================================================================

def image_node(state: GlobeTrotterState) -> Dict[str, Any]:
    """
    Searches permitted repositories (Wikimedia Commons), verifies licenses,
    formats legal attributions, and commits media assets.
    """
    logs = list(state.get("logs", []))
    article_id = state["article_id"]
    logs.append(f"[Node: image_node] Discovering verified media assets for Article ID {article_id}...")

    db = SessionLocal()
    try:
        assets = discover_and_attach_images(db=db, article_id=article_id, target_count=3)
        featured_url = assets[0].image_url if assets else None
        image_ids = [a.id for a in assets]

        logs.append(f"[image_node] Attached {len(assets)} verified licensed images (Featured ID: {assets[0].id if assets else 'None'}).")
        return {
            "image_ids": image_ids,
            "featured_image_url": featured_url,
            "images_count": len(assets),
            "status": "images_attached",
            "current_node": "image_node",
            "logs": logs,
        }
    finally:
        db.close()


# =====================================================================
# Node 7: Quality Gate Node
# =====================================================================

def quality_node(state: GlobeTrotterState) -> Dict[str, Any]:
    """
    Scores article against the 11-dimension evaluation rubric via NVIDIA NIM.
    Sets status to 'quality_passed' if score >= threshold, or triggers revision logic.
    """
    logs = list(state.get("logs", []))
    article_id = state["article_id"]
    threshold = state.get("quality_threshold", 8.0)
    max_revisions = state.get("max_revisions", 1)
    current_attempt = state.get("revision_attempts", 0)

    logs.append(
        f"[Node: quality_node] Evaluating Article ID {article_id} "
        f"(Threshold: {threshold}/10, Attempt: {current_attempt + 1})..."
    )

    db = SessionLocal()
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        topic = db.query(Topic).filter(Topic.id == article.topic_id).first()
        sources = db.query(ResearchSource).filter(ResearchSource.article_id == article.id).all()
        images = db.query(ImageAsset).filter(ImageAsset.article_id == article.id).all()

        sources_data = [{"publisher": s.publisher, "title": s.title, "url": s.url} for s in sources]
        images_data = [{"provider": img.provider, "license_name": img.license_name, "alt_text": img.alt_text} for img in images]
        seo_meta = {
            "seo_title": article.seo_title,
            "seo_description": article.seo_description,
            "main_keyword": article.main_keyword,
            "slug": article.slug,
        }

        eval_result: QualityEvaluationResult = evaluate_article_quality(
            article_title=article.title,
            destination=topic.destination,
            country=topic.country,
            category=topic.category,
            unique_angle=topic.unique_angle,
            body_markdown=article.body_markdown,
            word_count=article.word_count,
            seo_metadata=seo_meta,
            sources=sources_data,
            images=images_data,
            threshold=threshold,
        )

        logs.append(
            f"[quality_node] Quality Score: {eval_result.overall_score}/10.0 "
            f"(Passed: {eval_result.passes_threshold})"
        )

        if eval_result.passes_threshold:
            article.status = "quality_passed"
            article.quality_score = eval_result.overall_score
            db.commit()
            logs.append(f"[quality_node] PASSED Quality Gate! Article ready for publication.")
            return {
                "quality_score": eval_result.overall_score,
                "passes_quality": True,
                "dimension_scores": eval_result.dimension_scores,
                "deficiencies": eval_result.deficiencies,
                "revision_recommendations": eval_result.revision_recommendations,
                "status": "quality_passed",
                "current_node": "quality_node",
                "logs": logs,
            }

        # Failed threshold
        if current_attempt < max_revisions:
            logs.append(
                f"[quality_node] Score {eval_result.overall_score} < {threshold}. "
                f"Deficiencies detected: {len(eval_result.deficiencies)}. Triggering revision node..."
            )
            return {
                "quality_score": eval_result.overall_score,
                "passes_quality": False,
                "dimension_scores": eval_result.dimension_scores,
                "deficiencies": eval_result.deficiencies,
                "revision_recommendations": eval_result.revision_recommendations,
                "status": "revision_needed",
                "current_node": "quality_node",
                "logs": logs,
            }
        else:
            article.status = "needs_review"
            article.quality_score = eval_result.overall_score
            db.commit()
            logs.append(
                f"[quality_node] Exhausted revision retries ({current_attempt}/{max_revisions}). "
                f"Flagged as 'needs_review' to prevent automatic publication."
            )
            return {
                "quality_score": eval_result.overall_score,
                "passes_quality": False,
                "dimension_scores": eval_result.dimension_scores,
                "deficiencies": eval_result.deficiencies,
                "revision_recommendations": eval_result.revision_recommendations,
                "status": "needs_review",
                "current_node": "quality_node",
                "logs": logs,
            }
    finally:
        db.close()


# =====================================================================
# Node 8: Revision Node
# =====================================================================

def revision_node(state: GlobeTrotterState) -> Dict[str, Any]:
    """
    Executes automated corrective revision using LLM based on specific rubric deficiencies.
    Updates the Article record in PostgreSQL and increments revision counter.
    """
    logs = list(state.get("logs", []))
    article_id = state["article_id"]
    current_attempts = state.get("revision_attempts", 0) + 1
    logs.append(f"[Node: revision_node] Executing corrective revision (Attempt {current_attempts})...")

    db = SessionLocal()
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        topic = db.query(Topic).filter(Topic.id == article.topic_id).first()

        revised_markdown = revise_article_content(
            article_title=article.title,
            destination=topic.destination,
            country=topic.country,
            current_markdown=article.body_markdown,
            deficiencies=state.get("deficiencies", []),
            recommendations=state.get("revision_recommendations", []),
        )

        article.body_markdown = revised_markdown
        article.word_count = count_words(revised_markdown)
        db.commit()
        db.refresh(article)

        logs.append(f"[revision_node] Revision completed. New word count: {article.word_count}.")
        return {
            "body_markdown": article.body_markdown,
            "word_count": article.word_count,
            "revision_attempts": current_attempts,
            "status": "revised",
            "current_node": "revision_node",
            "logs": logs,
        }
    finally:
        db.close()


# =====================================================================
# Conditional Routing Functions
# =====================================================================

def route_after_deduplication(state: GlobeTrotterState) -> str:
    """
    Routes to END if topic is duplicate; otherwise proceeds to research.
    """
    if state.get("is_duplicate", False):
        logger.info("[Workflow Router] Topic flagged as duplicate. Terminating pipeline.")
        return "duplicate"
    return "proceed"


def route_after_quality_check(state: GlobeTrotterState) -> str:
    """
    Routes to END if article passes quality threshold.
    Routes to revision_node if retries remain; otherwise halts as needs_review.
    """
    if state.get("passes_quality", False):
        logger.info("[Workflow Router] Article passed quality threshold! Completing workflow.")
        return "passed"

    max_revisions = state.get("max_revisions", 1)
    current_attempts = state.get("revision_attempts", 0)

    if current_attempts < max_revisions:
        logger.info(f"[Workflow Router] Article needs revision (Attempt {current_attempts}/{max_revisions}).")
        return "revise"

    logger.warning("[Workflow Router] Max revisions reached without passing threshold. Halting.")
    return "exhausted"


# =====================================================================
# StateGraph Construction & Compilation
# =====================================================================

def build_globetrotter_workflow() -> Any:
    """
    Constructs and compiles the full GlobeTrotter AI LangGraph workflow.
    """
    workflow = StateGraph(GlobeTrotterState)

    # 1. Register all execution nodes
    workflow.add_node("discover_node", discover_node)
    workflow.add_node("deduplicate_node", deduplicate_node)
    workflow.add_node("research_node", research_node)
    workflow.add_node("writer_node", writer_node)
    workflow.add_node("seo_node", seo_node)
    workflow.add_node("image_node", image_node)
    workflow.add_node("quality_node", quality_node)
    workflow.add_node("revision_node", revision_node)

    # 2. Sequential Discovery -> Deduplication
    workflow.add_edge(START, "discover_node")
    workflow.add_edge("discover_node", "deduplicate_node")

    # 3. Conditional Edge: Deduplication Gate
    workflow.add_conditional_edges(
        "deduplicate_node",
        route_after_deduplication,
        {
            "duplicate": END,
            "proceed": "research_node",
        },
    )

    # 4. Sequential Core Pipeline: Research -> Writer -> SEO -> Images -> Quality
    workflow.add_edge("research_node", "writer_node")
    workflow.add_edge("writer_node", "seo_node")
    workflow.add_edge("seo_node", "image_node")
    workflow.add_edge("image_node", "quality_node")

    # 5. Conditional Edge: Quality Gate & Revision Loop
    workflow.add_conditional_edges(
        "quality_node",
        route_after_quality_check,
        {
            "passed": END,
            "revise": "revision_node",
            "exhausted": END,
        },
    )

    # 6. Revision routes back to Quality Gate
    workflow.add_edge("revision_node", "quality_node")

    # Compile with memory checkpointer
    checkpointer = MemorySaver()
    app = workflow.compile(checkpointer=checkpointer)
    return app


# Singleton compiled graph instance
globetrotter_graph = build_globetrotter_workflow()


# =====================================================================
# High-Level Execution Helper
# =====================================================================

def run_globetrotter_pipeline(
    initial_state: Optional[Dict[str, Any]] = None,
    thread_id: Optional[str] = None,
) -> GlobeTrotterState:
    """
    Convenience function to execute the full LangGraph pipeline end-to-end.
    """
    state_payload = initial_state or {}
    tid = thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": tid}}

    # Initialize default configuration fields
    if "quality_threshold" not in state_payload:
        state_payload["quality_threshold"] = 8.0
    if "max_revisions" not in state_payload:
        state_payload["max_revisions"] = 1
    if "revision_attempts" not in state_payload:
        state_payload["revision_attempts"] = 0
    if "logs" not in state_payload:
        state_payload["logs"] = []

    logger.info(f"[*] Commencing GlobeTrotter LangGraph Pipeline (Thread ID: {tid})...")
    final_state = globetrotter_graph.invoke(state_payload, config=config)
    logger.info(f"[+] GlobeTrotter Pipeline Completed with Status: '{final_state.get('status')}'")
    return final_state
