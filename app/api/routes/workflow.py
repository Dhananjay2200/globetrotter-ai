"""
GlobeTrotter AI - LangGraph Workflow API Router.
Provides endpoints to trigger, inspect, and monitor autonomous end-to-end pipelines.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from app.graph.workflow import run_globetrotter_pipeline, globetrotter_graph
from app.utils.logging import logger

router = APIRouter(prefix="/workflow", tags=["LangGraph Workflow"])


class WorkflowRunRequest(BaseModel):
    """Payload to trigger the autonomous workflow."""
    topic_id: Optional[int] = Field(None, description="Existing Topic ID to process")
    destination: Optional[str] = Field(None, description="Target destination (e.g. Banff, Kyoto)")
    country: Optional[str] = Field(None, description="Target country")
    region: Optional[str] = Field(None, description="Target region")
    category: Optional[str] = Field(None, description="Target tourism category")
    proposed_title: Optional[str] = Field(None, description="Custom article title")
    unique_angle: Optional[str] = Field(None, description="Distinct editorial focus")
    quality_threshold: Optional[float] = Field(8.0, ge=1.0, le=10.0, description="Minimum score to pass quality gate")
    max_revisions: Optional[int] = Field(1, ge=0, le=3, description="Maximum automated revision attempts")


class WorkflowRunResponse(BaseModel):
    """Response payload returned by the workflow runner."""
    status: str
    is_duplicate: bool
    topic_id: Optional[int] = None
    destination: Optional[str] = None
    country: Optional[str] = None
    article_id: Optional[int] = None
    article_title: Optional[str] = None
    slug: Optional[str] = None
    word_count: Optional[int] = None
    quality_score: Optional[float] = None
    passes_quality: Optional[bool] = None
    dimension_scores: Optional[Dict[str, float]] = None
    seo_title: Optional[str] = None
    featured_image_url: Optional[str] = None
    images_count: Optional[int] = None
    revision_attempts: int = 0
    logs: List[str] = []


@router.post("/run", response_model=WorkflowRunResponse)
def execute_workflow(request: WorkflowRunRequest):
    """
    Executes the full LangGraph GlobeTrotter AI pipeline end-to-end:
    Discovery -> Deduplication -> Research -> Writer -> SEO -> Media -> Quality Gate -> Revision.
    """
    try:
        initial_payload = {k: v for k, v in request.model_dump().items() if v is not None}
        final_state = run_globetrotter_pipeline(initial_state=initial_payload)

        return WorkflowRunResponse(
            status=final_state.get("status", "unknown"),
            is_duplicate=final_state.get("is_duplicate", False),
            topic_id=final_state.get("topic_id"),
            destination=final_state.get("destination"),
            country=final_state.get("country"),
            article_id=final_state.get("article_id"),
            article_title=final_state.get("article_title"),
            slug=final_state.get("slug"),
            word_count=final_state.get("word_count"),
            quality_score=final_state.get("quality_score"),
            passes_quality=final_state.get("passes_quality"),
            dimension_scores=final_state.get("dimension_scores"),
            seo_title=final_state.get("seo_title"),
            featured_image_url=final_state.get("featured_image_url"),
            images_count=final_state.get("images_count"),
            revision_attempts=final_state.get("revision_attempts", 0),
            logs=final_state.get("logs", []),
        )
    except Exception as exc:
        logger.error(f"Workflow execution failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(exc)}")


@router.get("/stages")
def get_workflow_stages():
    """
    Returns pipeline architecture, node definitions, and routing rules.
    """
    return {
        "framework": "LangGraph (StateGraph)",
        "state_schema": "GlobeTrotterState",
        "nodes": [
            {
                "id": "discover_node",
                "name": "Topic Discovery Agent",
                "description": "Explores worldwide tourist destinations and angles across 10 global regions and 13 categories using NVIDIA NIM.",
            },
            {
                "id": "deduplicate_node",
                "name": "Deduplication Gate (Level 1 & Level 2)",
                "description": "Enforces exact canonical key uniqueness and semantic overlap thresholds. Rejects duplicates instantly.",
            },
            {
                "id": "research_node",
                "name": "Research Agent",
                "description": "Gathers authoritative evidence from Wikipedia and Tavily, synthesizing structured factual points with publisher attribution.",
            },
            {
                "id": "writer_node",
                "name": "Article Writer Agent",
                "description": "Two-stage editorial generation: builds a 12-section outline and writes long-form (1,200–1,800 words) Markdown.",
            },
            {
                "id": "seo_node",
                "name": "SEO Optimization Agent",
                "description": "Synthesizes 50–60 char titles, 140–160 char meta descriptions, unique slugs, keywords, and tags.",
            },
            {
                "id": "image_node",
                "name": "Image Discovery & Licensing Agent",
                "description": "Discovers CC0 and Public Domain images via Wikimedia Commons with automated legal attribution and alt text.",
            },
            {
                "id": "quality_node",
                "name": "Quality Gate Node",
                "description": "Scores articles across 11 dimensions via NVIDIA NIM. Only articles scoring >= 8.0/10 qualify for publishing.",
            },
            {
                "id": "revision_node",
                "name": "Corrective Revision Node",
                "description": "Applies targeted revisions based on identified rubric deficiencies before re-evaluating.",
            },
        ],
        "conditional_routes": [
            {
                "from": "deduplicate_node",
                "condition": "is_duplicate == True",
                "target": "END (duplicate_rejected)",
            },
            {
                "from": "deduplicate_node",
                "condition": "is_duplicate == False",
                "target": "research_node",
            },
            {
                "from": "quality_node",
                "condition": "passes_quality == True",
                "target": "END (quality_passed)",
            },
            {
                "from": "quality_node",
                "condition": "passes_quality == False and retries < max_retries",
                "target": "revision_node -> quality_node",
            },
            {
                "from": "quality_node",
                "condition": "retries >= max_retries",
                "target": "END (needs_review)",
            },
        ],
    }
