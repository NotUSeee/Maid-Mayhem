"""Shared per-server state for player-to-player trades.

Structure (single KV key ``trade:{trade_id}``)::

    {
      "trade_id":   "abcdef",
      "channel_id": "...",
      "status":     "pending" | "active" | "completed" | "cancelled",
      "a":          {"user_id": "...", "user_name": "...",
                     "offer": [(card_type, card_id), ...],
                     "locked": False},
      "b":          {... same shape ...},
      "started_at": ISO timestamp,
    }

Plus per-user pointer keys so a click can look up the trade by user id:

    pending_trade:{user_id} -> trade_id  (TTL = pending phase, ~120s)
    active_trade:{user_id}  -> trade_id  (TTL = active phase, ~10 min)

Cards offered are tracked as (card_type, card_id) pairs. Each entry
represents one physical copy of that card. To trade 2 of the same card,
add two entries.
"""
from __future__ import annotations

import secrets
from typing import Any, Optional

from mmo_maid_sdk import Context

PENDING_TTL_S = 120
ACTIVE_TTL_S  = 10 * 60

MAX_OFFER_SIZE = 5   # how many physical cards per side


def new_trade_id() -> str:
    return secrets.token_hex(6)


def _key(trade_id: str) -> str:
    return f"trade:{trade_id}"


def load(ctx: Context, trade_id: str) -> Optional[dict[str, Any]]:
    raw = ctx.kv.get(_key(trade_id))
    return raw if isinstance(raw, dict) else None


def save(ctx: Context, trade_id: str, state: dict[str, Any],
         *, ttl_seconds: int = ACTIVE_TTL_S) -> None:
    ctx.kv.set(_key(trade_id), state, ttl_seconds=ttl_seconds)


def clear(ctx: Context, trade_id: str) -> None:
    ctx.kv.delete(_key(trade_id))


def set_pending_for(ctx: Context, user_id: str, trade_id: str) -> None:
    ctx.kv.set(f"pending_trade:{user_id}", trade_id, ttl_seconds=PENDING_TTL_S)


def get_pending_for(ctx: Context, user_id: str) -> Optional[str]:
    v = ctx.kv.get(f"pending_trade:{user_id}")
    return str(v) if v else None


def clear_pending_for(ctx: Context, user_id: str) -> None:
    ctx.kv.delete(f"pending_trade:{user_id}")


def set_active_for(ctx: Context, user_id: str, trade_id: str) -> None:
    ctx.kv.set(f"active_trade:{user_id}", trade_id, ttl_seconds=ACTIVE_TTL_S)


def get_active_for(ctx: Context, user_id: str) -> Optional[str]:
    v = ctx.kv.get(f"active_trade:{user_id}")
    return str(v) if v else None


def clear_active_for(ctx: Context, user_id: str) -> None:
    ctx.kv.delete(f"active_trade:{user_id}")
