"""
Hackathon data fetching.
Primary: Insights API. Fallback: static JSON URL.
Filters out past events before returning.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import httpx

from config import HACKATHONS_API_BASE, HACKATHONS_JSON_URL, MAX_HACKATHONS_DISPLAY

log = logging.getLogger("roommate.hackathons")

_http: httpx.AsyncClient | None = None


def _get_http() -> httpx.AsyncClient:
    global _http
    if _http is None or _http.is_closed:
        _http = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=5.0),
            follow_redirects=True,
        )
    return _http


def _is_future(event: dict[str, Any]) -> bool:
    """Return True if the event hasn't ended yet (or has no parseable date)."""
    now = datetime.now(timezone.utc)
    for key in ("end_date", "start_date"):
        raw = (event.get(key) or "").strip()
        if not raw:
            continue
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            return dt >= now
        except ValueError:
            pass
    return True  # unknown date → keep


async def fetch_upcoming(limit: int = MAX_HACKATHONS_DISPLAY) -> list[dict[str, Any]]:
    """Fetch and return upcoming hackathons, capped at `limit`."""
    client = _get_http()

    # Try Insights API
    if HACKATHONS_API_BASE:
        try:
            r = await client.get(
                f"{HACKATHONS_API_BASE.rstrip('/')}/hackathons/upcoming",
                params={"days": 365, "limit": 100},
            )
            r.raise_for_status()
            payload = r.json()
            events: list = payload.get("events", payload) if isinstance(payload, dict) else payload
            if isinstance(events, list) and events:
                return [e for e in events if _is_future(e)][:limit]
        except Exception as e:
            log.warning("Insights API unavailable: %s", e)

    # Fallback JSON
    try:
        r = await client.get(HACKATHONS_JSON_URL)
        r.raise_for_status()
        events = r.json()
        if isinstance(events, list):
            return [e for e in events if _is_future(e)][:limit]
    except Exception as e:
        log.warning("JSON fallback failed: %s", e)

    return []
