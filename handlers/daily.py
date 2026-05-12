"""/maid daily — claim a 3-card Dust Pack, 24h cooldown."""
from __future__ import annotations

from mmo_maid_sdk import Context

from engine import drops
from engine import manor as manor_engine
from store import sql as store_sql
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

    embed = embeds.daily_pack_embed(pack)
    ctx.interaction.respond(embeds=[embed], ephemeral=False)
