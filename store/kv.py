"""Typed KV wrappers for profile + deck.

KV is per-server (host namespaces by discord_srv_id + plugin_id), so user
ID alone is enough as the key suffix.
"""
from __future__ import annotations

from typing import Any

from mmo_maid_sdk import Context


# ── Profile ─────────────────────────────────────────────────────────────────

DEFAULT_PROFILE: dict[str, Any] = {
    "coins": 0,
    "xp": 0,
    "level": 1,
    "wins": 0,
    "losses": 0,
    "prestige": 0,
    "polish": 0,
}


def _profile_key(user_id: str) -> str:
    return f"profile:{user_id}"


def load_profile(ctx: Context, user_id: str) -> dict[str, Any]:
    raw = ctx.kv.get(_profile_key(user_id))
    if not isinstance(raw, dict):
        return dict(DEFAULT_PROFILE)
    return {**DEFAULT_PROFILE, **raw}


def save_profile(ctx: Context, user_id: str, profile: dict[str, Any]) -> None:
    ctx.kv.set(_profile_key(user_id), profile)


def add_rewards(ctx: Context, user_id: str, *, coins: int, xp: int, won: bool) -> dict[str, Any]:
    """Atomic-ish update of profile after a battle. Returns the new profile."""
    p = load_profile(ctx, user_id)
    p["coins"] = int(p.get("coins", 0)) + int(coins)
    p["xp"]    = int(p.get("xp", 0)) + int(xp)
    if won:
        p["wins"] = int(p.get("wins", 0)) + 1
    else:
        p["losses"] = int(p.get("losses", 0)) + 1
    p["level"] = level_for_xp(p["xp"])
    save_profile(ctx, user_id, p)
    return p


def level_for_xp(xp: int) -> int:
    """Simple curve: level N requires 50 * N * (N-1) total XP (quadratic).
    Level 1 = 0 xp, 2 = 100, 3 = 300, 4 = 600, ... 10 = 4500, 20 = 19000.
    """
    n = 1
    while 50 * (n + 1) * n <= int(xp):
        n += 1
        if n > 50:
            return 50
    return n


# ── Deck ────────────────────────────────────────────────────────────────────

DECK_MAID_SLOTS = 3
DECK_TOOL_SLOTS = 3


def _deck_key(user_id: str) -> str:
    return f"deck:{user_id}"


def load_deck(ctx: Context, user_id: str) -> dict[str, list[str]]:
    raw = ctx.kv.get(_deck_key(user_id))
    if not isinstance(raw, dict):
        return {"maids": [], "tools": []}
    return {
        "maids": list(raw.get("maids") or [])[:DECK_MAID_SLOTS],
        "tools": list(raw.get("tools") or [])[:DECK_TOOL_SLOTS],
    }


def save_deck(ctx: Context, user_id: str, deck: dict[str, list[str]]) -> None:
    safe = {
        "maids": list(deck.get("maids") or [])[:DECK_MAID_SLOTS],
        "tools": list(deck.get("tools") or [])[:DECK_TOOL_SLOTS],
    }
    ctx.kv.set(_deck_key(user_id), safe)


def set_deck_slot(ctx: Context, user_id: str, slot_kind: str, slot_idx: int, card_id: str) -> dict[str, list[str]]:
    """Place `card_id` at the given slot. Pads list to length if needed."""
    deck = load_deck(ctx, user_id)
    cap = DECK_MAID_SLOTS if slot_kind == "maids" else DECK_TOOL_SLOTS
    slots = list(deck.get(slot_kind) or [])
    while len(slots) <= slot_idx:
        slots.append("")
    if slot_idx >= cap:
        return deck
    slots[slot_idx] = card_id
    deck[slot_kind] = slots[:cap]
    save_deck(ctx, user_id, deck)
    return deck


# ── Manor ───────────────────────────────────────────────────────────────────

def _manor_key(user_id: str) -> str:
    return f"manor:{user_id}"


def load_manor(ctx: Context, user_id: str) -> dict[str, int]:
    """Return {room_id: level}. Missing entries default to level 1."""
    # Imported lazily so data/rooms doesn't have to be on import path during
    # tests that only touch unrelated KV helpers.
    from data import rooms as rooms_data
    raw = ctx.kv.get(_manor_key(user_id))
    if not isinstance(raw, dict):
        raw = {}
    out = {}
    for room in rooms_data.ALL:
        lvl = int(raw.get(room.id, 1))
        out[room.id] = max(1, min(rooms_data.MAX_LEVEL, lvl))
    return out


def save_manor(ctx: Context, user_id: str, manor: dict[str, int]) -> None:
    from data import rooms as rooms_data
    safe = {}
    for room in rooms_data.ALL:
        lvl = int(manor.get(room.id, 1))
        safe[room.id] = max(1, min(rooms_data.MAX_LEVEL, lvl))
    ctx.kv.set(_manor_key(user_id), safe)


def manor_room_level(ctx: Context, user_id: str, room_id: str) -> int:
    return int(load_manor(ctx, user_id).get(room_id, 1))


def add_polish(ctx: Context, user_id: str, amount: int) -> int:
    """Atomic-ish polish credit. Returns the new balance."""
    p = load_profile(ctx, user_id)
    p["polish"] = max(0, int(p.get("polish", 0)) + int(amount))
    save_profile(ctx, user_id, p)
    return int(p["polish"])


# ── Cosmetics ───────────────────────────────────────────────────────────────

DEFAULT_COSMETICS: dict[str, Any] = {
    "owned": [],                      # list of cosmetic_id
    "equipped": {"title": "", "badge": "", "color": 0},
}


def _cosmetics_key(user_id: str) -> str:
    return f"cosmetics:{user_id}"


def load_cosmetics(ctx: Context, user_id: str) -> dict[str, Any]:
    raw = ctx.kv.get(_cosmetics_key(user_id))
    if not isinstance(raw, dict):
        return {"owned": [], "equipped": {**DEFAULT_COSMETICS["equipped"]}}
    return {
        "owned": list(raw.get("owned") or []),
        "equipped": {
            "title": str((raw.get("equipped") or {}).get("title", "")),
            "badge": str((raw.get("equipped") or {}).get("badge", "")),
            "color": int((raw.get("equipped") or {}).get("color", 0) or 0),
        },
    }


def save_cosmetics(ctx: Context, user_id: str, cosmetics: dict[str, Any]) -> None:
    ctx.kv.set(_cosmetics_key(user_id), {
        "owned": list(cosmetics.get("owned") or []),
        "equipped": cosmetics.get("equipped") or {},
    })
