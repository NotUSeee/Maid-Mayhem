"""/maid deck — view and edit your battle deck.

Edit flow:
    1. /maid deck → embed + SelectMenu of 6 slots.
    2. Pick a slot → SelectMenu of owned cards of the right type.
    3. Pick a card → slot is saved, embed re-renders.
"""
from __future__ import annotations

from mmo_maid_sdk import ActionRow, Context, SelectMenu, SelectOption

from data import maids as maids_data
from data import rarities as rarities_data
from data import tools as tools_data
from store import kv, sql as store_sql
from ui import embeds


def _slot_picker_row(deck: dict[str, list[str]]) -> ActionRow:
    options = []
    maids = (deck.get("maids") or []) + [""] * 3
    tools = (deck.get("tools") or []) + [""] * 3
    for i in range(3):
        cid = maids[i]
        label = f"Maid slot {i + 1}"
        desc = "(empty)" if not cid else (maids_data.BY_ID.get(cid).name if maids_data.BY_ID.get(cid) else cid)
        options.append(SelectOption(label, f"maid:{i}", description=desc[:100]))
    for i in range(3):
        cid = tools[i]
        label = f"Tool slot {i + 1}"
        desc = "(empty)" if not cid else (tools_data.BY_ID.get(cid).name if tools_data.BY_ID.get(cid) else cid)
        options.append(SelectOption(label, f"tool:{i}", description=desc[:100]))
    return ActionRow(SelectMenu(
        "mm:deck:choose_slot",
        options=options,
        placeholder="Edit a slot...",
    ))


def _card_picker_row(ctx: Context, user_id: str, slot_kind: str, slot_idx: int) -> ActionRow | None:
    """SelectMenu of cards the user owns matching the slot type."""
    rows = store_sql.get_inventory(ctx, user_id)
    wanted_type = "maid" if slot_kind == "maid" else "tool"
    candidates = [r for r in rows if r.get("card_type") == wanted_type and int(r.get("count", 0)) > 0]
    if not candidates:
        return None
    options = []
    for r in candidates[:25]:  # Discord max 25 options
        cid = r.get("card_id", "")
        if wanted_type == "maid":
            m = maids_data.BY_ID.get(cid)
            if not m:
                continue
            rarity = rarities_data.BY_ID.get(m.rarity)
            tag = rarity.emoji if rarity else ""
            options.append(SelectOption(f"{tag} {m.name}"[:100], cid, description=m.role[:100]))
        else:
            t = tools_data.BY_ID.get(cid)
            if not t:
                continue
            rarity = rarities_data.BY_ID.get(t.rarity)
            tag = rarity.emoji if rarity else ""
            options.append(SelectOption(f"{tag} {t.name}"[:100], cid, description=t.description[:100]))
    if not options:
        return None
    custom_id = f"mm:deck:pick:{slot_kind}:{slot_idx}"
    placeholder = f"Pick a {wanted_type} for slot {slot_idx + 1}..."
    return ActionRow(SelectMenu(custom_id, options=options, placeholder=placeholder))


def run(ctx: Context, event: dict) -> None:
    user_id = str(event.get("user_id") or "")
    deck = kv.load_deck(ctx, user_id)
    ctx.interaction.respond(
        embeds=[embeds.deck_embed(deck)],
        components=[_slot_picker_row(deck)],
        ephemeral=True,
    )


def on_component(ctx: Context, event: dict, tail: list[str]) -> None:
    user_id = str(event.get("user_id") or "")
    if not tail:
        return

    action = tail[0]
    values = event.get("values") or []

    if action == "choose_slot":
        if not values:
            return
        try:
            slot_kind, slot_idx_str = str(values[0]).split(":", 1)
            slot_idx = int(slot_idx_str)
        except (ValueError, IndexError):
            return
        picker = _card_picker_row(ctx, user_id, slot_kind, slot_idx)
        if picker is None:
            ctx.interaction.respond(
                content=f"You don't own any {slot_kind} cards yet. Try `/maid daily`.",
                ephemeral=True,
            )
            return
        ctx.interaction.respond(
            content=f"Pick a {slot_kind} for slot {slot_idx + 1}:",
            components=[picker],
            ephemeral=True,
        )
        return

    if action == "pick":
        if len(tail) < 3 or not values:
            return
        slot_kind = tail[1]
        try:
            slot_idx = int(tail[2])
        except ValueError:
            return
        card_id = str(values[0])
        # Defensive: confirm ownership (in case inventory changed between menus)
        if not store_sql.owns_card(ctx, user_id, slot_kind, card_id):
            ctx.interaction.respond(
                content="You no longer own that card.", ephemeral=True,
            )
            return
        deck = kv.set_deck_slot(ctx, user_id, slot_kind + "s", slot_idx, card_id)
        ctx.interaction.respond(
            embeds=[embeds.deck_embed(deck)],
            components=[_slot_picker_row(deck)],
            ephemeral=True,
        )
        return
