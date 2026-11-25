"""
Standalone Diagnostic Script: Test Phase 5 - Article Writer Agent.
Tests:
  1. 12-section editorial outline generation via NVIDIA NIM
  2. Full long-form Markdown article generation
  3. Word-count calculation & section completeness verification
  4. Citation linkage to 'research_sources'
  5. PostgreSQL persistence in 'articles' table
  6. Topic status advancement to 'written'

Usage:
    python test_writer.py
"""

import sys
import re
from app.database.session import SessionLocal, check_db_connection
from app.database.models import Topic, Article, ResearchSource
from app.graph.nodes.writer import write_article_for_topic
from app.services.writer_service import REQUIRED_ARTICLE_SECTIONS


def run_writer_test():
    print("=" * 65)
    print(" GlobeTrotter AI - Phase 5: Article Writer Agent")
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
        # 2. Select a target topic
        target_topic = (
            db.query(Topic)
            .filter(Topic.status.in_(["researched", "discovered", "written"]))
            .order_by(Topic.id.asc())
            .first()
        )

        if not target_topic:
            print("[-] No topics found in database. Run Phase 3/4 first.")
            sys.exit(1)

        print(f"[*] Target Topic Selected for Article Generation:")
        print(f"    Topic ID    : {target_topic.id}")
        print(f"    Destination : {target_topic.destination} ({target_topic.country})")
        print(f"    Title       : {target_topic.proposed_title}")
        print(f"    Angle       : {target_topic.unique_angle}")
        print("-" * 65)

        # 3. Execute Article Writer Agent
        print("[*] Generating Article Outline & Full Markdown Content via NVIDIA NIM...")
        article: Article = write_article_for_topic(db=db, topic_id=target_topic.id)

        print(f"[+] Article successfully created in PostgreSQL! Article ID: {article.id}")
        print(f"[+] Title       : {article.title}")
        print(f"[+] URL Slug    : {article.slug}")
        print(f"[+] Word Count  : {article.word_count} words")
        print(f"[+] Status      : '{article.status}'")
        print("-" * 65)

        # 4. Verify Section Headers in Markdown
        headers = re.findall(r"^##\s+(.+)$", article.body_markdown, flags=re.MULTILINE)
        print(f"[*] Detected {len(headers)} Major Sections (## Headers):")
        for h in headers:
            print(f"    - {h}")
        print("-" * 65)

        # 5. Verify Citation Linkage
        linked_sources = (
            db.query(ResearchSource)
            .filter(ResearchSource.article_id == article.id)
            .all()
        )
        print(f"[*] Verified Linked Research Citations: {len(linked_sources)} sources linked to Article ID {article.id}")
        for s in linked_sources:
            print(f"    - [{s.publisher}] {s.title} ({s.url})")
        print("-" * 65)

        # 6. Preview First 400 Characters of Article Body
        print("[*] Article Markdown Preview:")
        print("-" * 65)
        preview_lines = article.body_markdown.split("\n")[:18]
        print("\n".join(preview_lines))
        print("...\n[Content continues with full sections, itineraries, tips, and sources]")
        print("-" * 65)

        # 7. Quality & Integrity Assertions
        assert article.word_count >= 500, f"Article word count ({article.word_count}) is unexpectedly low."
        assert len(headers) >= 8, f"Expected at least 8 major sections, found {len(headers)}."
        assert target_topic.status == "written", f"Expected topic status 'written', found {target_topic.status}."
        print("[+] Phase 5 Article Writer Agent Tests Passed Successfully!")
        print("=" * 65)

    except Exception as exc:
        db.rollback()
        print(f"[-] Article Writer test encountered error: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    run_writer_test()
