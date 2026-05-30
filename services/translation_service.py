"""
Multilingual assistance via OpenAI.
Detects language automatically and responds in kind.
"""
from __future__ import annotations

from services.openai_service import chat
from config import MULTILINGUAL_SYSTEM


async def multilingual_answer(question: str) -> str:
    """Detect language of `question` and respond in the same language."""
    return await chat(
        question,
        system=MULTILINGUAL_SYSTEM,
        max_tokens=600,
        temperature=0.6,
    )
