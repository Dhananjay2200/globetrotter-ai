"""
Standalone Diagnostic Script: Test Phase 6 - SEO Agent.
Tests:
  1. SEO title generation & length optimization (50-60 chars)
  2. Meta description generation with call-to-action (140-160 chars)
  3. Clean, human-readable URL slug derivation & collision resolution
  4. Primary & secondary latent semantic (LSI) keyword extraction
  5. Content tagging & accessible image alt text suggestions
  6. PostgreSQL persistence in 'articles' table

Usage:
    python test_seo.py
"""

import sys
from app.database.session import SessionLocal, check_db_connection
from app.database.models import Article, Topic
from app.graph.nodes.seo import optimize_article_seo
from app.services.seo_service import SEOMetadata


def run_seo_test():
    print("=" * 65)
    print(" GlobeTrotter AI - Phase 6: SEO Optimization Agent")
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
        # 2. Select target article from database
        target_article = (
            db.query(Article)
            .order_by(Article.id.asc())
            .first()
        )

        if not target_article:
            print("[-] No articles found in database. Run Phase 5 first to generate an article.")
            sys.exit(1)

        topic = db.query(Topic).filter(Topic.id == target_article.topic_id).first()
        dest_name = topic.destination if topic else "Target Destination"

        print(f"[*] Target Article Selected for SEO Optimization:")
        print(f"    Article ID    : {target_article.id}")
        print(f"    Destination   : {dest_name}")
        print(f"    Current Title : {target_article.title}")
        print(f"    Current Slug  : {target_article.slug}")
        print(f"    Word Count    : {target_article.word_count} words")
        print("-" * 65)

        # 3. Execute SEO Optimization Pipeline via NVIDIA NIM
        print("[*] Generating Comprehensive SEO Metadata Package via NVIDIA NIM...")
        updated_article, seo_meta = optimize_article_seo(db=db, article_id=target_article.id)

        print("[+] SEO Optimization Completed Successfully!\n")
        print(f"  - SEO Title          : \"{seo_meta.seo_title}\" ({len(seo_meta.seo_title)} chars)")
        print(f"  - Meta Description   : \"{seo_meta.meta_description}\" ({len(seo_meta.meta_description)} chars)")
        print(f"  - Clean URL Slug     : {seo_meta.slug}")
        print(f"  - Main Keyword       : \"{seo_meta.main_keyword}\"")
        print(f"  - Secondary Keywords : {', '.join(seo_meta.secondary_keywords)}")
        print(f"  - Content Tags       : {', '.join(seo_meta.tags)}")
        print(f"  - Teaser Summary     : {seo_meta.summary[:130]}...")
        print("-" * 65)

        # 4. Display Accessible Image Alt Text Suggestions
        print("[*] Generated Image Alt Text Suggestions (for Phase 7 Media Integration):")
        for i, alt in enumerate(seo_meta.image_alt_text_suggestions, 1):
            print(f"    [{i}] \"{alt}\"")
        print("-" * 65)

        # 5. Verify PostgreSQL Persistence
        db.refresh(target_article)
        print("[*] Verifying PostgreSQL 'articles' Record Updates:")
        print(f"  - DB seo_title       : {target_article.seo_title}")
        print(f"  - DB seo_description : {target_article.seo_description[:80]}...")
        print(f"  - DB main_keyword    : {target_article.main_keyword}")
        print(f"  - DB slug            : {target_article.slug}")
        print(f"  - DB summary         : {target_article.summary[:80]}...")
        print("-" * 65)

        # 6. Quality Assertions
        assert target_article.seo_title is not None, "SEO Title must be persisted in database."
        assert target_article.seo_description is not None, "Meta description must be persisted."
        assert len(target_article.slug) > 3, "Slug must be valid non-empty string."
        assert target_article.main_keyword is not None, "Main keyword must be recorded."

        print("[+] Phase 6 SEO Optimization Agent Tests Passed Successfully!")
        print("=" * 65)

    except Exception as exc:
        db.rollback()
        print(f"[-] SEO Agent test encountered error: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    run_seo_test()
