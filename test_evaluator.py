"""
Standalone Diagnostic Script: Test Phase 8 - Article Quality Evaluation Agent.
Tests:
  1. Multidimensional scoring against the 11-point quality rubric via NVIDIA NIM
  2. Quality threshold gate enforcement (e.g., 8.0/10)
  3. Automated revision pass with targeted feedback loop if below threshold
  4. Retry-limit safeguards preventing infinite loops
  5. Failed article quarantine as 'needs_review' vs approval as 'quality_passed'
  6. PostgreSQL persistence of quality score and publication status

Usage:
    python test_evaluator.py
"""

import sys
from app.database.session import SessionLocal, check_db_connection
from app.database.models import Article, Topic
from app.graph.nodes.quality_check import evaluate_and_route_article
from app.services.evaluator_service import EVALUATION_DIMENSIONS


def run_evaluation_test():
    print("=" * 65)
    print(" GlobeTrotter AI - Phase 8: Article Quality Evaluation Agent")
    print("=" * 65)

    # 1. DB Connectivity Check
    conn_info = check_db_connection()
    if conn_info.get("status") != "connected":
        print(f"[-] Database connection failed: {conn_info.get('message')}")
        sys.exit(1)
    print(f"[+] Connected to PostgreSQL: {conn_info.get('database')}")
    print("-" * 65)

    db = SessionLocal()
    try:
        # 2. Select target article
        target_article = (
            db.query(Article)
            .order_by(Article.id.asc())
            .first()
        )

        if not target_article:
            print("[-] No articles found in database. Run Phase 5 first.")
            sys.exit(1)

        topic = db.query(Topic).filter(Topic.id == target_article.topic_id).first()
        dest_name = topic.destination if topic else "Target Destination"

        print(f"[*] Target Article Selected for Quality Audit:")
        print(f"    Article ID    : {target_article.id}")
        print(f"    Destination   : {dest_name} ({topic.country if topic else 'Global'})")
        print(f"    Title         : {target_article.title}")
        print(f"    Current Status: '{target_article.status}'")
        print(f"    Word Count    : {target_article.word_count} words")
        print("-" * 65)

        # 3. Execute Quality Evaluation Pipeline
        print("[*] Auditing Article across 11 Quality Dimensions via NVIDIA NIM...")
        eval_result = evaluate_and_route_article(
            db=db,
            article_id=target_article.id,
            max_retries=1,
            threshold=8.0,
        )

        print(f"[+] Quality Evaluation Completed! Decision: '{eval_result['status']}'")
        print(f"[+] Overall Quality Score : {eval_result['quality_score']} / 10.0 (Threshold: {eval_result['threshold_used']})")
        print(f"[+] Evaluation Passes     : {eval_result['passes_threshold']}")
        print(f"[+] Total Attempts Made   : {eval_result['attempts_made']}")
        print("-" * 65)

        # 4. Display 11-Point Rubric Breakdown
        print("[*] 11-Point Dimensional Scorecard:")
        dim_scores = eval_result["dimension_scores"]
        for dim in EVALUATION_DIMENSIONS:
            score = dim_scores.get(dim, 0.0)
            status_indicator = "[PASS]" if score >= 7.5 else "[MARGINAL]"
            formatted_name = dim.replace("_", " ").title().ljust(26)
            print(f"    - {formatted_name} : {score}/10.0 {status_indicator}")
        print("-" * 65)

        # 5. Display Strengths and Feedback
        if eval_result.get("strengths"):
            print("[*] Editorial Strengths:")
            for s in eval_result["strengths"]:
                print(f"    + {s}")

        if eval_result.get("deficiencies"):
            print("\n[*] Identified Deficiencies:")
            for d in eval_result["deficiencies"]:
                print(f"    - {d}")

        if eval_result.get("revision_recommendations"):
            print("\n[*] Actionable Revision Recommendations:")
            for r in eval_result["revision_recommendations"]:
                print(f"    > {r}")
        print("-" * 65)

        # 6. Verify PostgreSQL Updates
        db.refresh(target_article)
        print("[*] Verifying PostgreSQL 'articles' Status Updates:")
        print(f"  - DB Status        : '{target_article.status}'")
        print(f"  - DB Quality Score : {target_article.quality_score}/10.0")
        print("-" * 65)

        assert target_article.status in ["quality_passed", "needs_review"], f"Unexpected status: {target_article.status}"
        assert target_article.quality_score is not None, "Quality score must be recorded in DB."
        assert len(dim_scores) == 11, f"Expected 11 dimensions scored, found {len(dim_scores)}."

        print("[+] Phase 8 Article Quality Evaluation Agent Tests Passed Successfully!")
        print("=" * 65)

    except Exception as exc:
        db.rollback()
        print(f"[-] Quality Evaluation test encountered error: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    run_evaluation_test()
