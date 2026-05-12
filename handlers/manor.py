"""/maid manor — view rooms and upgrade them with coins.

The room SelectMenu lists every non-maxed room with its next-level cost.
Picking one upgrades by 1 level (cost deducted from KV profile coins).
KV is the source of truth for both manor state and coins.
"""
from __future__ import annotations

from mmo_maid_sdk import ActionRow, Context, SelectMenu, SelectOption

from data import rooms as rooms_data
from store import kv
from ui import embeds


def _room_picker(manor: dict[str, int], coins: int) -> ActionRow | None:
    """SelectMenu of rooms that are upgradable AND affordable."""
    options = []
    for room in rooms_data.ALL:
        lvl = int(manor.get(room.id, 1))
        if lvl >= rooms_data.MAX_LEVEL:
            continue
        cost = rooms_data.upgrade_cost(lvl)
        if coins < cost:
            continue
        options.append(SelectOption(
            f"{room.name} L{lvl} → L{lvl + 1}"[:100],
            room.id,
            description=f"Cost: {cost} coins"[:100],
            emoji=room.emoji,
        ))
    if not options:
        return None
    return ActionRow(SelectMenu(
        "mm:manor:upgrade", options=options, placeholder="Upgrade a room...",
    ))


def run(ctx: Context, event: dict) -> None:
    user_id = str(event.get("user_id") or "")
    if not user_id:
        ctx.interaction.respond(content="Could not identify user.", ephemeral=True)
        return

    manor = kv.load_manor(ctx, user_id)
    profile = kv.load_profile(ctx, user_id)
    coins = int(profile.get("coins", 0))
    picker = _room_picker(manor, coins)
    components = [picker] if picker is not None else []
    ctx.interaction.respond(
        embeds=[embeds.manor_embed(manor, coins)],
        components=components,
        ephemeral=True,
    )


def on_component(ctx: Context, event: dict, tail: list[str]) -> None:
    if not tail or tail[0] != "upgrade":
        return
    user_id = str(event.get("user_id") or "")
    if not user_id:
        return

    values = event.get("values") or []
    if not values:
        return
    room_id = str(values[0])
    room = rooms_data.BY_ID.get(room_id)
    if not room:
        ctx.interaction.respond(content="Unknown room.", ephemeral=True)
        return

    # Dedup so a frantic double-click doesn't double-charge.
    if not ctx.ephemeral.dedup(f"mm:manor:up:{user_id}:{room_id}", ttl_seconds=3):
        return

    manor = kv.load_manor(ctx, user_id)
    current = int(manor.get(room_id, 1))
    if current >= rooms_data.MAX_LEVEL:
        ctx.interaction.respond(content=f"{room.name} is already maxed.", ephemeral=True)
        return

    cost = rooms_data.upgrade_cost(current)
    profile = kv.load_profile(ctx, user_id)
    coins = int(profile.get("coins", 0))
    if coins < cost:
        ctx.interaction.respond(
            content=f"Need {cost} coins for {room.name} L{current + 1}; you have {coins}.",
            ephemeral=True,
        )
        return

    profile["coins"] = coins - cost
    manor[room_id] = current + 1
    kv.save_profile(ctx, user_id, profile)
    kv.save_manor(ctx, user_id, manor)

    ctx.interaction.respond(
        embeds=[
            embeds.manor_upgrade_result_embed(
                room_id, from_level=current, to_level=current + 1,
                coins_left=profile["coins"],
            ),
            embeds.manor_embed(manor, profile["coins"]),
        ],
        components=[picker] if (picker := _room_picker(manor, profile["coins"])) is not None else [],
        ephemeral=True,
    )
