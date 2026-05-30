"""
OpenAI integration — single async client, reusable chat helper.
All AI calls go through here.
"""
from __future__ import annotations

import logging
import os

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
    max_tokens: int = 500,
    temperature: float = 0.7,
) -> str:
    """Send a chat completion request and return the response text."""
    client = get_client()
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return (response.choices[0].message.content or "").strip()
    except Exception as e:
        log.error("OpenAI request failed: %s", e)
        raise
