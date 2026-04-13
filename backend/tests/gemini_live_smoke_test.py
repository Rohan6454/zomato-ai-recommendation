from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Tuple

import httpx


def load_env_file(path: Path) -> Dict[str, str]:
    data: Dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        data[k.strip()] = v.strip().strip('"').strip("'")
    return data


def call_gemini(*, api_key: str, model: str, prompt: str, timeout_s: float = 20.0) -> Tuple[int, str, int]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    params = {"key": api_key}
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ]
    }

    start = time.perf_counter()
    with httpx.Client(timeout=timeout_s) as client:
        resp = client.post(url, params=params, json=payload)
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    if resp.status_code != 200:
        return resp.status_code, resp.text[:300], elapsed_ms

    data = resp.json()
    text = ""
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        text = json.dumps(data)[:300]
    return resp.status_code, text, elapsed_ms


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    env_path = root / ".env"
    if not env_path.exists():
        legacy_path = root / "APIKey.env"
        if legacy_path.exists():
            env_path = legacy_path
        else:
            print("ERROR: .env not found at repository root.")
            return 1

    env = load_env_file(env_path)
    api_key = env.get("GEMINI_API_KEY", "")
    model = env.get("GEMINI_MODEL", "gemini-1.5-flash")

    if not api_key:
        print(f"ERROR: GEMINI_API_KEY missing in {env_path.name}.")
        return 1

    tests = [
        ("T1_basic", "Reply with exactly: GEMINI_OK"),
        ("T2_reasoning", "What is 17 + 25? Reply with number only."),
        (
            "T3_json",
            'Return valid JSON only: {"status":"ok","domain":"restaurant-recommendation"}',
        ),
    ]

    print(f"Running {len(tests)} live Gemini tests with model={model}")
    pass_count = 0
    for name, prompt in tests:
        status, body, elapsed_ms = call_gemini(api_key=api_key, model=model, prompt=prompt)
        ok = status == 200 and len(body.strip()) > 0
        if ok:
            pass_count += 1
        snippet = body.strip().replace("\n", " ")[:120]
        print(f"{name}: status={status} latency_ms={elapsed_ms} pass={ok} response_snippet={snippet}")

    print(f"Summary: {pass_count}/{len(tests)} passed")
    return 0 if pass_count == len(tests) else 2


if __name__ == "__main__":
    raise SystemExit(main())

