"""Shared state for in-flight PvP duels.

Stored per-server (KV is per-server anyway) keyed by a random duel id.
Both players' clients reference the same record by duel_id, so either
side's button click loads-mutates-saves the same state.

There are also two thin pointer keys for finding a player's active
challenge or duel from their user_id:

    pending_duel:{user_id}   -> duel_id (TTL ~60s)
    active_duel:{user_id}    -> duel_id (TTL 30min)

These let a player be in at most one challenge / one duel at a time
and let the handler find the duel from a button click without parsing
the custom_id payload.
"""
from __future__ import annotations

import secrets
from typing import Any, Optional

from mmo_maid_sdk import Context

PENDING_TTL_S = 90
ACTIVE_TTL_S = 30 * 60


def new_duel_id() -> str:
    return secrets.token_hex(6)   # 12 hex chars — fits well under custom_id 100-char limit


def _key(duel_id: str) -> str:
    return f"duel:{duel_id}"


def load(ctx: Context, duel_id: str) -> Optional[dict[str, Any]]:
    raw = ctx.kv.get(_key(duel_id))
    return raw if isinstance(raw, dict) else None


def save(ctx: Context, duel_id: str, state: dict[str, Any], *, ttl_seconds: int = ACTIVE_TTL_S) -> None:
    ctx.kv.set(_key(duel_id), state, ttl_seconds=ttl_seconds)


def clear(ctx: Context, duel_id: str) -> None:
    ctx.kv.delete(_key(duel_id))


# ── Pointer keys for per-user lookup ────────────────────────────────────────

def set_pending_for(ctx: Context, user_id: str, duel_id: str) -> None:
    ctx.kv.set(f"pending_duel:{user_id}", duel_id, ttl_seconds=PENDING_TTL_S)


def get_pending_for(ctx: Context, user_id: str) -> Optional[str]:
    v = ctx.kv.get(f"pending_duel:{user_id}")
    return str(v) if v else None


def clear_pending_for(ctx: Context, user_id: str) -> None:
    ctx.kv.delete(f"pending_duel:{user_id}")


def set_active_for(ctx: Context, user_id: str, duel_id: str) -> None:
    ctx.kv.set(f"active_duel:{user_id}", duel_id, ttl_seconds=ACTIVE_TTL_S)


def get_active_for(ctx: Context, user_id: str) -> Optional[str]:
    v = ctx.kv.get(f"active_duel:{user_id}")
    return str(v) if v else None


def clear_active_for(ctx: Context, user_id: str) -> None:
    ctx.kv.delete(f"active_duel:{user_id}")
