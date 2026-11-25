"""
GlobeTrotter AI - LangGraph Quality Evaluation & Routing Node.
Scores articles against the 11-point rubric, triggers corrective revision loops,
enforces retry limits, and sets article status to 'quality_passed' or 'needs_review'.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models import Article, Topic, ResearchSource, ImageAsset
from app.services.evaluator_service import (
    evaluate_article_quality,
    revise_article_content,
    QualityEvaluationResult,
)
from app.services.writer_service import count_words
from app.utils.logging import logger


def evaluate_and_route_article(
    db: Session,
    article_id: int,
    max_retries: int = 1,
    threshold: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Executes the Quality Evaluation & Routing Node:
    1. Loads article, topic, research citations, and media assets.
    2. Scores article on the 11-dimension rubric.
    3. If passes threshold: marks 'quality_passed'.
    4. If fails threshold: executes automated revision loop (up to max_retries).
    5. If still fails: marks 'needs_review' (preventing automatic publication).
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise ValueError(f"Article with ID {article_id} does not exist.")

    topic = db.query(Topic).filter(Topic.id == article.topic_id).first()
    if not topic:
        raise ValueError(f"Associated Topic for Article ID {article_id} not found.")

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

    logger.info(f"[*] Commencing Quality Evaluation for Article ID {article.id}: '{article.title}'")

    attempt = 0
    final_evaluation: Optional[QualityEvaluationResult] = None

    while attempt <= max_retries:
        eval_result = evaluate_article_quality(
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
        final_evaluation = eval_result

        # Success Case
        if eval_result.passes_threshold:
            article.status = "quality_passed"
            article.quality_score = eval_result.overall_score
            db.commit()
            db.refresh(article)
            logger.info(f"[+] Article ID {article.id} PASSED Quality Gate! Score: {eval_result.overall_score}/10.")
            return {
                "article_id": article.id,
                "status": article.status,
                "quality_score": eval_result.overall_score,
                "threshold_used": eval_result.threshold_used,
                "passes_threshold": True,
                "attempts_made": attempt + 1,
                "dimension_scores": eval_result.dimension_scores,
                "strengths": eval_result.strengths,
                "deficiencies": eval_result.deficiencies,
                "revision_recommendations": eval_result.revision_recommendations,
            }

        # Failure Case: Check if retries remaining
        attempt += 1
        if attempt <= max_retries:
            logger.warning(
                f"[!] Article ID {article.id} scored {eval_result.overall_score} < {eval_result.threshold_used}. "
                f"Triggering automated revision loop (Attempt {attempt}/{max_retries})..."
            )
            revised_markdown = revise_article_content(
                article_title=article.title,
                destination=topic.destination,
                country=topic.country,
                current_markdown=article.body_markdown,
                deficiencies=eval_result.deficiencies,
                recommendations=eval_result.revision_recommendations,
            )
            article.body_markdown = revised_markdown
            article.word_count = count_words(revised_markdown)
            db.commit()
            db.refresh(article)

    # Exhausted retries without meeting threshold
    article.status = "needs_review"
    article.quality_score = final_evaluation.overall_score if final_evaluation else 0.0
    db.commit()
    db.refresh(article)

    logger.warning(
        f"[-] Article ID {article.id} failed quality gate after {max_retries} revision attempts. "
        f"Flagged as 'needs_review' to prevent automatic publishing."
    )

    return {
        "article_id": article.id,
        "status": article.status,
        "quality_score": final_evaluation.overall_score if final_evaluation else 0.0,
        "threshold_used": final_evaluation.threshold_used if final_evaluation else 8.0,
        "passes_threshold": False,
        "attempts_made": attempt,
        "dimension_scores": final_evaluation.dimension_scores if final_evaluation else {},
        "strengths": final_evaluation.strengths if final_evaluation else [],
        "deficiencies": final_evaluation.deficiencies if final_evaluation else [],
        "revision_recommendations": final_evaluation.revision_recommendations if final_evaluation else [],
    }
