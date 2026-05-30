"""
Per-user conversation memory for /ask.
Keeps the last N message pairs in memory so context carries across calls.
Resets if the bot restarts (intentional — memory is session-scoped).
"""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

MAX_MESSAGES = 10  # 5 exchanges (user + assistant = 2 per exchange)

_history: dict[int, deque[dict[str, str]]] = defaultdict(
    lambda: deque(maxlen=MAX_MESSAGES)
)


def add_exchange(user_id: int, user_msg: str, assistant_msg: str) -> None:
    _history[user_id].append({"role": "user", "content": user_msg})
    _history[user_id].append({"role": "assistant", "content": assistant_msg})


def get_history(user_id: int) -> list[dict[str, Any]]:
    return list(_history[user_id])


def clear(user_id: int) -> None:
    _history[user_id].clear()
