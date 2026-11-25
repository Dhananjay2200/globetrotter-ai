"""
Standalone Database Diagnostic & Deduplication Verification Script.
Tests:
 1. Connection to PostgreSQL (or SQLite fallback)
 2. Table creation (Destinations, Topics, Articles, Sources, Images, PublishingJobs)
 3. Inserting a Destination and Topic
 4. Level 1 Canonical Deduplication enforcement

Usage:
    python test_db.py
"""

import sys
from app.database.session import check_db_connection, SessionLocal
from app.database.init_db import init_db
from app.database.models import Destination, Topic
from app.database.topic_store import save_topic_if_unique, generate_canonical_key


def run_db_diagnostic():
    print("=" * 65)
    print(" GlobeTrotter AI - Database & Deduplication Diagnostic")
    print("=" * 65)

    # 1. Connection Check
    print("[*] Checking Database Connectivity...")
    conn_info = check_db_connection()
    if conn_info.get("status") != "connected":
        print(f"[-] Database connection failed:")
        print(f"    Error: {conn_info.get('message')}")
        print("\nTroubleshooting tips:")
        print(" 1. Ensure PostgreSQL service is running on your machine.")
        print(" 2. Confirm your DATABASE_URL in .env (default: postgresql+psycopg2://postgres:postgres@localhost:5432/globetrotter_ai).")
        print(" 3. Create the database if it doesn't exist: CREATE DATABASE globetrotter_ai;")
        print(" 4. If using SQLite for immediate local testing, set DATABASE_URL=sqlite:///./globetrotter.db in .env")
        sys.exit(1)

    print(f"[+] Connected to: {conn_info.get('dialect')} ({conn_info.get('url')})")
    print("-" * 65)

    # 2. Schema / Tables Verification
    print("[*] Verifying Database Schema & Creating Tables...")
    if not init_db():
        print("[-] Schema initialization failed.")
        sys.exit(1)
    print("-" * 65)

    # 3. Test Destination & Topic Creation
    print("[*] Testing Data Insertion & Level-1 Exact Duplicate Detection...")
    db = SessionLocal()
    try:
        # Create Destination if not exists
        dest_name = "Kyoto Historical Temples"
        country_name = "Japan"
        dest = db.query(Destination).filter(
            Destination.name == dest_name,
            Destination.country == country_name
        ).first()

        if not dest:
            dest = Destination(
                name=dest_name,
                country=country_name,
                region="Kansai",
                destination_type="Historical & Cultural",
                description="Ancient imperial capital of Japan, famous for historic Buddhist temples and Shinto shrines."
            )
            db.add(dest)
            db.commit()
            db.refresh(dest)
            print(f"[+] Created Destination: {dest.name} (ID: {dest.id})")
        else:
            print(f"[+] Found existing Destination: {dest.name} (ID: {dest.id})")

        # Define Topic sample
        category = "Heritage"
        unique_angle = "Exploring Zen architecture and moss gardens of 1200-year-old temples"
        proposed_title = "The Ancient Soul of Kyoto: Walking Through Timeless Zen Temples"

        expected_key = generate_canonical_key(dest_name, category, unique_angle)
        print(f"[*] Generated Canonical Key: '{expected_key}'")

        # Insertion #1: Should succeed
        topic1, is_created1 = save_topic_if_unique(
            db=db,
            destination=dest_name,
            country=country_name,
            category=category,
            proposed_title=proposed_title,
            unique_angle=unique_angle,
            discovery_source="test_diagnostic",
            destination_id=dest.id
        )

        if is_created1:
            print(f"[+] First insertion successful! Topic ID: {topic1.id}")
        else:
            print(f"[i] Topic already existed from prior run: Topic ID {topic1.id}")

        # Insertion #2: Identical topic parameters -> Must be rejected as duplicate
        print("[*] Attempting duplicate insertion with identical canonical attributes...")
        topic2, is_created2 = save_topic_if_unique(
            db=db,
            destination=dest_name,
            country=country_name,
            category=category,
            proposed_title=proposed_title,
            unique_angle=unique_angle,
            discovery_source="test_diagnostic",
            destination_id=dest.id
        )

        if not is_created2:
            print(f"[+] Success: Duplicate topic was rejected by Level-1 Deduplication!")
            print(f"    Returned existing Topic ID: {topic2.id}")
        else:
            print(f"[-] ERROR: Duplicate topic was NOT rejected! Duplicate prevention failed.")
            sys.exit(1)

        print("-" * 65)
        print("[+] All Database & Level-1 Deduplication Tests Passed Successfully!")
        print("=" * 65)

    except Exception as exc:
        db.rollback()
        print(f"[-] Database test error: {exc}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    run_db_diagnostic()
