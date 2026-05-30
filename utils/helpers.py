"""Shared utility helpers used across cogs and services."""
from __future__ import annotations

from datetime import datetime, timezone

import discord


def sanitize(text: str, max_length: int = 100) -> str:
    """Escape markdown and truncate."""
    return discord.utils.escape_markdown(text.strip()[:max_length])


def format_date(raw: str | None) -> str:
    """Parse an ISO date string and return YYYY-MM-DD, or 'TBA'."""
    if not raw:
        return "TBA"
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return raw[:10] if len(raw) >= 10 else "TBA"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def chunk_text(text: str, size: int = 1024) -> list[str]:
    """Split long text into Discord-safe chunks."""
    return [text[i : i + size] for i in range(0, len(text), size)]
