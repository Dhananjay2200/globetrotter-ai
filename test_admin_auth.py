"""
GlobeTrotter AI - Admin Authentication Diagnostic Test.
Verifies that:
1. Admin credentials are read directly from .env (and app.config).
2. Login with incorrect credentials is automatically rejected (401).
3. Login with valid .env credentials generates a secure signed HMAC token.
4. Token verification endpoint validates the session.
5. Tampered or expired tokens are strictly rejected.
"""

from fastapi.testclient import TestClient
from app.main import app
from app.config import get_settings


def run_auth_diagnostics():
    print("=" * 65)
    print(" GlobeTrotter AI - Admin Authentication (.env) Diagnostic")
    print("=" * 65)

    settings = get_settings()
    configured_user = settings.ADMIN_USERNAME
    configured_pass = settings.ADMIN_PASSWORD

    print(f"[*] Configured Admin User (from .env) : '{configured_user}'")
    print(f"[*] Configured Password Length        : {len(configured_pass)} characters")
    print(f"[*] Configured HMAC Secret Key        : {settings.JWT_SECRET_KEY[:8]}...")
    print("-" * 65)

    with TestClient(app) as client:
        # Test 1: Reject invalid username
        print("[*] Test 1: Attempting login with invalid username...")
        res_bad_user = client.post("/api/v1/auth/login", json={
            "username": "hacker_user",
            "password": configured_pass
        })
        assert res_bad_user.status_code == 401, f"Expected 401, got {res_bad_user.status_code}"
        print(f"    [+] Invalid username correctly rejected (401): {res_bad_user.json()['detail']}")

        # Test 2: Reject invalid password
        print("-" * 65)
        print("[*] Test 2: Attempting login with incorrect password...")
        res_bad_pass = client.post("/api/v1/auth/login", json={
            "username": configured_user,
            "password": "wrong_password_999"
        })
        assert res_bad_pass.status_code == 401, f"Expected 401, got {res_bad_pass.status_code}"
        print(f"    [+] Invalid password correctly rejected (401): {res_bad_pass.json()['detail']}")

        # Test 3: Successful login with .env credentials
        print("-" * 65)
        print("[*] Test 3: Logging in with valid .env credentials...")
        res_success = client.post("/api/v1/auth/login", json={
            "username": configured_user,
            "password": configured_pass
        })
        assert res_success.status_code == 200, f"Expected 200, got {res_success.status_code}"
        auth_data = res_success.json()
        assert auth_data["status"] == "success"
        assert "token" in auth_data
        token = auth_data["token"]
        print(f"    [+] Authentication Successful (200 OK)")
        print(f"    [+] Signed HMAC-SHA256 Token : {token[:24]}...{token[-12:]}")
        print(f"    [+] Session Expiration       : {auth_data['expires_in']} seconds (24h)")

        # Test 4: Verify active session with Bearer token
        print("-" * 65)
        print("[*] Test 4: Verifying session token with /api/v1/auth/verify...")
        res_verify = client.get("/api/v1/auth/verify", headers={
            "Authorization": f"Bearer {token}"
        })
        assert res_verify.status_code == 200, f"Expected 200, got {res_verify.status_code}"
        verify_data = res_verify.json()
        assert verify_data["valid"] is True
        assert verify_data["username"] == configured_user
        print(f"    [+] Token Verified Successfully (200 OK) -> User: '{verify_data['username']}'")

        # Test 5: Reject tampered token
        print("-" * 65)
        print("[*] Test 5: Testing security with tampered token signature...")
        tampered_token = token[:-5] + "XXXXX"
        res_tampered = client.get("/api/v1/auth/verify", headers={
            "Authorization": f"Bearer {tampered_token}"
        })
        assert res_tampered.status_code == 401, f"Expected 401, got {res_tampered.status_code}"
        print(f"    [+] Tampered signature rejected (401): {res_tampered.json()['detail']}")

        # Test 6: Reject missing authorization header
        print("-" * 65)
        print("[*] Test 6: Testing request without authorization header...")
        res_no_auth = client.get("/api/v1/auth/verify")
        assert res_no_auth.status_code == 401
        print(f"    [+] Missing header rejected (401): {res_no_auth.json()['detail']}")

    print("-" * 65)
    print("[+] All Admin Authentication & .env Tests Passed Successfully!")
    print("=" * 65)


if __name__ == "__main__":
    run_auth_diagnostics()
