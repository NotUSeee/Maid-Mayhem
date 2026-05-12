"""/maid battle — PvE turn-based combat.

Whole-team turns: every round the player picks Attack / Defend / Flee.
All living maids act, then all living enemies counter. Element triangle +
random variance create the swing. Battle state is stored ephemerally per
user; abandoned battles auto-expire after 30 minutes.
"""
from __future__ import annotations

from typing import Any

from mmo_maid_sdk import ActionRow, Button, Context

from engine import battle as battle_engine
from store import battle_state, kv, sql as store_sql
from ui import embeds


def _action_row(state: dict[str, Any]) -> ActionRow:
    """Three-button row for the player's options."""
    disabled = state.get("result") is not None
    return ActionRow(
        Button("⚔ Attack", custom_id="mm:battle:attack",
               style="danger", disabled=disabled),
        Button("🛡 Defend", custom_id="mm:battle:defend",
               style="primary", disabled=disabled),
        Button("🏃 Flee",   custom_id="mm:battle:flee",
               style="secondary", disabled=disabled),
    )


def _finalize_if_terminal(ctx: Context, state: dict[str, Any]) -> dict[str, Any] | None:
    """If state is terminal, write rewards + return the result embed dict.
    Returns None if the battle is still in progress."""
    result = state.get("result")
    if not result:
        return None
    user_id = str(state.get("user_id") or "")
    rewards = state.get("rewards") or {"coins": 0, "xp": 0}
    coins = int(rewards.get("coins", 0))
    xp = int(rewards.get("xp", 0))
    won = (result == "win")
    if user_id:
        kv.add_rewards(ctx, user_id, coins=coins, xp=xp, won=won)
        store_sql.record_battle(
            ctx, user_id, result=result, coins=coins, xp=xp,
        )
        battle_state.clear(ctx, user_id)
    return embeds.battle_result_embed(state, won=won, coins=coins, xp=xp)


def run(ctx: Context, event: dict) -> None:
    """Start a new battle (or resume if one is already in flight)."""
    user_id = str(event.get("user_id") or "")
    if not user_id:
        ctx.interaction.respond(content="Could not identify user.", ephemeral=True)
        return

    deck = kv.load_deck(ctx, user_id)
    if not [c for c in (deck.get("maids") or []) if c]:
        ctx.interaction.respond(
            content="Your deck is empty. Build one with `/maid deck` first.",
            ephemeral=True,
        )
        return

    # Resume if a battle is still in flight
    existing = battle_state.load(ctx, user_id)
    if existing and not existing.get("result"):
        ctx.interaction.respond(
            content="Resuming your battle in progress.",
            embeds=[embeds.battle_embed(existing)],
            components=[_action_row(existing)],
            ephemeral=True,
        )
        return

    state = battle_engine.start_battle(user_id, deck)
    if state.get("result") == "no_deck":
        ctx.interaction.respond(
            content="Your deck has no maids. Set one with `/maid deck`.",
            ephemeral=True,
        )
        return

    battle_state.save(ctx, user_id, state)
    ctx.interaction.respond(
        embeds=[embeds.battle_embed(state)],
        components=[_action_row(state)],
        ephemeral=True,
    )


def on_component(ctx: Context, event: dict, tail: list[str]) -> None:
    if not tail:
        return
    action = tail[0]
    if action not in ("attack", "defend", "flee"):
        return
    user_id = str(event.get("user_id") or "")
    state = battle_state.load(ctx, user_id)
    if not state or state.get("result"):
        ctx.interaction.respond(
            content="No battle in progress. Start one with `/maid battle`.",
            ephemeral=True,
        )
        return

    # Drop accidental double-clicks within 1.5s
    if not ctx.ephemeral.dedup(f"mm:battle:click:{user_id}:{state['turn']}:{action}",
                                ttl_seconds=2):
        return

    new_state = battle_engine.take_turn(state, action)
    final_embed = _finalize_if_terminal(ctx, new_state)

    if final_embed is not None:
        ctx.interaction.respond(
            embeds=[embeds.battle_embed(new_state), final_embed],
            components=[],
            ephemeral=True,
        )
        return

    battle_state.save(ctx, user_id, new_state)
    ctx.interaction.respond(
        embeds=[embeds.battle_embed(new_state)],
        components=[_action_row(new_state)],
        ephemeral=True,
    )
