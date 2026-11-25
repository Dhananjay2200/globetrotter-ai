"""
Standalone Diagnostic Script: Test NVIDIA NIM Connectivity.
Run this script to verify your NVIDIA API key and model response.

Usage:
    python test_nim.py
"""

import sys
import time
from app.config import get_settings
from app.llm import get_chat_llm
from app.utils.logging import logger


def run_nim_test():
    settings = get_settings()
    print("=" * 65)
    print(" GlobeTrotter AI - NVIDIA NIM Connection Diagnostic")
    print("=" * 65)
    print(f"Base URL   : {settings.NVIDIA_BASE_URL}")
    print(f"Model ID   : {settings.NVIDIA_MODEL_NAME}")
    
    masked_key = (
        settings.NVIDIA_API_KEY[:8] + "..." + settings.NVIDIA_API_KEY[-4:]
        if len(settings.NVIDIA_API_KEY) > 12
        else "NOT CONFIGURED"
    )
    print(f"API Key    : {masked_key}")
    print("-" * 65)

    if not settings.NVIDIA_API_KEY or settings.NVIDIA_API_KEY.startswith("nvapi-placeholder"):
        print("[!] ERROR: Valid NVIDIA_API_KEY not found in .env file.")
        print("    Please copy .env.example to .env and insert your key from:")
        print("    https://build.nvidia.com")
        sys.exit(1)

    print("[*] Dispatching test prompt to NVIDIA NIM endpoint via LangChain...")
    try:
        llm = get_chat_llm(max_tokens=150, temperature=0.3)
        start_time = time.perf_counter()

        prompt = (
            "You are GlobeTrotter AI. In 2 concise sentences, describe why Petra, Jordan "
            "is an essential historical destination for global travelers."
        )
        response = llm.invoke(prompt)
        elapsed = round((time.perf_counter() - start_time) * 1000, 2)

        print(f"[+] Success! Response received in {elapsed} ms:\n")
        print(f"    \"{response.content.strip()}\"\n")
        print("-" * 65)
        print("[+] LangChain <-> NVIDIA NIM integration verified successfully.")
        print("=" * 65)

    except Exception as exc:
        print(f"\n[-] FAILED to communicate with NVIDIA NIM API:")
        print(f"    Error: {exc}")
        print("\nTroubleshooting tips:")
        print(" 1. Check if NVIDIA_API_KEY starts with 'nvapi-'.")
        print(" 2. Confirm internet connection and proxy settings.")
        print(" 3. Check NVIDIA API quota / rate limits at https://build.nvidia.com.")
        sys.exit(1)


if __name__ == "__main__":
    run_nim_test()
