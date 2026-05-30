"""
Storage layer — writes to Supabase when available, JSON files otherwise.
Transparent fallback: the rest of the codebase calls these functions
without knowing which backend is active.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any

import aiofiles

from config import DATA_DIR, WINNERS_FILE, TEAMS_FILE
from services import db_service

log = logging.getLogger("roommate.storage")

_lock = asyncio.Lock()


def _ensure_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


# ── JSON helpers ──────────────────────────────────────────────────────────────

async def _read_json(path: str) -> dict[str, Any]:
    if not os.path.exists(path):
        return {}
    try:
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            return json.loads(await f.read())
    except Exception as e:
        log.warning("JSON read failed (%s): %s", path, e)
        return {}


async def _write_json(path: str, data: dict[str, Any]) -> None:
    _ensure_dir()
    async with _lock:
        try:
            async with aiofiles.open(path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            log.error("JSON write failed (%s): %s", path, e)


# ── Winners ───────────────────────────────────────────────────────────────────

async def get_winners() -> dict[str, Any]:
    if db_service.is_available():
        return await db_service.fetch_all_winners()
    return await _read_json(WINNERS_FILE)


async def save_winner(hackathon: str, entry: dict[str, Any]) -> None:
    if db_service.is_available():
        await db_service.upsert_winner(hackathon, entry)
        return
    winners = await _read_json(WINNERS_FILE)
    winners[hackathon] = entry
    await _write_json(WINNERS_FILE, winners)


# ── Team Profiles ─────────────────────────────────────────────────────────────

async def get_all_profiles() -> dict[str, Any]:
    if db_service.is_available():
        return await db_service.fetch_all_profiles()
    return await _read_json(TEAMS_FILE)


async def save_profile(user_id: str, profile: dict[str, Any]) -> None:
    if db_service.is_available():
        await db_service.upsert_profile(user_id, profile)
        return
    profiles = await _read_json(TEAMS_FILE)
    profiles[user_id] = profile
    await _write_json(TEAMS_FILE, profiles)


async def get_profile(user_id: str) -> dict[str, Any] | None:
    profiles = await get_all_profiles()
    return profiles.get(user_id)
