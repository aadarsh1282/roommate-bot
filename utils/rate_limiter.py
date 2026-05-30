"""Per-user, per-command cooldown decorator."""
from __future__ import annotations

import time
from collections import defaultdict
from functools import wraps
from typing import Callable

import discord

# {command_name: {user_id: last_used_timestamp}}
_cooldowns: dict[str, dict[int, float]] = defaultdict(dict)


def cooldown(seconds: int) -> Callable:
    """Apply a per-user cooldown to a slash command method."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            uid = interaction.user.id
            cmd = func.__name__
            now = time.monotonic()
            remaining = seconds - (now - _cooldowns[cmd].get(uid, 0))
            if remaining > 0:
                await interaction.response.send_message(
                    f"⏳ Slow down! Try again in **{remaining:.1f}s**.",
                    ephemeral=True,
                )
                return
            _cooldowns[cmd][uid] = now
            return await func(self, interaction, *args, **kwargs)
        return wrapper
    return decorator
