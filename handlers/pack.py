"""/maid pack — shop for coin-purchased packs.

Flow:
    1. /maid pack            → shop embed with a Buy button per pack
    2. click Buy             → coin balance checked, deducted, pack opened,
                               cards added to SQL inventory

KV profile is the source of truth for coins; SQL inventory is the source
of truth for owned cards.
"""
from __future__ import annotations

from mmo_maid_sdk import ActionRow, Button, Context

from data import packs as packs_data
from engine import drops
from store import kv, sql as store_sql
from ui import embeds


def _shop_components(profile: dict) -> ActionRow:
    coins = int(profile.get("coins", 0))
    buttons = []
    for p in packs_data.ALL:
        affordable = coins >= p.price
        buttons.append(Button(
            f"Buy {p.name}",
            custom_id=f"mm:pack:buy:{p.id}",
            style="success" if affordable else "secondary",
            disabled=not affordable,
        ))
    return ActionRow(*buttons)


def run(ctx: Context, event: dict) -> None:
    user_id = str(event.get("user_id") or "")
    profile = kv.load_profile(ctx, user_id)
    ctx.interaction.respond(
        embeds=[embeds.pack_shop_embed(int(profile.get("coins", 0)))],
        components=[_shop_components(profile)],
        ephemeral=True,
    )


def on_component(ctx: Context, event: dict, tail: list[str]) -> None:
    if len(tail) < 2 or tail[0] != "buy":
        return
    pack_id = tail[1]
    pack = packs_data.BY_ID.get(pack_id)
    if not pack:
        ctx.interaction.respond(content="Unknown pack.", ephemeral=True)
        return

    user_id = str(event.get("user_id") or "")
    if not user_id:
        ctx.interaction.respond(content="Could not identify user.", ephemeral=True)
        return

    # Dedup to prevent double-spend from a fast double-click on the Buy button.
    if not ctx.ephemeral.dedup(f"mm:pack:buy:{user_id}:{pack_id}", ttl_seconds=3):
        return

    profile = kv.load_profile(ctx, user_id)
    coins = int(profile.get("coins", 0))
    if coins < pack.price:
        ctx.interaction.respond(
            content=f"You need {pack.price} coins ({pack.price - coins} more).",
            ephemeral=True,
        )
        return

    profile["coins"] = coins - pack.price
    kv.save_profile(ctx, user_id, profile)

    pulls = drops.roll_pack_with_floor(pack.n_cards, pack.floor)
    for card_type, card_id in pulls:
        store_sql.grant_card(ctx, user_id, card_type, card_id, qty=1)

    ctx.interaction.respond(
        embeds=[embeds.pack_reveal_embed(pack.id, pulls, coins_left=profile["coins"])],
        ephemeral=False,
    )
