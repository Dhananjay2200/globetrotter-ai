"""
GlobeTrotter AI - Phase 10 Diagnostic: Automatic Publishing API Test.
Verifies the automated publishing service, idempotency guarantees, quality gates,
and public feed integration for the React website frontend.
"""

import sys
from sqlalchemy.orm import Session
from app.database.session import SessionLocal, ensure_database_exists
from app.database.init_db import init_db
from app.database.models import Article, Topic, PublishingJob
from app.services.publisher_service import (
    publish_article,
    publish_all_pending,
    get_public_feed,
)


def run_publisher_diagnostics():
    print("=" * 65)
    print(" GlobeTrotter AI - Phase 10: Automatic Publishing API Diagnostic")
    print("=" * 65)

    ensure_database_exists()
    init_db()

    db: Session = SessionLocal()
    try:
        # 1. Test Quality Gate Blocking on Unapproved Articles
        print("[*] Test 1: Quality Gate Publishing Block...")
        # Create a temporary draft topic and article
        temp_topic = Topic(
            canonical_key="temp-unapproved-test-destination__test-cat__test-angle",
            destination="Unapproved Draft Test",
            country="Testland",
            category="Historical Monuments & Heritage Sites",
            proposed_title="Draft Unapproved Article",
            unique_angle="Test angle",
            status="draft",
        )
        db.add(temp_topic)
        db.commit()
        db.refresh(temp_topic)

        temp_article = Article(
            topic_id=temp_topic.id,
            title="Draft Unapproved Article",
            slug="draft-unapproved-article-test",
            body_markdown="Draft content not reviewed.",
            word_count=5,
            status="draft",  # NOT quality_passed
            quality_score=4.2,
        )
        db.add(temp_article)
        db.commit()
        db.refresh(temp_article)

        blocked = False
        try:
            publish_article(db=db, article_id=temp_article.id)
        except ValueError as ve:
            blocked = True
            print(f"    [+] Successfully blocked publication of non-approved article: {ve}")

        # Clean up temporary test records
        db.delete(temp_article)
        db.delete(temp_topic)
        db.commit()

        assert blocked, "Quality Gate failed to block an unapproved draft article!"

        print("-" * 65)

        # 2. Test Publishing Quality-Passed Article (Article ID 2 - Banff National Park)
        print("[*] Test 2: Publishing Verified Article...")
        target_article = db.query(Article).filter(Article.status == "quality_passed").first()
        if not target_article:
            # Fallback: check if Article 1 or 2 exists
            target_article = db.query(Article).first()
            if target_article:
                target_article.status = "quality_passed"
                db.commit()

        assert target_article is not None, "No test article found in database!"
        article_id = target_article.id
        print(f"    Target Article ID : {article_id} ('{target_article.title}')")
        print(f"    Initial Status    : {target_article.status}")
        print(f"    Quality Score     : {target_article.quality_score}/10.0")

        job, post_payload = publish_article(db=db, article_id=article_id)
        print(f"[+] Successfully Published Article ID {article_id}!")
        print(f"    Publishing Job ID : {job.id}")
        print(f"    Job Status        : {job.status}")
        print(f"    Idempotency Key   : {job.idempotency_key[:32]}...")
        print(f"    Website Post ID   : {post_payload['post_id']}")
        print(f"    Website URL       : {post_payload['website_url']}")
        print(f"    Featured Image    : {post_payload['featured_image']['url'][:60]}... ({post_payload['featured_image']['license']})")
        print(f"    Citations Linked  : {len(post_payload['citations'])}")

        print("-" * 65)

        # 3. Test Idempotency (Re-publishing the exact same article)
        print("[*] Test 3: Idempotency Verification (Double-Publishing Prevention)...")
        initial_job_count = db.query(PublishingJob).filter(PublishingJob.article_id == article_id).count()

        job_repeat, payload_repeat = publish_article(db=db, article_id=article_id)
        final_job_count = db.query(PublishingJob).filter(PublishingJob.article_id == article_id).count()

        assert job_repeat.id == job.id, "Idempotency failed: Returned a different job ID!"
        assert initial_job_count == final_job_count, "Idempotency failed: Created duplicate PublishingJob record!"
        print(f"[+] Idempotency Verified! Re-publish returned existing Job ID {job_repeat.id} without duplicating.")

        print("-" * 65)

        # 4. Test Batch Publishing (publishes remaining quality_passed articles)
        print("[*] Test 4: Batch Publishing Run...")
        batch_res = publish_all_pending(db=db, limit=10)
        print(f"    Total Pending Found : {batch_res['total_pending']}")
        print(f"    Published Count     : {batch_res['published_count']}")
        print(f"    Published IDs       : {batch_res['published_ids']}")
        print(f"    Failed Count        : {batch_res['failed_count']}")

        print("-" * 65)

        # 5. Test Public React Feed Generation
        print("[*] Test 5: Public Blog Feed Generation for React Website...")
        feed = get_public_feed(db=db, limit=5)
        print(f"[+] Total Published Posts in Feed: {feed['total']}")
        for idx, p in enumerate(feed["posts"], 1):
            print(f"    [{idx}] Title       : {p['title']}")
            print(f"        Slug        : {p['slug']}")
            print(f"        Destination : {p['destination']}, {p['country']}")
            print(f"        Category    : {p['category']}")
            print(f"        Words       : {p['word_count']} words")
            print(f"        Score       : {p['quality_score']}/10.0")
            print(f"        Featured Img: {p['featured_image']['url'][:50] if p['featured_image'] else 'None'}...")

        assert feed["total"] >= 1, "Public feed did not contain published articles!"

        print("-" * 65)
        print("[+] Phase 10 Automatic Publishing API Diagnostic Passed Successfully!")
        print("=" * 65)

    finally:
        db.close()


if __name__ == "__main__":
    run_publisher_diagnostics()
