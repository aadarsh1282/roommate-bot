"""
Async JSON storage for winners and team profiles.
Single lock prevents concurrent write corruption.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any

import aiofiles

from config import DATA_DIR, WINNERS_FILE, TEAMS_FILE

log = logging.getLogger("roommate.storage")

_lock = asyncio.Lock()


def _ensure_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


async def _read(path: str) -> dict[str, Any]:
    if not os.path.exists(path):
        return {}
    try:
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            return json.loads(await f.read())
    except Exception as e:
        log.warning("Read failed (%s): %s", path, e)
        return {}


async def _write(path: str, data: dict[str, Any]) -> None:
    _ensure_dir()
    async with _lock:
        try:
            async with aiofiles.open(path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            log.error("Write failed (%s): %s", path, e)


# ── Winners ──────────────────────────────────────────────────────────────────

async def get_winners() -> dict[str, Any]:
    return await _read(WINNERS_FILE)


async def save_winner(hackathon: str, entry: dict[str, Any]) -> None:
    winners = await get_winners()
    winners[hackathon] = entry
    await _write(WINNERS_FILE, winners)


# ── Team Profiles ─────────────────────────────────────────────────────────────

async def get_all_profiles() -> dict[str, Any]:
    return await _read(TEAMS_FILE)


async def save_profile(user_id: str, profile: dict[str, Any]) -> None:
    profiles = await get_all_profiles()
    profiles[user_id] = profile
    await _write(TEAMS_FILE, profiles)


async def get_profile(user_id: str) -> dict[str, Any] | None:
    profiles = await get_all_profiles()
    return profiles.get(user_id)
