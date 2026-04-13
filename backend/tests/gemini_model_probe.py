from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

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


def probe_model(api_key: str, model: str) -> Tuple[int, str]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {"contents": [{"role": "user", "parts": [{"text": "Reply with OK"}]}]}
    try:
        with httpx.Client(timeout=20.0) as client:
            resp = client.post(url, params={"key": api_key}, json=payload)
        if resp.status_code == 200:
            return 200, "OK"
        text = resp.text.replace("\n", " ")[:180]
        return resp.status_code, text
    except Exception as e:  # noqa: BLE001
        return 0, f"ERROR: {type(e).__name__}: {e}"


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    env_path = root / ".env"
    if not env_path.exists():
        print("ERROR: .env not found at repository root.")
        return 1

    env = load_env_file(env_path)
    api_key = env.get("GEMINI_API_KEY", "")
    if not api_key:
        print("ERROR: GEMINI_API_KEY missing in .env.")
        return 1

    # Keep this list small and practical.
    candidates: List[str] = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-2.0-flash",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
    ]

    print(f"Probing {len(candidates)} Gemini model names...")
    ok_models: List[str] = []
    for model in candidates:
        status, info = probe_model(api_key, model)
        is_ok = status == 200
        if is_ok:
            ok_models.append(model)
        print(f"{model}: status={status} pass={is_ok} info={info}")

    print("-" * 60)
    if ok_models:
        print("Working models:")
        for m in ok_models:
            print(f"- {m}")
        return 0

    print("No probed model name worked with current key/endpoint.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

