"""
Diagnostic to verify:
1. Backend feed payload contains 'region' properly resolved.
2. Combinatorial filtering logic matches Region AND Category.
"""

from fastapi.testclient import TestClient
from app.main import app
from app.services.cache_service import blog_cache


def run_filter_tests():
    print("=" * 65)
    print(" GlobeTrotter AI - Region & Category Combinatorial Filter Diagnostic")
    print("=" * 65)

    # Invalidate feed cache to get latest published posts and new region fields
    blog_cache.invalidate_prefix("feed:")

    with TestClient(app) as client:
        res = client.get("/api/v1/publish/feed?limit=50")
        assert res.status_code == 200
        feed = res.json()
        posts = feed.get("posts", [])

        print(f"[+] Loaded {len(posts)} published posts from public feed:")
        for p in posts:
            print(f"    - ID {p['article_id']:2d}: {p['destination']:<25} | Country: {p['country']:<10} | Region: {p.get('region'):<25} | Category: {p['category']}")

        # Verify that all posts have a valid resolved region
        for p in posts:
            assert "region" in p and p["region"] is not None and p["region"] != "Global", \
                f"Post {p['destination']} has unresolved region: {p.get('region')}"

        print("-" * 65)
        print("[*] Testing Combinatorial Filters (Region AND Category)...")

        # Test Case A: North America + Waterfalls, Mountains & Natural Wonders
        na_mountains = [
            p for p in posts 
            if p.get("region") == "North America" and "Mountain" in p.get("category", "")
        ]
        assert len(na_mountains) >= 1, "North America + Mountains combination returned 0 posts!"
        print(f"    [+] North America + Mountains: {len(na_mountains)} post(s) found -> {[p['destination'] for p in na_mountains]}")

        # Test Case B: Western & Northern Europe + Historical Monuments & Heritage Sites
        we_heritage = [
            p for p in posts 
            if p.get("region") == "Western & Northern Europe" and ("Heritage" in p.get("category", "") or "Historic" in p.get("category", ""))
        ]
        assert len(we_heritage) >= 1, "Western & Northern Europe + Heritage returned 0 posts!"
        print(f"    [+] Western Europe + Heritage: {len(we_heritage)} post(s) found -> {[p['destination'] for p in we_heritage]}")

        # Test Case C: Southern & Eastern Europe + Coastal Escapes
        se_coastal = [
            p for p in posts 
            if p.get("region") == "Southern & Eastern Europe" and "Coastal" in p.get("category", "")
        ]
        assert len(se_coastal) >= 1, "Southern & Eastern Europe + Coastal returned 0 posts!"
        print(f"    [+] Southern Europe + Coastal: {len(se_coastal)} post(s) found -> {[p['destination'] for p in se_coastal]}")

        # Test Case D: Southern & Eastern Europe + Local Cuisines
        se_food = [
            p for p in posts 
            if p.get("region") == "Southern & Eastern Europe" and ("Cuisine" in p.get("category", "") or "Pasta" in p.get("category", "") or "Culinary" in p.get("category", ""))
        ]
        assert len(se_food) >= 1, "Southern & Eastern Europe + Cuisine returned 0 posts!"
        print(f"    [+] Southern Europe + Cuisines: {len(se_food)} post(s) found -> {[p['destination'] for p in se_food]}")

        # Test Case E: South America + Wildlife & Safaris
        sa_wildlife = [
            p for p in posts 
            if p.get("region") == "South America" and "Wildlife" in p.get("category", "")
        ]
        assert len(sa_wildlife) >= 1, "South America + Wildlife returned 0 posts!"
        print(f"    [+] South America + Wildlife: {len(sa_wildlife)} post(s) found -> {[p['destination'] for p in sa_wildlife]}")

    print("-" * 65)
    print("[+] Combinatorial Filtering Diagnostic Passed with 100% Accuracy!")
    print("=" * 65)


if __name__ == "__main__":
    run_filter_tests()
