"""Ephemeral storage for in-flight battle state.

A battle lives in Redis (via ctx.ephemeral semantics, but we use kv with
a short TTL because ephemeral doesn't store arbitrary JSON). 30-minute
TTL is plenty for one PvE encounter; abandoned battles auto-expire.
"""
from __future__ import annotations

import json
from typing import Any, Optional

from mmo_maid_sdk import Context


_BATTLE_TTL_S = 30 * 60  # 30 minutes


def _key(user_id: str) -> str:
    return f"battle:{user_id}"


def load(ctx: Context, user_id: str) -> Optional[dict[str, Any]]:
    raw = ctx.kv.get(_key(user_id))
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except Exception:
            return None
    return None


def save(ctx: Context, user_id: str, state: dict[str, Any]) -> None:
    ctx.kv.set(_key(user_id), state, ttl_seconds=_BATTLE_TTL_S)


def clear(ctx: Context, user_id: str) -> None:
    ctx.kv.delete(_key(user_id))


def has_active(ctx: Context, user_id: str) -> bool:
    return load(ctx, user_id) is not None
