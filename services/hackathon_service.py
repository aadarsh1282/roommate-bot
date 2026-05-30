"""
Hackathon data fetching with in-memory TTL cache.
Primary: Insights API. Fallback: static JSON URL.
Cache TTL: 1 hour — avoids hammering the API on every command call.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any

import httpx

from config import HACKATHONS_API_BASE, HACKATHONS_JSON_URL, MAX_HACKATHONS_DISPLAY, HACKATHONS_CACHE_TTL

log = logging.getLogger("roommate.hackathons")

_http: httpx.AsyncClient | None = None
_cache: tuple[float, list[dict[str, Any]]] | None = None  # (timestamp, events)


def _get_http() -> httpx.AsyncClient:
    global _http
    if _http is None or _http.is_closed:
        _http = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=5.0),
            follow_redirects=True,
        )
    return _http


def _is_future(event: dict[str, Any]) -> bool:
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
    return True


async def _fetch_raw() -> list[dict[str, Any]]:
    """Fetch from API or JSON fallback, no caching."""
    client = _get_http()

    if HACKATHONS_API_BASE:
        try:
            r = await client.get(
                f"{HACKATHONS_API_BASE.rstrip('/')}/hackathons/upcoming",
                params={"days": 365, "limit": 100},
            )
            r.raise_for_status()
            payload = r.json()
            events = payload.get("events", payload) if isinstance(payload, dict) else payload
            if isinstance(events, list) and events:
                log.info("Fetched %d events from Insights API", len(events))
                return events
        except Exception as e:
            log.warning("Insights API unavailable: %s", e)

    try:
        r = await client.get(HACKATHONS_JSON_URL)
        r.raise_for_status()
        events = r.json()
        if isinstance(events, list):
            log.info("Fetched %d events from JSON fallback", len(events))
            return events
    except Exception as e:
        log.warning("JSON fallback failed: %s", e)

    return []


async def fetch_upcoming(limit: int = MAX_HACKATHONS_DISPLAY) -> list[dict[str, Any]]:
    """Return upcoming events, served from cache when fresh."""
    global _cache

    now = time.monotonic()
    if _cache and (now - _cache[0]) < HACKATHONS_CACHE_TTL:
        log.info("Serving hackathons from cache")
        return _cache[1][:limit]

    raw = await _fetch_raw()
    future = [e for e in raw if _is_future(e)]
    _cache = (now, future)
    log.info("Cache refreshed — %d future events", len(future))
    return future[:limit]
