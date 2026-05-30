"""
AI-powered team matching.
Saves profiles to storage, uses OpenAI to reason about compatibility.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from services.openai_service import chat
from services.storage_service import get_all_profiles, save_profile
from config import MATCH_SYSTEM

log = logging.getLogger("roommate.teams")


async def register_profile(user_id: str, username: str, profile: dict[str, Any]) -> None:
    profile["username"] = username
    await save_profile(user_id, profile)


async def find_matches(seeker_id: str, seeker_profile: dict[str, Any]) -> str:
    """Return AI-generated match suggestions for the seeker."""
    all_profiles = await get_all_profiles()
    candidates = [
        {**v, "user_id": k}
        for k, v in all_profiles.items()
        if k != seeker_id
    ]

    if not candidates:
        return (
            "No other registered profiles yet — you're the first! 🚀\n"
            "Share this server with teammates and ask them to run `/team-match` too."
        )

    prompt = (
        f"Seeker profile:\n{json.dumps(seeker_profile, indent=2)}\n\n"
        f"Available candidates ({len(candidates)} total):\n"
        f"{json.dumps(candidates[:20], indent=2)}\n\n"
        "Return the top 3 best teammates with their Discord username, "
        "a compatibility score out of 10, and one sentence of reasoning."
    )

    return await chat(prompt, system=MATCH_SYSTEM, max_tokens=600, temperature=0.5)
