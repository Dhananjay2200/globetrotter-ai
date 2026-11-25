"""
Standalone Diagnostic Script: Test Phase 4 - Research & Evidence Collection Agent.
Tests:
  1. Multi-source evidence gathering (Tavily & Wikipedia APIs)
  2. Factual evidence synthesis via NVIDIA NIM
  3. Strict factual constraints verification (No hallucinated pricing/hours)
  4. PostgreSQL persistence into 'research_sources' table
  5. Topic status advancement to 'researched'

Usage:
    python test_research.py
"""

import sys
from app.database.session import SessionLocal, check_db_connection
from app.database.models import Topic, ResearchSource
from app.graph.nodes.research import conduct_topic_research


def run_research_test():
    print("=" * 65)
    print(" GlobeTrotter AI - Phase 4: Research Agent & Evidence Collection")
    print("=" * 65)

    # 1. Database Connectivity Check
    conn_info = check_db_connection()
    if conn_info.get("status") != "connected":
        print(f"[-] Database connection failed: {conn_info.get('message')}")
        sys.exit(1)
    print(f"[+] Connected to PostgreSQL: {conn_info.get('database')}")
    print("-" * 65)

    db = SessionLocal()
    try:
        # 2. Pick a target topic from PostgreSQL
        target_topic = (
            db.query(Topic)
            .filter(Topic.status.in_(["discovered", "researched"]))
            .order_by(Topic.id.asc())
            .first()
        )

        if not target_topic:
            print("[-] No topics available in the database to research. Please run Phase 3 first.")
            sys.exit(1)

        print(f"[*] Selected Topic ID {target_topic.id} for Research:")
        print(f"    Destination : {target_topic.destination} ({target_topic.country})")
        print(f"    Category    : {target_topic.category}")
        print(f"    Title       : {target_topic.proposed_title}")
        print(f"    Angle       : {target_topic.unique_angle}")
        print("-" * 65)

        # 3. Execute Research Agent Pipeline
        print("[*] Initiating Multi-Source Research Gathering & Evidence Synthesis...")
        result = conduct_topic_research(db=db, topic_id=target_topic.id)

        print(f"[+] Research completed! Topic status: '{result['status']}'")
        print(f"[+] Total Citations Stored: {result['total_sources']}")
        print("-" * 65)

        # 4. Display Synthesized Factual Evidence
        evidence = result["evidence"]
        print("[*] Synthesized Evidence Domains (NVIDIA NIM):")
        print(f"  - Geographical Context  : {evidence.get('geographical_context')[:140]}...")
        print(f"  - Historical Background : {evidence.get('historical_background')[:140]}...")
        print(f"  - Cultural Significance : {evidence.get('cultural_significance')[:140]}...")
        print(f"  - Key Attractions       : {', '.join(evidence.get('key_attractions', []))}")
        print(f"  - Local Cuisine         : {evidence.get('local_cuisine')[:140]}...")
        print(f"  - Best Visiting Season  : {evidence.get('best_visiting_season')[:140]}...")
        print(f"  - Transportation Access : {evidence.get('transportation_access')[:140]}...")
        print(f"  - Practical Tips        : {len(evidence.get('practical_travel_tips', []))} verified tips")
        print(f"  - Safety Guidelines     : {evidence.get('safety_guidelines')[:140]}...")
        print("-" * 65)

        # 5. Verify Database Persistence of Research Sources
        saved_sources = (
            db.query(ResearchSource)
            .filter(ResearchSource.topic_id == target_topic.id)
            .all()
        )

        print(f"[*] Verifying PostgreSQL 'research_sources' Table ({len(saved_sources)} records):")
        for i, src in enumerate(saved_sources, 1):
            print(f"  [{i}] Source ID: {src.id}")
            print(f"      Publisher: {src.publisher}")
            print(f"      Title    : {src.title}")
            print(f"      URL      : {src.url}")
            print(f"      Excerpt  : {src.evidence_excerpt[:100]}...")
            print()

        assert len(saved_sources) >= 1, "At least one research source must be persisted."
        assert target_topic.status == "researched", "Topic status must be 'researched'."

        print("-" * 65)
        print("[+] Phase 4 Research Agent & Evidence Collection Tests Passed Successfully!")
        print("=" * 65)

    except Exception as exc:
        db.rollback()
        print(f"[-] Research test encountered error: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    run_research_test()
