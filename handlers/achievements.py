"""/maid achievements — view unlock progress + lifetime milestones."""
from __future__ import annotations

from mmo_maid_sdk import Context

from engine import achievements as ach_engine
from ui import embeds


def run(ctx: Context, event: dict) -> None:
    user_id = str(event.get("user_id") or "")
    if not user_id:
        ctx.interaction.respond(content="Could not identify user.", ephemeral=True)
        return
    state = ach_engine.load(ctx, user_id)
    ctx.interaction.respond(embeds=[embeds.achievements_embed(state)], ephemeral=True)
