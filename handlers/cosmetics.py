"""/maid cosmetics — view, buy, and equip cosmetics with Polish.

Three slots: title, badge, color. Each slot has 4-6 cosmetics. Bought
with Polish (premium currency) — no coin alternative, so cosmetics are
genuinely rare. Polish is earned slowly (see data/cosmetics.py docstring).
"""
from __future__ import annotations

from typing import Any

from mmo_maid_sdk import ActionRow, Context, SelectMenu, SelectOption

from data import cosmetics as cosmetics_data
from store import kv
from ui import embeds


def _shop_picker(profile: dict, cosmetics: dict) -> ActionRow | None:
    """SelectMenu of unowned cosmetics the user can afford."""
    polish = int(profile.get("polish", 0))
    owned = set(cosmetics.get("owned") or [])
    options = []
    for c in cosmetics_data.ALL:
        if c.id in owned:
            continue
        if polish < c.polish_cost:
            continue
        options.append(SelectOption(
            f"{c.name} — ✨{c.polish_cost}"[:100],
            f"buy:{c.id}",
            description=f"[{c.slot}] {c.flavor or ''}"[:100],
        ))
    if not options:
        return None
    return ActionRow(SelectMenu(
        "mm:cosmetics:select", options=options[:25],
        placeholder="Buy a cosmetic...",
    ))


def _equip_picker(cosmetics: dict) -> ActionRow | None:
    """SelectMenu of owned cosmetics, with the currently-equipped one marked."""
    owned = list(cosmetics.get("owned") or [])
    if not owned:
        return None
    equipped = cosmetics.get("equipped") or {}
    options = []
    for cid in owned:
        c = cosmetics_data.BY_ID.get(cid)
        if not c:
            continue
        is_equipped = (
            (c.slot == "title" and equipped.get("title") == c.id)
            or (c.slot == "badge" and equipped.get("badge") == c.id)
            or (c.slot == "color" and int(equipped.get("color", 0)) == int(c.value))
        )
        suffix = " [equipped]" if is_equipped else ""
        options.append(SelectOption(
            f"{c.name}{suffix}"[:100],
            f"equip:{c.id}",
            description=f"[{c.slot}]"[:100],
            default=is_equipped,
        ))
    if not options:
        return None
    return ActionRow(SelectMenu(
        "mm:cosmetics:select", options=options[:25],
        placeholder="Equip a cosmetic...",
    ))


def run(ctx: Context, event: dict) -> None:
    user_id = str(event.get("user_id") or "")
    profile = kv.load_profile(ctx, user_id)
    cosmetics = kv.load_cosmetics(ctx, user_id)
    rows = []
    p = _shop_picker(profile, cosmetics)
    if p is not None:
        rows.append(p)
    e = _equip_picker(cosmetics)
    if e is not None:
        rows.append(e)
    ctx.interaction.respond(
        embeds=[embeds.cosmetics_embed(profile, cosmetics)],
        components=rows,
        ephemeral=True,
    )


def on_component(ctx: Context, event: dict, tail: list[str]) -> None:
    if not tail or tail[0] != "select":
        return
    values = event.get("values") or []
    if not values:
        return
    action_payload = str(values[0])
    if ":" not in action_payload:
        return
    action, cid = action_payload.split(":", 1)

    user_id = str(event.get("user_id") or "")
    if not user_id:
        return
    cosmetic = cosmetics_data.BY_ID.get(cid)
    if not cosmetic:
        ctx.interaction.respond(content="Unknown cosmetic.", ephemeral=True)
        return

    if action == "buy":
        _do_buy(ctx, user_id, cosmetic)
        return
    if action == "equip":
        _do_equip(ctx, user_id, cosmetic)
        return


def _do_buy(ctx: Context, user_id: str, cosmetic) -> None:
    # Dedup so a double-click can't double-charge.
    if not ctx.ephemeral.dedup(f"mm:cos:buy:{user_id}:{cosmetic.id}", ttl_seconds=3):
        return

    profile = kv.load_profile(ctx, user_id)
    polish = int(profile.get("polish", 0))
    if polish < cosmetic.polish_cost:
        ctx.interaction.respond(
            content=f"You need ✨{cosmetic.polish_cost} Polish ({cosmetic.polish_cost - polish} more).",
            ephemeral=True,
        )
        return

    cosmetics = kv.load_cosmetics(ctx, user_id)
    if cosmetic.id in (cosmetics.get("owned") or []):
        ctx.interaction.respond(content="You already own that.", ephemeral=True)
        return

    profile["polish"] = polish - cosmetic.polish_cost
    cosmetics["owned"] = list(set((cosmetics.get("owned") or []) + [cosmetic.id]))
    kv.save_profile(ctx, user_id, profile)
    kv.save_cosmetics(ctx, user_id, cosmetics)

    ctx.interaction.respond(
        embeds=[embeds.cosmetic_buy_result_embed(cosmetic, polish_left=profile["polish"])],
        ephemeral=True,
    )


def _do_equip(ctx: Context, user_id: str, cosmetic) -> None:
    cosmetics = kv.load_cosmetics(ctx, user_id)
    if cosmetic.id not in (cosmetics.get("owned") or []):
        ctx.interaction.respond(content="You don't own that yet.", ephemeral=True)
        return
    equipped = cosmetics.get("equipped") or {}
    if cosmetic.slot == "color":
        equipped["color"] = int(cosmetic.value)
    else:
        equipped[cosmetic.slot] = cosmetic.id
    cosmetics["equipped"] = equipped
    kv.save_cosmetics(ctx, user_id, cosmetics)
    profile = kv.load_profile(ctx, user_id)
    rows = []
    p = _shop_picker(profile, cosmetics)
    if p is not None:
        rows.append(p)
    e = _equip_picker(cosmetics)
    if e is not None:
        rows.append(e)
    ctx.interaction.respond(
        embeds=[embeds.cosmetic_equip_result_embed(cosmetic), embeds.cosmetics_embed(profile, cosmetics)],
        components=rows,
        ephemeral=True,
    )
