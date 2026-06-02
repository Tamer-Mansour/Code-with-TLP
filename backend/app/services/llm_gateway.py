"""Thin gateway to OpenAI-compatible LLM providers.

All providers listed here use the OpenAI Chat-Completion wire format, so a
single :func:`chat_complete` implementation covers them all.
"""

from __future__ import annotations

import json
from collections.abc import Iterator

import httpx
from fastapi import HTTPException

from app.schemas.chat import ProviderInfo

# ── Provider catalogue ──────────────────────────────────────────────────────

PROVIDERS: list[ProviderInfo] = [
    ProviderInfo(
        id="deepseek",
        name="DeepSeek",
        base_url="https://api.deepseek.com",
        models=["deepseek-chat", "deepseek-reasoner"],
        openai_compatible=True,
    ),
    ProviderInfo(
        id="openai",
        name="OpenAI",
        base_url="https://api.openai.com/v1",
        models=["gpt-4o-mini", "gpt-4o"],
        openai_compatible=True,
    ),
    ProviderInfo(
        id="qwen",
        name="Qwen (Alibaba)",
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        models=["qwen-plus", "qwen-turbo"],
        openai_compatible=True,
    ),
    ProviderInfo(
        id="moonshot",
        name="Moonshot",
        base_url="https://api.moonshot.cn/v1",
        models=["moonshot-v1-8k"],
        openai_compatible=True,
    ),
    ProviderInfo(
        id="zhipu",
        name="Zhipu (GLM)",
        base_url="https://open.bigmodel.cn/api/paas/v4",
        models=["glm-4-flash"],
        openai_compatible=True,
    ),
    ProviderInfo(
        id="groq",
        name="Groq",
        base_url="https://api.groq.com/openai/v1",
        models=["llama-3.3-70b-versatile"],
        openai_compatible=True,
    ),
    ProviderInfo(
        id="openrouter",
        name="OpenRouter",
        base_url="https://openrouter.ai/api/v1",
        models=["openai/gpt-4o-mini"],
        openai_compatible=True,
    ),
    ProviderInfo(
        id="gemini",
        name="Google Gemini",
        # Native Generative Language API (not OpenAI-compatible) — required for
        # google_search grounding. Routed through the dedicated gemini_* helpers.
        base_url="https://generativelanguage.googleapis.com/v1beta",
        models=[
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
        ],
        openai_compatible=False,
    ),
]

_PROVIDER_MAP: dict[str, ProviderInfo] = {p.id: p for p in PROVIDERS}


def get_provider(provider_id: str) -> ProviderInfo | None:
    return _PROVIDER_MAP.get(provider_id)


_GEMINI_DEFAULT_BASE = "https://generativelanguage.googleapis.com/v1beta"


def _gemini_payload(messages: list[dict], web_search: bool, model: str) -> dict:
    """Translate OpenAI-style messages into a Gemini generateContent payload."""
    system_parts: list[dict] = []
    contents: list[dict] = []
    for m in messages:
        text = m.get("content") or ""
        role = m.get("role")
        if role == "system":
            if text:
                system_parts.append({"text": text})
            continue
        gemini_role = "model" if role == "assistant" else "user"
        contents.append({"role": gemini_role, "parts": [{"text": text}]})

    payload: dict = {"contents": contents}
    if system_parts:
        payload["system_instruction"] = {"parts": system_parts}
    if web_search:
        # gemini-1.5 uses the legacy retrieval tool; 2.0+ uses google_search.
        if model.startswith("gemini-1.5"):
            payload["tools"] = [{"google_search_retrieval": {}}]
        else:
            payload["tools"] = [{"google_search": {}}]
    return payload


def gemini_complete(
    api_key: str,
    base_url: str,
    model: str,
    messages: list[dict],
    web_search: bool = False,
) -> str:
    """Call Gemini's native generateContent endpoint and return the reply text."""
    base = (base_url or _GEMINI_DEFAULT_BASE).rstrip("/")
    url = f"{base}/models/{model}:generateContent"
    payload = _gemini_payload(messages, web_search, model)
    try:
        response = httpx.post(url, params={"key": api_key}, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        parts = data["candidates"][0]["content"]["parts"]
        return "".join(p.get("text", "") for p in parts)
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Gemini error: {exc}",
        ) from exc


def gemini_complete_stream(
    api_key: str,
    base_url: str,
    model: str,
    messages: list[dict],
    web_search: bool = False,
) -> Iterator[str]:
    """Stream Gemini's native streamGenerateContent reply token-by-token (SSE)."""
    base = (base_url or _GEMINI_DEFAULT_BASE).rstrip("/")
    url = f"{base}/models/{model}:streamGenerateContent"
    payload = _gemini_payload(messages, web_search, model)
    try:
        with httpx.stream(
            "POST",
            url,
            params={"alt": "sse", "key": api_key},
            json=payload,
            timeout=httpx.Timeout(120.0, connect=15.0),
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line or not line.startswith("data:"):
                    continue
                raw = line[5:].strip()
                if not raw or raw == "[DONE]":
                    continue
                try:
                    obj = json.loads(raw)
                    parts = obj["candidates"][0]["content"]["parts"]
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
                for p in parts:
                    text = p.get("text")
                    if text:
                        yield text
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Gemini stream error: {exc}",
        ) from exc


# ── Chat completion ─────────────────────────────────────────────────────────

def chat_complete(
    provider: str,
    api_key: str,
    base_url: str,
    model: str,
    messages: list[dict],
) -> str:
    """Call the provider's chat-completion endpoint and return the reply text.

    All providers in :data:`PROVIDERS` expose the OpenAI wire format, so one
    implementation is sufficient.

    Raises :class:`fastapi.HTTPException` (502) on network or parse failures.
    """
    url = f"{base_url.rstrip('/')}/chat/completions"
    try:
        response = httpx.post(
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": model, "messages": messages},
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"LLM provider '{provider}' error: {exc}",
        ) from exc


def chat_complete_stream(
    provider: str,
    api_key: str,
    base_url: str,
    model: str,
    messages: list[dict],
) -> Iterator[str]:
    """Stream the provider's chat-completion reply token-by-token.

    Yields incremental text deltas. Uses the OpenAI-compatible SSE stream format
    (``data: {...}`` lines, terminated by ``data: [DONE]``).
    """
    url = f"{base_url.rstrip('/')}/chat/completions"
    try:
        with httpx.stream(
            "POST",
            url,
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": model, "messages": messages, "stream": True},
            timeout=httpx.Timeout(120.0, connect=15.0),
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                if line.startswith("data:"):
                    line = line[5:].strip()
                if not line or line == "[DONE]":
                    continue
                try:
                    obj = json.loads(line)
                    delta = obj["choices"][0]["delta"].get("content")
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue
                if delta:
                    yield delta
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"LLM provider '{provider}' stream error: {exc}",
        ) from exc
