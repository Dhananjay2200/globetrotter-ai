"""
Standalone Diagnostic Script: Test Phase 3 - Topic Discovery & Deduplication.
Tests:
  1. AI-driven Global Topic Discovery via NVIDIA NIM
  2. Pydantic Schema Validation & Diversity Checks
  3. Level 1 Exact Canonical Deduplication
  4. Level 2 Semantic Similarity Duplicate Detection
  5. PostgreSQL Persistence

Usage:
    python test_discovery.py
"""

import sys
from app.database.session import SessionLocal, check_db_connection
from app.services.discovery_service import (
    discover_topics,
    TopicProposal,
    TOURISM_CATEGORIES,
)
from app.graph.nodes.duplicate_check import (
    evaluate_and_persist_topic,
    check_level1_canonical_duplicate,
    check_level2_semantic_duplicate,
)
from app.database.models import Topic, Destination


def run_discovery_test():
    print("=" * 65)
    print(" GlobeTrotter AI - Phase 3: Topic Discovery & Deduplication")
    print("=" * 65)

    # 1. DB Connectivity Check
    conn_info = check_db_connection()
    if conn_info.get("status") != "connected":
        print(f"[-] Database is not accessible: {conn_info.get('message')}")
        sys.exit(1)
    print(f"[+] Connected to PostgreSQL: {conn_info.get('database')}")
    print("-" * 65)

    db = SessionLocal()
    try:
        # 2. AI Global Topic Discovery via NVIDIA NIM
        print("[*] Initiating AI Topic Discovery via NVIDIA NIM (Target: 3 global topics)...")
        candidates = discover_topics(db=db, count=3)
        print(f"[+] Received {len(candidates)} candidate topics from AI Editor:\n")

        for idx, t in enumerate(candidates, 1):
            print(f"  [{idx}] Destination: {t.destination} ({t.country}) - Region: {t.region}")
            print(f"      Category   : {t.category}")
            print(f"      Title      : {t.proposed_title}")
            print(f"      Angle      : {t.unique_angle}")
            print()

        print("-" * 65)

        # 3. Persistence & Deduplication Verification
        print("[*] Evaluating & Persisting Discovered Topics...")
        saved_records = []
        for candidate in candidates:
            # Ensure destination record
            dest = db.query(Destination).filter(
                Destination.name == candidate.destination,
                Destination.country == candidate.country,
            ).first()
            if not dest:
                dest = Destination(
                    name=candidate.destination,
                    country=candidate.country,
                    region=candidate.region,
                    destination_type=candidate.category,
                    description=candidate.unique_angle,
                )
                db.add(dest)
                db.commit()
                db.refresh(dest)

            topic_rec, is_saved, reason = evaluate_and_persist_topic(db, candidate, destination_id=dest.id)
            if is_saved:
                print(f"[+] Saved: '{candidate.proposed_title}' (ID: {topic_rec.id})")
                saved_records.append(topic_rec)
            else:
                print(f"[i] Skipped: '{candidate.proposed_title}' -> {reason}")

        db.commit()
        print("-" * 65)

        # 4. Explicit Level-1 Canonical Deduplication Test
        existing_any = db.query(Topic).first()
        if existing_any:
            print(f"[*] Testing Level-1 Canonical Duplicate with Topic ID {existing_any.id}...")
            duplicate_candidate = TopicProposal(
                destination=existing_any.destination,
                country=existing_any.country,
                region="Test Region",
                category=existing_any.category,
                proposed_title=existing_any.proposed_title,
                unique_angle=existing_any.unique_angle,
            )
            is_l1_dup, l1_key = check_level1_canonical_duplicate(
                db=db,
                destination=duplicate_candidate.destination,
                category=duplicate_candidate.category,
                unique_angle=duplicate_candidate.unique_angle,
            )
            if is_l1_dup:
                print(f"[+] Level-1 Test PASSED: Exact duplicate correctly blocked! (Key: {l1_key})")
            else:
                print(f"[-] Level-1 Test FAILED: Exact duplicate was not recognized.")
                sys.exit(1)

        print("-" * 65)

        # 5. Explicit Level-2 Semantic Deduplication Test
        print("[*] Testing Level-2 Semantic Overlap Detection...")
        # Create an anchor topic: Iceland Waterfalls
        anchor_candidate = TopicProposal(
            destination="Seljalandsfoss Waterfalls",
            country="Iceland",
            region="Western & Northern Europe",
            category="Waterfalls, Mountains & Natural Wonders",
            proposed_title="Southern Iceland Waterfalls: Walking Behind Glacial Cascades",
            unique_angle="Exploring legendary southern Iceland waterfalls, glacial mist walks, and hidden cave viewpoints.",
        )
        rec_anchor, _, _ = evaluate_and_persist_topic(db, anchor_candidate)
        db.commit()

        # Create a semantic duplicate (different wording, same core destination, subject, and features)
        semantic_dup_candidate = TopicProposal(
            destination="Seljalandsfoss Waterfalls",
            country="Iceland",
            region="Western & Northern Europe",
            category="Waterfalls, Mountains & Natural Wonders",
            proposed_title="Top Iceland Waterfalls to Visit: Glacial Cascades and Southern Wonders",
            unique_angle="Walking through southern Iceland waterfalls, glacial cascades, and scenic viewpoints.",
        )

        is_sem_dup, match_title, sim_score = check_level2_semantic_duplicate(
            db=db,
            candidate=semantic_dup_candidate,
            threshold=0.35,
        )

        if is_sem_dup:
            print(f"[+] Level-2 Test PASSED: Semantic duplicate successfully detected!")
            print(f"    Overlaps with: '{match_title}' (Similarity score: {sim_score})")
        else:
            print(f"[-] Level-2 Test FAILED: Semantic duplicate was not detected (score: {sim_score}).")
            sys.exit(1)

        print("-" * 65)
        print("[+] Phase 3 Topic Discovery & Deduplication Tests Completed Successfully!")
        print("=" * 65)

    except Exception as exc:
        db.rollback()
        print(f"[-] Diagnostic failed with exception: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    run_discovery_test()
