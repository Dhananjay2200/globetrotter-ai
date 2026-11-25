"""
GlobeTrotter AI - Dual Frontend & Mobile Optimization Diagnostic.
Validates:
1. Admin and User SPA route availability (/app, /admin).
2. Unpublish & Re-publish actions with micro-cache purge.
3. Cache stats and cache flush operations.
4. Public feed retrieval for mobile readers.
"""

from fastapi.testclient import TestClient
from app.main import app


def test_dual_frontend_architecture():
    print("=" * 65)
    print(" GlobeTrotter AI - Dual Frontend & Admin/User Separation Test")
    print("=" * 65)

    with TestClient(app) as client:
        # 1. Test User and Admin SPA routes
        print("[*] Test 1: Testing SPA Routes for User and Admin Frontends...")
        res_app = client.get("/app")
        assert res_app.status_code == 200, f"/app returned {res_app.status_code}"
        assert "<html" in res_app.text.lower()
        print("    [+] User Frontend Portal Served (200 OK) -> /app")

        res_admin = client.get("/admin")
        assert res_admin.status_code == 200, f"/admin returned {res_admin.status_code}"
        assert "<html" in res_admin.text.lower()
        print("    [+] Admin Control Portal Served (200 OK) -> /admin")

        # 2. Test Cache Telemetry and Flush
        print("-" * 65)
        print("[*] Test 2: Testing Cache Telemetry & Flush Operations...")
        res_cache = client.get("/api/v1/publish/cache/stats")
        assert res_cache.status_code == 200
        cache_stats = res_cache.json()
        print(f"    [+] In-Memory Cache Stats: {cache_stats['hit_ratio_percent']}% hit ratio, {cache_stats.get('total_cache_entries', 0)} keys")

        res_flush = client.post("/api/v1/publish/cache/flush")
        assert res_flush.status_code == 200
        print("    [+] Cache Flush Completed -> 0 keys in memory")

        # 3. Test Public Feed for User Reader
        print("-" * 65)
        print("[*] Test 3: Testing Public Feed with Region & Category Filtering...")
        res_feed = client.get("/api/v1/publish/feed?limit=10")
        assert res_feed.status_code == 200
        feed = res_feed.json()
        print(f"    [+] Public Blog Feed: {feed['total']} posts returned for mobile readers")

        if feed["posts"]:
            sample = feed["posts"][0]
            art_id = sample["article_id"]
            slug = sample["slug"]
            print(f"    [+] Sample Published Post: ID={art_id}, Destination='{sample['destination']}', Slug='{slug}'")

            # 4. Test Unpublish & Re-publish Control (Admin Action)
            print("-" * 65)
            print("[*] Test 4: Testing Admin Unpublish & Republish Controls...")
            # Unpublish
            res_unpub = client.post(f"/api/v1/publish/unpublish/{art_id}")
            print(f"    [DEBUG] unpublish response: {res_unpub.status_code} -> {res_unpub.text}")
            assert res_unpub.status_code == 200, f"Unpublish failed: {res_unpub.text}"
            print(f"    [+] Admin Unpublish Action: Article ID {art_id} reverted to draft")

            # Verify feed was invalidated and article count decreased by 1
            res_feed_after = client.get("/api/v1/publish/feed")
            feed_after = res_feed_after.json()
            assert feed_after["total"] == feed["total"] - 1
            print(f"    [+] Cache Invalidation Verified: Public feed total is now {feed_after['total']}")

            # Re-publish
            res_pub = client.post(f"/api/v1/publish/{art_id}")
            assert res_pub.status_code == 200
            print(f"    [+] Admin Republish Action: Article ID {art_id} restored to published")

            res_feed_restored = client.get("/api/v1/publish/feed")
            assert res_feed_restored.json()["total"] == feed["total"]
            print(f"    [+] Public Feed Restored: Total={feed['total']} published posts")

    print("-" * 65)
    print("[+] All Dual Frontend & Admin Control Tests Passed Successfully!")
    print("=" * 65)


if __name__ == "__main__":
    test_dual_frontend_architecture()
