"""/maid card <name> — single-card detail view.

Search resolves by id, name, or partial substring (in that order) across
maids, tools, chaos enemies, and raid bosses. If the user owns the card,
the embed includes their owned count and the card's current level.
"""
from __future__ import annotations

from mmo_maid_sdk import Context

from engine import card_lookup
from store import sql as store_sql
from ui import embeds


def _extract_name_option(event: dict) -> str:
    opts = event.get("command_options") or []
    if not opts:
        return ""
    sub = opts[0]
    for o in (sub.get("options") or []):
        if o.get("name") == "name":
            return str(o.get("value") or "")
    return ""


def _owned_and_level(ctx: Context, user_id: str, card_type: str, card_id: str) -> tuple[int, int]:
    """Return (count, level). (0, 1) if the user doesn't own this card."""
    row = ctx.sql.query_one(
        "SELECT count, level FROM mm_inventory WHERE user_id=%s AND card_type=%s AND card_id=%s",
        [user_id, card_type, card_id],
    )
    if not row:
        return (0, 1)
    return (int(row.get("count", 0)), int(row.get("level", 1)))


def run(ctx: Context, event: dict) -> None:
    query = _extract_name_option(event)
    if not query:
        ctx.interaction.respond(
            content="Pass a card name: `/maid card name:<text>`.",
            ephemeral=True,
        )
        return

    hit = card_lookup.lookup(query)
    if hit is None:
        ctx.interaction.respond(
            content=(
                f"No card matches `{query[:60]}`. Try a maid name like "
                f"`Aurelia`, a tool like `Cursed Mop`, or part of either."
            ),
            ephemeral=True,
        )
        return

    kind, cid = hit
    user_id = str(event.get("user_id") or "")

    if kind == "maid":
        owned, level = (0, 1)
        if user_id:
            owned, level = _owned_and_level(ctx, user_id, "maid", cid)
        embed = embeds.maid_card_embed(
            cid,
            owned_count=(owned if owned > 0 else None),
            level=(level if owned > 0 else None),
        )
    elif kind == "tool":
        owned = 0
        if user_id:
            owned, _ = _owned_and_level(ctx, user_id, "tool", cid)
        embed = embeds.tool_card_embed(
            cid, owned_count=(owned if owned > 0 else None),
        )
    elif kind == "chaos":
        embed = embeds.chaos_card_embed(cid)
    elif kind == "raid_boss":
        embed = embeds.raid_boss_card_embed(cid)
    else:
        ctx.interaction.respond(content="Unknown card kind.", ephemeral=True)
        return

    ctx.interaction.respond(embeds=[embed], ephemeral=True)
