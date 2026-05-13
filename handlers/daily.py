"""/maid daily — claim a 3-card Dust Pack, 24h cooldown."""
from __future__ import annotations

from mmo_maid_sdk import Context

from engine import achievements as ach_engine
from engine import drops
from engine import manor as manor_engine
from engine import quests as quests_engine
from engine import ranks as ranks_engine
from store import kv, sql as store_sql
from ui import embeds


_DAILY_KEY = "mm:daily"   # ephemeral cooldown key (per user, plugin auto-namespaces)
_DAILY_TTL_S = 22 * 60 * 60   # 22h — slightly under 24h so day-to-day timing isn't punishing
_DAILY_PACK_BASE = 3


def run(ctx: Context, event: dict) -> None:
    user_id = str(event.get("user_id") or "")
    if not user_id:
        ctx.interaction.respond(content="Could not identify user.", ephemeral=True)
        return

    cd = ctx.ephemeral.cooldown_check(f"{_DAILY_KEY}:{user_id}")
    if cd.get("active"):
        remaining = int(cd.get("remaining_seconds", 0))
        hrs, mins = divmod(remaining // 60, 60)
        ctx.interaction.respond(
            content=f"Your maids are still resting. Come back in **{hrs}h {mins}m**.",
            ephemeral=True,
        )
        return

    pack_size = manor_engine.daily_pack_size_for_user(ctx, user_id, _DAILY_PACK_BASE)
    pack = drops.roll_pack(pack_size)
    for card_type, card_id in pack:
        store_sql.grant_card(ctx, user_id, card_type, card_id, qty=1)

    # Garden bonus: each level trims 10 min off the cooldown, min 1 minute.
    cooldown_s = manor_engine.daily_cooldown_for_user(ctx, user_id, _DAILY_TTL_S)
    ctx.ephemeral.cooldown_set(f"{_DAILY_KEY}:{user_id}", ttl_seconds=cooldown_s)

    # Award rank points and a sliver of Polish for showing up.
    ranks_engine.award_rp(ctx, user_id, 5)
    kv.add_polish(ctx, user_id, 1)

    # /maid daily counts as a pack-open for quest purposes.
    quests_engine.bump(ctx, user_id, "pack_open")

    # Achievements: daily_claim (Foundation: First Steps)
    newly = ach_engine.bump(ctx, user_id, "daily_claim")
    _maybe_announce_collection(ctx, user_id)

    embed = embeds.daily_pack_embed(pack)
    out_embeds = [embed]
    if newly:
        out_embeds.append(embeds.achievement_unlock_embed(newly))
    ctx.interaction.respond(embeds=out_embeds, ephemeral=False)


def _maybe_announce_collection(ctx, user_id: str) -> list[str]:
    """Recount the user's unique-card total and update the collection
    achievements. Cheap COUNT(DISTINCT) query; runs after every grant.
    Returns any newly-unlocked IDs (caller decides whether to surface them).
    """
    try:
        row = ctx.sql.query_one(
            "SELECT COUNT(*) AS n FROM mm_inventory WHERE user_id=%s AND count > 0",
            [user_id],
        )
        n = int((row or {}).get("n", 0))
    except Exception:
        return []
    return ach_engine.set_counter(ctx, user_id, "unique_owned", n)
