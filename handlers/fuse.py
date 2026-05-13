"""/maid fuse — combine duplicate cards into the next rarity tier.

Flow:
    1. /maid fuse            → tier menu + SelectMenu (fusable tiers only)
    2. pick a tier           → confirm embed (lists what'll be consumed)
                               with [Confirm] [Cancel] buttons
    3. click Confirm         → consume cards, grant 1 random card of the
                               next tier, show reveal embed

The plan is not encoded in the confirm button's custom_id — we re-plan
at confirm time from fresh inventory. The plan algorithm is deterministic
(greedy from highest count), so the user sees the same result they saw
on the confirm screen unless their inventory changed in between (rare,
but the re-plan guards against it gracefully).
"""
from __future__ import annotations

from mmo_maid_sdk import ActionRow, Button, Context, SelectMenu, SelectOption

from data import fusion as fusion_data
from data import maids as maids_data
from data import rarities as rarities_data
from engine import achievements as ach_engine
from engine import fusion as fusion_engine
from engine import quests as quests_engine
from store import sql as store_sql
from ui import embeds


def _totals_by_rarity(rows: list[dict]) -> dict[str, int]:
    """Sum owned card counts grouped by rarity (across maid + tool)."""
    out: dict[str, int] = {}
    for r in rows:
        rarity = fusion_engine._rarity_of(
            str(r.get("card_type", "")), str(r.get("card_id", ""))
        )
        if not rarity:
            continue
        out[rarity] = out.get(rarity, 0) + int(r.get("count", 0))
    return out


def _tier_picker(totals: dict[str, int]) -> ActionRow | None:
    """SelectMenu of tiers the user has enough cards to fuse."""
    options = []
    for rcp in fusion_data.RECIPES:
        have = int(totals.get(rcp.from_rarity, 0))
        if have < rcp.cost:
            continue
        from_r = rarities_data.BY_ID.get(rcp.from_rarity)
        to_r   = rarities_data.BY_ID.get(rcp.to_rarity)
        label = f"{rcp.cost}× {from_r.label if from_r else rcp.from_rarity} → 1× {to_r.label if to_r else rcp.to_rarity}"
        options.append(SelectOption(
            label[:100],
            rcp.from_rarity,
            description=f"You have {have}"[:100],
            emoji=(from_r.emoji if from_r else None),
        ))
    if not options:
        return None
    return ActionRow(SelectMenu(
        "mm:fuse:pick", options=options, placeholder="Pick a tier to fuse...",
    ))


def run(ctx: Context, event: dict) -> None:
    user_id = str(event.get("user_id") or "")
    rows = store_sql.get_inventory(ctx, user_id)
    totals = _totals_by_rarity(rows)
    picker = _tier_picker(totals)
    if picker is None:
        ctx.interaction.respond(
            content="You don't have enough duplicates to fuse yet. Try `/maid daily` or `/maid pack` first.",
            ephemeral=True,
        )
        return
    ctx.interaction.respond(
        embeds=[embeds.fusion_menu_embed(totals)],
        components=[picker],
        ephemeral=True,
    )


def on_component(ctx: Context, event: dict, tail: list[str]) -> None:
    if not tail:
        return
    user_id = str(event.get("user_id") or "")
    if not user_id:
        return

    action = tail[0]

    if action == "pick":
        # SelectMenu fired — value is the from_rarity id
        values = event.get("values") or []
        if not values:
            return
        from_rarity = str(values[0])
        recipe = fusion_data.BY_FROM.get(from_rarity)
        if not recipe:
            ctx.interaction.respond(content="Unknown tier.", ephemeral=True)
            return
        rows = store_sql.get_inventory(ctx, user_id)
        plan = fusion_engine.plan_consumption(rows, from_rarity, recipe.cost)
        if not plan:
            ctx.interaction.respond(
                content=f"You no longer have {recipe.cost} {from_rarity} cards.",
                ephemeral=True,
            )
            return
        ctx.interaction.respond(
            embeds=[embeds.fusion_confirm_embed(
                recipe.from_rarity, recipe.to_rarity, recipe.cost, plan,
            )],
            components=[ActionRow(
                Button("Fuse", custom_id=f"mm:fuse:confirm:{from_rarity}", style="success"),
                Button("Cancel", custom_id="mm:fuse:cancel", style="secondary"),
            )],
            ephemeral=True,
        )
        return

    if action == "cancel":
        ctx.interaction.respond(content="Cancelled.", ephemeral=True)
        return

    if action == "confirm":
        if len(tail) < 2:
            return
        from_rarity = tail[1]
        recipe = fusion_data.BY_FROM.get(from_rarity)
        if not recipe:
            ctx.interaction.respond(content="Unknown tier.", ephemeral=True)
            return

        # Dedup so frantic double-clicks don't fuse twice.
        if not ctx.ephemeral.dedup(
            f"mm:fuse:do:{user_id}:{from_rarity}", ttl_seconds=3,
        ):
            return

        rows = store_sql.get_inventory(ctx, user_id)
        plan = fusion_engine.plan_consumption(rows, from_rarity, recipe.cost)
        if not plan:
            ctx.interaction.respond(
                content=f"You no longer have enough {from_rarity} cards.",
                ephemeral=True,
            )
            return

        for card_type, card_id, qty in plan:
            store_sql.consume_card(ctx, user_id, card_type, card_id, qty)

        result_type, result_id = fusion_engine.roll_output(recipe.to_rarity)
        store_sql.grant_card(ctx, user_id, result_type, result_id, qty=1)

        quests_engine.bump(ctx, user_id, "card_fuse")

        unlocks = list(ach_engine.bump(ctx, user_id, "card_fuse"))
        if result_type == "maid":
            m = maids_data.BY_ID.get(result_id)
            if m and m.rarity == "mythic":
                unlocks.extend(ach_engine.bump(ctx, user_id, "mythic_owned"))
        unlocks.extend(_recount_unique(ctx, user_id))

        out = [embeds.fusion_result_embed(plan, result_type, result_id)]
        if unlocks:
            out.append(embeds.achievement_unlock_embed(unlocks))
        ctx.interaction.respond(embeds=out, ephemeral=False)
        return


def _recount_unique(ctx, user_id: str) -> list[str]:
    try:
        row = ctx.sql.query_one(
            "SELECT COUNT(*) AS n FROM mm_inventory WHERE user_id=%s AND count > 0",
            [user_id],
        )
        n = int((row or {}).get("n", 0))
    except Exception:
        return []
    return ach_engine.set_counter(ctx, user_id, "unique_owned", n)
