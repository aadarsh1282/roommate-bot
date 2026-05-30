"""
OpenAI integration — single async client, reusable helpers.
Supports stateless chat and stateful chat-with-history.
"""
from __future__ import annotations

import logging
import os
from typing import Any

from openai import AsyncOpenAI

from config import OPENAI_MODEL, SYSTEM_PROMPT

log = logging.getLogger("roommate.openai")

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        _client = AsyncOpenAI(api_key=api_key)
    return _client


async def chat(
    prompt: str,
    *,
    system: str = SYSTEM_PROMPT,
    model: str = OPENAI_MODEL,
    max_tokens: int = 400,
    temperature: float = 0.7,
) -> str:
    """Stateless single-turn chat completion."""
    return await chat_with_history(
        messages=[{"role": "user", "content": prompt}],
        system=system,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
    )


async def chat_with_history(
    messages: list[dict[str, Any]],
    *,
    system: str = SYSTEM_PROMPT,
    model: str = OPENAI_MODEL,
    max_tokens: int = 400,
    temperature: float = 0.7,
) -> str:
    """Multi-turn chat with injected message history."""
    client = get_client()
    full_messages = [{"role": "system", "content": system}, *messages]
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=full_messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return (response.choices[0].message.content or "").strip()
    except Exception as e:
        log.error("OpenAI request failed: %s", e)
        raise
