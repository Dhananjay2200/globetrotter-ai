"""
GlobeTrotter AI - Phase 11 Diagnostic: React Frontend & Dashboard Integration Test.
Verifies the Vite + React build, asset bundle integrity, and FastAPI static serving endpoints.
"""

import os
import sys
from fastapi.testclient import TestClient
from app.main import app


def run_frontend_diagnostics():
    print("=" * 65)
    print(" GlobeTrotter AI - Phase 11: React Frontend & Dashboard Diagnostic")
    print("=" * 65)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(base_dir, "frontend", "dist")
    index_html = os.path.join(dist_dir, "index.html")
    assets_dir = os.path.join(dist_dir, "assets")

    # 1. Verify build artifacts on disk
    print("[*] Test 1: Verifying Vite Production Build Artifacts...")
    assert os.path.exists(dist_dir), f"frontend/dist directory missing at {dist_dir}!"
    assert os.path.exists(index_html), f"index.html missing at {index_html}!"
    assert os.path.exists(assets_dir), f"assets directory missing at {assets_dir}!"

    asset_files = os.listdir(assets_dir)
    js_bundle = next((f for f in asset_files if f.endswith(".js")), None)
    css_bundle = next((f for f in asset_files if f.endswith(".css")), None)

    assert js_bundle is not None, "JavaScript bundle (.js) missing from assets!"
    assert css_bundle is not None, "Tailwind CSS bundle (.css) missing from assets!"

    print(f"[+] Found compiled production bundle in 'frontend/dist/':")
    print(f"    - HTML Entrypoint : {index_html} ({os.path.getsize(index_html)} bytes)")
    print(f"    - JavaScript App  : {js_bundle} ({os.path.getsize(os.path.join(assets_dir, js_bundle)) // 1024} KB)")
    print(f"    - Stylesheet CSS  : {css_bundle} ({os.path.getsize(os.path.join(assets_dir, css_bundle)) // 1024} KB)")

    print("-" * 65)

    # 2. Test FastAPI TestClient Integration
    print("[*] Test 2: Testing FastAPI Web Endpoints with TestClient...")
    with TestClient(app) as client:
        # Check API root
        res_root = client.get("/")
        assert res_root.status_code == 200, f"Root endpoint returned {res_root.status_code}"
        root_data = res_root.json()
        assert "react_app" in root_data, "react_app link missing from root!"
        print(f"    [+] API Root Endpoint (200 OK) -> {root_data['message']}")

        # Check React App SPA serving
        res_app = client.get("/app")
        assert res_app.status_code == 200, f"/app endpoint returned {res_app.status_code}"
        assert "<html" in res_app.text.lower(), "/app did not return HTML content!"
        print(f"    [+] React SPA Serving Endpoint (200 OK) -> /app ({len(res_app.text)} chars HTML)")

        # Check static asset serving
        res_js = client.get(f"/assets/{js_bundle}")
        assert res_js.status_code == 200, f"Static asset {js_bundle} returned {res_js.status_code}"
        print(f"    [+] Static JS Bundle Served (200 OK) -> /assets/{js_bundle}")

        res_css = client.get(f"/assets/{css_bundle}")
        assert res_css.status_code == 200, f"Static asset {css_bundle} returned {res_css.status_code}"
        print(f"    [+] Static CSS Bundle Served (200 OK) -> /assets/{css_bundle}")

        # Check Public Blog Feed
        res_feed = client.get("/api/v1/publish/feed")
        assert res_feed.status_code == 200, f"/api/v1/publish/feed returned {res_feed.status_code}"
        feed_data = res_feed.json()
        print(f"    [+] Public Blog Feed API (200 OK) -> {feed_data['total']} published posts available")

    print("-" * 65)
    print("[+] Phase 11 React Frontend & Dashboard Diagnostic Passed Successfully!")
    print("=" * 65)


if __name__ == "__main__":
    run_frontend_diagnostics()
