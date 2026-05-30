"""
Supabase integration — optional persistent storage layer.
Falls back silently to JSON file storage when not configured.

Setup (optional):
  1. Create a free project at supabase.com
  2. Run supabase_schema.sql in the SQL editor
  3. Add SUPABASE_URL and SUPABASE_KEY to .env
"""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

log = logging.getLogger("roommate.db")

_client = None
_available = False


def init() -> bool:
    """Attempt to connect to Supabase. Returns True if successful."""
    global _client, _available

    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")

    if not url or not key:
        log.info("Supabase not configured — using local JSON storage")
        return False

    try:
        from supabase import create_client
        _client = create_client(url, key)
        _available = True
        log.info("Supabase connected ✅")
        return True
    except ImportError:
        log.warning("supabase package not installed — run: pip install supabase")
        return False
    except Exception as e:
        log.error("Supabase connection failed: %s", e)
        return False


def is_available() -> bool:
    return _available


# ── Team Profiles ─────────────────────────────────────────────────────────────

async def upsert_profile(user_id: str, profile: dict[str, Any]) -> None:
    if not _available:
        return
    try:
        await asyncio.to_thread(
            lambda: _client.table("team_profiles")
            .upsert({"user_id": user_id, **profile})
            .execute()
        )
    except Exception as e:
        log.error("upsert_profile failed: %s", e)


async def fetch_all_profiles() -> dict[str, Any]:
    if not _available:
        return {}
    try:
        result = await asyncio.to_thread(
            lambda: _client.table("team_profiles").select("*").execute()
        )
        return {row["user_id"]: row for row in (result.data or [])}
    except Exception as e:
        log.error("fetch_all_profiles failed: %s", e)
        return {}


# ── Winners ───────────────────────────────────────────────────────────────────

async def upsert_winner(hackathon: str, entry: dict[str, Any]) -> None:
    if not _available:
        return
    try:
        await asyncio.to_thread(
            lambda: _client.table("winners")
            .upsert({"hackathon": hackathon, **entry})
            .execute()
        )
    except Exception as e:
        log.error("upsert_winner failed: %s", e)


async def fetch_all_winners() -> dict[str, Any]:
    if not _available:
        return {}
    try:
        result = await asyncio.to_thread(
            lambda: _client.table("winners").select("*").execute()
        )
        return {row["hackathon"]: row for row in (result.data or [])}
    except Exception as e:
        log.error("fetch_all_winners failed: %s", e)
        return {}
