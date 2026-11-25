"""
GlobeTrotter AI - Phase 9 Diagnostic: Full LangGraph Integration Test.
Verifies the end-to-end multi-agent pipeline orchestrated by LangGraph:
  1. Discovery Node
  2. Deduplication Gate (Level 1 & Level 2 conditional edge)
  3. Research Node (Evidence collection & citations)
  4. Article Writer Node (12-section long-form markdown)
  5. SEO Optimization Node (Metadata, keywords, slug)
  6. Image Discovery Node (Wikimedia Commons & CC licensing)
  7. Quality Gate Node (11-dimension scoring & revision loop)
"""

import sys
import time
from sqlalchemy.orm import Session
from app.database.session import SessionLocal, ensure_database_exists
from app.database.init_db import init_db
from app.database.models import Topic, Article, ResearchSource, ImageAsset
from app.database.topic_store import generate_canonical_key
from app.graph.workflow import (
    globetrotter_graph,
    run_globetrotter_pipeline,
    route_after_deduplication,
    route_after_quality_check,
)
from app.utils.logging import logger


def run_langgraph_diagnostics():
    print("=" * 65)
    print(" GlobeTrotter AI - Phase 9: LangGraph Pipeline Diagnostic")
    print("=" * 65)

    # 1. Ensure DB readiness
    ensure_database_exists()
    init_db()

    # 2. Test Graph Compilation & Node Registration
    print("[*] Verifying LangGraph Structure & Node Registration...")
    try:
        nodes = list(globetrotter_graph.get_graph().nodes.keys())
        expected_nodes = [
            "discover_node",
            "deduplicate_node",
            "research_node",
            "writer_node",
            "seo_node",
            "image_node",
            "quality_node",
            "revision_node",
        ]
        for node in expected_nodes:
            assert node in nodes, f"Expected node '{node}' missing from compiled graph!"
        print(f"[+] Successfully verified compiled LangGraph with {len(nodes)} registered nodes:")
        for n in expected_nodes:
            print(f"    - {n}")
    except Exception as exc:
        print(f"[-] Graph structure check failed: {exc}")
        sys.exit(1)

    print("-" * 65)

    # 3. Test Conditional Edge Routing Functions
    print("[*] Testing Conditional Edge Routing Functions...")
    route_dup = route_after_deduplication({"is_duplicate": True})
    route_pass = route_after_deduplication({"is_duplicate": False})
    assert route_dup == "duplicate", f"Expected 'duplicate', got '{route_dup}'"
    assert route_pass == "proceed", f"Expected 'proceed', got '{route_pass}'"
    print("    [+] Deduplication router: Verified (duplicate -> END, proceed -> research_node)")

    route_q_pass = route_after_quality_check({"passes_quality": True})
    route_q_rev = route_after_quality_check({"passes_quality": False, "revision_attempts": 0, "max_revisions": 1})
    route_q_exh = route_after_quality_check({"passes_quality": False, "revision_attempts": 1, "max_revisions": 1})
    assert route_q_pass == "passed", f"Expected 'passed', got '{route_q_pass}'"
    assert route_q_rev == "revise", f"Expected 'revise', got '{route_q_rev}'"
    assert route_q_exh == "exhausted", f"Expected 'exhausted', got '{route_q_exh}'"
    print("    [+] Quality Gate router: Verified (passed -> END, revise -> revision_node, exhausted -> END)")

    print("-" * 65)

    # 4A. Live Graph Deduplication Short-Circuit Test
    print("[*] Test 4A: Live Graph Deduplication Gate Test (Duplicate Rejection)...")
    duplicate_candidate = {
        "destination": "Banff National Park",
        "country": "Canada",
        "region": "North America",
        "category": "Waterfalls, Mountains & Natural Wonders",
        "proposed_title": "Banff National Park: Turquoise Glacial Lakes and Rocky Mountain Peaks",
        "unique_angle": "Exploring pristine alpine waters of Lake Louise and Moraine Lake amidst the Canadian Rockies",
    }
    dup_state = run_globetrotter_pipeline(initial_state=duplicate_candidate)
    assert dup_state.get("is_duplicate") is True, "Deduplication gate failed to flag existing topic as duplicate!"
    assert dup_state.get("status") == "duplicate_rejected", f"Expected 'duplicate_rejected', got {dup_state.get('status')}"
    print(f"    [+] Success! LangGraph short-circuited duplicate topic cleanly in {dup_state.get('current_node')}.")
    print(f"        Reason: {dup_state.get('deduplication_reason')}")

    print("-" * 65)

    # 4B. Live Graph End-to-End Execution with Novel Candidate
    print("[*] Test 4B: Live Graph End-to-End Pipeline Execution (Novel Destination)...")
    
    # Candidate pool to ensure repeatability across runs
    candidates_pool = [
        {
            "destination": "Salzburg Historic Altstadt",
            "country": "Austria",
            "region": "Western & Northern Europe",
            "category": "Historical Monuments & Heritage Sites",
            "proposed_title": "Salzburg Historic Altstadt: Baroque Splendor and Mozart's Musical Legacy",
            "unique_angle": "Exploring baroque cathedral architecture, Hohensalzburg fortress, and Mirabell gardens in Mozart's birthplace",
        },
        {
            "destination": "Santorini Caldera",
            "country": "Greece",
            "region": "Southern & Eastern Europe",
            "category": "Coastal Escapes & Island Wonders",
            "proposed_title": "Santorini Caldera: Whitewashed Clifftop Villages and Volcanic Sunsets",
            "unique_angle": "Discovering cliffside Cycladic architecture, volcanic rim hiking trails, and ancient Thera heritage",
        },
        {
            "destination": "Jiuzhaigou Valley",
            "country": "China",
            "region": "East & Southeast Asia",
            "category": "Waterfalls, Mountains & Natural Wonders",
            "proposed_title": "Jiuzhaigou Valley: Multi-Tiered Waterfalls and Colorful Alpine Lakes",
            "unique_angle": "Traversing UNESCO-protected Tibetan plateau valleys featuring crystal-clear turquoise lakes and cascading karst falls",
        },
    ]

    db: Session = SessionLocal()
    chosen_candidate = None
    try:
        # Find the first candidate that hasn't been added to PostgreSQL yet
        for cand in candidates_pool:
            key = generate_canonical_key(cand["destination"], cand["category"], cand["unique_angle"])
            existing = db.query(Topic).filter(Topic.canonical_key == key).first()
            if not existing:
                chosen_candidate = cand
                break

        # If all candidates in pool were used, append a timestamped angle to guarantee uniqueness
        if not chosen_candidate:
            epoch = int(time.time())
            chosen_candidate = {
                "destination": "Salzburg Historic Altstadt",
                "country": "Austria",
                "region": "Western & Northern Europe",
                "category": "Historical Monuments & Heritage Sites",
                "proposed_title": f"Salzburg Historic Altstadt: Baroque Splendor #{epoch}",
                "unique_angle": f"Exploring baroque architecture and classical music legacy in Salzburg volume {epoch}",
            }
    finally:
        db.close()

    print(f"    Target Destination : {chosen_candidate['destination']} ({chosen_candidate['country']})")
    print(f"    Category           : {chosen_candidate['category']}")
    print(f"    Proposed Title     : {chosen_candidate['proposed_title']}")
    print("-" * 65)

    start_time = time.time()
    final_state = run_globetrotter_pipeline(initial_state=chosen_candidate)
    elapsed = time.time() - start_time

    print(f"[+] Pipeline Run Finished in {elapsed:.1f} seconds!")
    print(f"    Final Status      : {final_state.get('status')}")
    print(f"    Topic ID          : {final_state.get('topic_id')}")
    print(f"    Article ID        : {final_state.get('article_id')}")
    print(f"    Article Title     : {final_state.get('article_title')}")
    print(f"    Slug              : {final_state.get('slug')}")
    print(f"    Word Count        : {final_state.get('word_count')} words")
    print(f"    Sections Detected : {len(final_state.get('sections_detected', []))}")
    print(f"    SEO Title         : {final_state.get('seo_title')}")
    print(f"    Meta Description  : {final_state.get('meta_description')}")
    print(f"    Main Keyword      : {final_state.get('main_keyword')}")
    print(f"    Images Attached   : {final_state.get('images_count')} verified assets")
    print(f"    Featured Image    : {final_state.get('featured_image_url')}")
    print(f"    Quality Score     : {final_state.get('quality_score')}/10.0")
    print(f"    Passes Threshold  : {final_state.get('passes_quality')}")
    print(f"    Revision Attempts : {final_state.get('revision_attempts', 0)}")

    print("-" * 65)
    print("[*] Pipeline Execution Logs:")
    for log_entry in final_state.get("logs", []):
        print(f"    {log_entry}")

    print("-" * 65)

    # 5. Database Cross-Verification
    db = SessionLocal()
    try:
        article_id = final_state.get("article_id")
        assert article_id is not None, "Article ID was not created in final state!"

        article = db.query(Article).filter(Article.id == article_id).first()
        assert article is not None, f"Article ID {article_id} not found in PostgreSQL!"

        sources = db.query(ResearchSource).filter(ResearchSource.article_id == article.id).all()
        images = db.query(ImageAsset).filter(ImageAsset.article_id == article.id).all()

        print(f"[*] PostgreSQL Verification for Article ID {article.id}:")
        print(f"    - Status in DB    : {article.status}")
        print(f"    - Quality Score   : {article.quality_score}")
        print(f"    - Linked Sources  : {len(sources)} citations")
        print(f"    - Linked Images   : {len(images)} media assets")

        assert len(sources) > 0, "No research sources linked to article!"
        assert len(images) > 0, "No images linked to article!"
        assert article.status in ["quality_passed", "needs_review"], f"Unexpected article status: {article.status}"

        print("-" * 65)
        print("[+] Phase 9 LangGraph Integration Diagnostic Passed Successfully!")
        print("=" * 65)
    finally:
        db.close()


if __name__ == "__main__":
    run_langgraph_diagnostics()
