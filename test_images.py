"""
Standalone Diagnostic Script: Test Phase 7 - Image Discovery & License Agent.
Tests:
  1. Image discovery from permitted repositories (Wikimedia Commons, Unsplash, Pexels)
  2. Strict usage license compliance (CC BY-SA, CC BY, Public Domain, Unsplash)
  3. Creator attribution statement generation
  4. Featured image designation (1 featured image per article)
  5. Descriptive alt text assignment
  6. PostgreSQL persistence in 'image_assets' table

Usage:
    python test_images.py
"""

import sys
from app.database.session import SessionLocal, check_db_connection
from app.database.models import Article, Topic, ImageAsset
from app.graph.nodes.image_search import discover_and_attach_images
from app.services.image_service import is_license_permitted


def run_image_test():
    print("=" * 65)
    print(" GlobeTrotter AI - Phase 7: Image Discovery & Licensing Agent")
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

        print(f"[*] Target Article Selected for Media Attachment:")
        print(f"    Article ID    : {target_article.id}")
        print(f"    Destination   : {dest_name} ({topic.country if topic else 'Global'})")
        print(f"    Title         : {target_article.title}")
        print(f"    Target Images : 3 verified media assets")
        print("-" * 65)

        # 3. Execute Image Discovery & Licensing Pipeline
        print("[*] Searching Permitted Repositories & Validating Licenses...")
        assets = discover_and_attach_images(db=db, article_id=target_article.id, target_count=3)

        print(f"[+] Successfully retrieved and verified {len(assets)} media assets!\n")

        featured_count = 0
        for i, a in enumerate(assets, 1):
            if a.is_featured:
                featured_count += 1
            status_tag = "[FEATURED IMAGE]" if a.is_featured else "[GALLERY IMAGE]"
            print(f"  [{i}] {status_tag} (ID: {a.id})")
            print(f"      Provider    : {a.provider.upper()}")
            print(f"      License     : {a.license_name}")
            print(f"      Creator     : {a.creator}")
            print(f"      Attribution : \"{a.attribution}\"")
            print(f"      Alt Text    : \"{a.alt_text}\"")
            print(f"      Image URL   : {a.image_url[:80]}...")
            print()

        print("-" * 65)

        # 4. Strict License Compliance & Integrity Assertions
        assert len(assets) >= 1, "At least one legally usable image must be retrieved."
        assert featured_count == 1, f"Exactly 1 featured image expected, found {featured_count}."

        for a in assets:
            assert is_license_permitted(a.license_name), f"License '{a.license_name}' is not permitted!"
            assert len(a.attribution) > 5, "Attribution statement must be populated."
            assert len(a.alt_text) > 5, "Descriptive alt text must be populated."

        # 5. Verify PostgreSQL Persistence
        db_assets = db.query(ImageAsset).filter(ImageAsset.article_id == target_article.id).all()
        print(f"[*] Verified PostgreSQL 'image_assets' Table ({len(db_assets)} records for Article ID {target_article.id}):")
        for da in db_assets:
            print(f"    - Asset #{da.id} | Featured: {da.is_featured} | {da.provider} | {da.license_name}")

        print("-" * 65)
        print("[+] Phase 7 Image Discovery & Licensing Agent Tests Passed Successfully!")
        print("=" * 65)

    except Exception as exc:
        db.rollback()
        print(f"[-] Image Agent test encountered error: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    run_image_test()
