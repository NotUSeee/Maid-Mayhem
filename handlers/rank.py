"""/maid rank — current rank, RP, and season info."""
from __future__ import annotations

from mmo_maid_sdk import Context

from engine import ranks as ranks_engine
from ui import embeds


def run(ctx: Context, event: dict) -> None:
    user_id = str(event.get("user_id") or "")
    name = event.get("user_name") or "Maid"
    # Trigger any pending season rollover before reading state.
    ranks_engine.ensure_season_current(ctx, user_id)
    state = ranks_engine.load_state(ctx, user_id)
    ctx.interaction.respond(embeds=[embeds.rank_embed(state, display_name=name)], ephemeral=True)
