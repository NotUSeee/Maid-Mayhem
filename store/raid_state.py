"""Shared per-server raid state.

KV is already per-server, so a single key ``raid:current`` holds the
in-flight boss. The record looks like::

    {
      "boss_id": "great_unwashed_one",
      "hp": 1320,
      "max_hp": 1500,
      "contributors": {"<user_id>": 240, ...},   # total dmg per user
      "started_at": "2026-05-12T14:32:11+00:00",
    }
"""
from __future__ import annotations

from typing import Any, Optional

from mmo_maid_sdk import Context


_KEY = "raid:current"


def load(ctx: Context) -> Optional[dict[str, Any]]:
    raw = ctx.kv.get(_KEY)
    return raw if isinstance(raw, dict) else None


def save(ctx: Context, state: dict[str, Any]) -> None:
    # No TTL — a raid persists until killed (or admin manually clears it).
    ctx.kv.set(_KEY, state)


def clear(ctx: Context) -> None:
    ctx.kv.delete(_KEY)
