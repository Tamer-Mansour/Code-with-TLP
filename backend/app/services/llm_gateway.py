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
]

_PROVIDER_MAP: dict[str, ProviderInfo] = {p.id: p for p in PROVIDERS}


def get_provider(provider_id: str) -> ProviderInfo | None:
    return _PROVIDER_MAP.get(provider_id)


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
