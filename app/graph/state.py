"""
GlobeTrotter AI - LangGraph Shared State Definition.
Maintains typed state across all pipeline stages from topic discovery to publication.
"""

from typing import TypedDict, List, Dict, Any, Optional


class GlobeTrotterState(TypedDict, total=False):
    """
    Central state container traversing the LangGraph workflow.
    Each node consumes and enriches this state.
    """
    # 1. Topic Discovery & Deduplication State
    topic_id: Optional[int]
    destination: str
    country: str
    region: str
    category: str
    proposed_title: str
    unique_angle: str
    canonical_key: Optional[str]
    is_duplicate: bool
    deduplication_reason: Optional[str]

    # 2. Research & Evidence State
    evidence: Dict[str, Any]
    source_ids: List[int]
    citations: List[Dict[str, str]]

    # 3. Article Authoring State
    article_id: Optional[int]
    article_title: Optional[str]
    slug: Optional[str]
    summary: Optional[str]
    body_markdown: Optional[str]
    word_count: int
    sections_detected: List[str]

    # 4. SEO Optimization State
    seo_metadata: Dict[str, Any]
    seo_title: Optional[str]
    meta_description: Optional[str]
    main_keyword: Optional[str]
    secondary_keywords: List[str]
    tags: List[str]

    # 5. Media & Licensing State
    image_ids: List[int]
    featured_image_url: Optional[str]
    images_count: int

    # 6. Quality Gate & Revision Loop State
    quality_score: Optional[float]
    passes_quality: bool
    quality_threshold: float
    dimension_scores: Dict[str, float]
    deficiencies: List[str]
    revision_recommendations: List[str]
    revision_attempts: int
    max_revisions: int

    # 7. Workflow Metadata & Execution Logging
    status: str  # discovered, researching, written, seo_optimized, images_attached, quality_passed, needs_review, duplicate_rejected, failed
    current_node: str
    logs: List[str]
    error_message: Optional[str]
