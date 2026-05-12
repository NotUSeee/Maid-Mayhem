"""/maid leaderboard — top 25 players by XP.

User names are resolved via ctx.discord.get_member; failures fall back
to the raw user_id. We do not bulk-resolve — 25 lookups per leaderboard
render is cheap and the host pages member fetches anyway.
"""
from __future__ import annotations

from mmo_maid_sdk import Context

from store import sql as store_sql
from ui import embeds


def _resolve_name(ctx: Context, user_id: str) -> str:
    try:
        m = ctx.discord.get_member(user_id=user_id)
    except Exception:
        return user_id
    if not isinstance(m, dict):
        return user_id
    return (
        m.get("display_name")
        or m.get("username")
        or m.get("name")
        or user_id
    )


def run(ctx: Context, event: dict) -> None:
    rows = store_sql.top_players(ctx, limit=25)
    names: dict[str, str] = {}
    for row in rows:
        uid = str(row.get("user_id", ""))
        if uid:
            names[uid] = _resolve_name(ctx, uid)
    ctx.interaction.respond(
        embeds=[embeds.leaderboard_embed(rows, names)],
        ephemeral=False,
    )
