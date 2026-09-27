#!/usr/bin/env python3
"""
omni-model-router — Lightweight OpenRouter model router & health checker.

A CLI tool that tests, benchmarks, and auto-selects the best available
free AI model from OpenRouter's catalog. Useful for developers who want
to use free LLM models in their projects without worrying about which
ones are currently available and responsive.

MIT License — Jay Patel (2026)
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

__version__ = "1.0.0"

# Top free models on OpenRouter, ordered by quality
FREE_MODELS = [
    "google/gemini-2.5-flash:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen3-coder:free",
    "deepseek/deepseek-r1-0528:free",
    "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
    "microsoft/mai-ds-r1:free",
    "google/gemma-3-27b-it:free",
    "mistralai/mistral-small-3.2-24b-instruct:free",
]

OPENROUTER_API = "https://openrouter.ai/api/v1/chat/completions"


def test_model(model: str, api_key: str, timeout: int = 15) -> dict:
    """Test a single model and return latency + status."""
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": "Say 'ok' and nothing else."}],
        "max_tokens": 5,
    }).encode("utf-8")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/jaypatel29042008-glitch/omni-model-router",
    }

    req = urllib.request.Request(OPENROUTER_API, data=payload, headers=headers)
    start = time.time()

    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        data = json.loads(resp.read().decode())
        latency = round((time.time() - start) * 1000)
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return {
            "model": model,
            "status": "ok",
            "latency_ms": latency,
            "response": content.strip()[:50],
        }
    except urllib.error.HTTPError as e:
        return {
            "model": model,
            "status": f"error-{e.code}",
            "latency_ms": round((time.time() - start) * 1000),
            "response": str(e.reason),
        }
    except Exception as e:
        return {
            "model": model,
            "status": "timeout",
            "latency_ms": round((time.time() - start) * 1000),
            "response": str(e)[:50],
        }


def check_key(api_key: str) -> dict:
    """Validate an OpenRouter API key."""
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/auth/key",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode())
        info = data.get("data", {})
        return {
            "valid": True,
            "label": info.get("label", ""),
            "usage": info.get("usage", 0),
            "limit": info.get("limit"),
        }
    except Exception as e:
        return {"valid": False, "error": str(e)}


def list_free_models(api_key: str) -> list:
    """List all free models available on OpenRouter."""
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/models",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode())
        free = [
            m["id"] for m in data.get("data", [])
            if m["id"].endswith(":free") or "free" in m["id"]
        ]
        return sorted(free)
    except Exception:
        return []


def auto_select(api_key: str, models: list = None, timeout: int = 15) -> str | None:
    """Test models in parallel and return the fastest working one."""
    if models is None:
        models = FREE_MODELS

    results = []
    with ThreadPoolExecutor(max_workers=min(len(models), 8)) as pool:
        futures = {pool.submit(test_model, m, api_key, timeout): m for m in models}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)

    working = [r for r in results if r["status"] == "ok"]
    if not working:
        return None

    best = min(working, key=lambda r: r["latency_ms"])
    return best["model"]


def main():
    parser = argparse.ArgumentParser(
        prog="omni-model-router",
        description="Test, benchmark, and auto-select the best free AI model from OpenRouter.",
    )
    parser.add_argument("--key", "-k", required=True, help="OpenRouter API key (sk-or-...)")
    parser.add_argument("--timeout", "-t", type=int, default=15, help="Timeout per model (seconds)")

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("check", help="Validate your API key")
    sub.add_parser("list", help="List all available free models")
    sub.add_parser("bench", help="Benchmark all free models")
    sub.add_parser("auto", help="Auto-select the fastest working free model")

    test_parser = sub.add_parser("test", help="Test a specific model")
    test_parser.add_argument("model", help="Model ID to test")

    args = parser.parse_args()

    if args.command == "check":
        result = check_key(args.key)
        print(json.dumps(result, indent=2))

    elif args.command == "list":
        models = list_free_models(args.key)
        for m in models:
            print(m)
        print(f"\nTotal: {len(models)} free models")

    elif args.command == "test":
        result = test_model(args.model, args.key, args.timeout)
        print(json.dumps(result, indent=2))

    elif args.command == "bench":
        print(f"Benchmarking {len(FREE_MODELS)} models...\n")
        print(f"{'Model':<55} {'Status':<12} {'Latency':<10} {'Response'}")
        print("-" * 100)

        results = []
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {pool.submit(test_model, m, args.key, args.timeout): m for m in FREE_MODELS}
            for future in as_completed(futures):
                r = future.result()
                results.append(r)
                status_icon = "✅" if r["status"] == "ok" else "❌"
                print(f"{r['model']:<55} {status_icon} {r['status']:<10} {r['latency_ms']}ms{'':<5} {r['response']}")

        working = [r for r in results if r["status"] == "ok"]
        print(f"\n{len(working)}/{len(FREE_MODELS)} models responding")
        if working:
            best = min(working, key=lambda r: r["latency_ms"])
            print(f"Fastest: {best['model']} ({best['latency_ms']}ms)")

    elif args.command == "auto":
        print("Auto-selecting best model...")
        model = auto_select(args.key, timeout=args.timeout)
        if model:
            print(f"\n✅ Best model: {model}")
            print(f"\nTo use in Claude Code settings.json:")
            print(f'  "ANTHROPIC_MODEL": "{model}"')
        else:
            print("\n❌ No models available right now. Try again in 60 seconds.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
