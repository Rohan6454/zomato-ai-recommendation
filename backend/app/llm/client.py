from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional, Protocol


class LLMClient(Protocol):
    def generate(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str: ...


@dataclass(frozen=True)
class LLMRequestMetadata:
    model: str
    temperature: float
    max_tokens: int


class OpenAICompatibleClient:
    """
    Minimal OpenAI-compatible Chat Completions client.

    Works with OpenAI/Azure/OpenAI-compatible gateways that expose:
      POST {base_url}/v1/chat/completions

    Notes:
    - This is intentionally lightweight and provider-agnostic.
    - We log only metadata (duration/model), not full prompt content.
    """

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str = "https://api.openai.com",
        timeout_s: float = 20.0,
        max_retries: int = 2,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout_s = timeout_s
        self._max_retries = max_retries

    def generate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 500,
    ) -> str:
        meta = LLMRequestMetadata(
            model=model or self._model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return _chat_completions_with_retries(
            base_url=self._base_url,
            api_key=self._api_key,
            prompt=prompt,
            meta=meta,
            timeout_s=self._timeout_s,
            max_retries=self._max_retries,
        )


class MockLLMClient:
    """Deterministic LLM client for tests."""

    def __init__(self, response_text: str) -> None:
        self._response_text = response_text

    def generate(self, prompt: str, *, model: str, temperature: float, max_tokens: int) -> str:
        return self._response_text


def _chat_completions_with_retries(
    *,
    base_url: str,
    api_key: str,
    prompt: str,
    meta: LLMRequestMetadata,
    timeout_s: float,
    max_retries: int,
) -> str:
    # Local import so tests can run without installing httpx when using MockLLMClient.
    import httpx

    url = f"{base_url}/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": meta.model,
        "temperature": meta.temperature,
        "max_tokens": meta.max_tokens,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    }

    attempt = 0
    last_error: Optional[Exception] = None
    while attempt <= max_retries:
        attempt += 1
        start = time.perf_counter()
        try:
            with httpx.Client(timeout=timeout_s) as client:
                resp = client.post(url, headers=headers, json=payload)
            duration_ms = int((time.perf_counter() - start) * 1000)
            # Basic metadata logging (stdout). Avoid logging prompt content.
            print(
                f"[llm] model={meta.model} temp={meta.temperature} max_tokens={meta.max_tokens} "
                f"status={resp.status_code} duration_ms={duration_ms}"
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except (httpx.TimeoutException, httpx.TransportError, httpx.HTTPStatusError, KeyError, IndexError) as e:
            last_error = e
            if attempt > max_retries:
                break
            # simple backoff
            time.sleep(0.4 * attempt)

    raise RuntimeError("LLM request failed after retries") from last_error

