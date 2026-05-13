"""Card lookup by user-typed query.

Tries (in order):
    1. exact id match (lowercased, snake-case)
    2. exact case-insensitive name match
    3. case-insensitive substring on name
    4. case-insensitive substring on id

Searches across maids, tools, chaos enemies, and raid bosses. Returns the
first match as a (kind, id) tuple where ``kind`` is one of
``"maid" | "tool" | "chaos" | "raid_boss"``, or None if nothing matches.

Disambiguation: when a query is ambiguous, the first hit in the search
order above wins. We intentionally don't prompt for clarification —
users can refine the query with a longer substring.
"""
from __future__ import annotations

from data import chaos as chaos_data
from data import maids as maids_data
from data import raid_bosses as raid_bosses_data
from data import tools as tools_data


def _normalize(s: str) -> str:
    return "".join(ch for ch in s.lower().strip() if not ch.isspace())


def lookup(query: str) -> tuple[str, str] | None:
    """Return ``(kind, card_id)`` for the best match, or None."""
    if not query:
        return None
    raw = query.strip()
    lower = raw.lower()
    snake = _normalize(raw).replace("-", "_").replace(",", "").replace("'", "")

    pools: list[tuple[str, dict]] = [
        ("maid",      maids_data.BY_ID),
        ("tool",      tools_data.BY_ID),
        ("chaos",     chaos_data.BY_ID),
        ("raid_boss", raid_bosses_data.BY_ID),
    ]

    # 1. exact id match
    for kind, by_id in pools:
        if snake in by_id:
            return (kind, snake)

    # 2. exact case-insensitive name match
    for kind, by_id in pools:
        for cid, card in by_id.items():
            if card.name.lower() == lower:
                return (kind, cid)

    # 3. substring on name
    for kind, by_id in pools:
        for cid, card in by_id.items():
            if lower in card.name.lower():
                return (kind, cid)

    # 4. substring on id
    for kind, by_id in pools:
        for cid in by_id.keys():
            if snake and snake in cid:
                return (kind, cid)

    return None
