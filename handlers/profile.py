"""/maid profile — show coins, xp, level, win/loss record."""
from __future__ import annotations

from mmo_maid_sdk import Context

from store import kv
from ui import embeds


def run(ctx: Context, event: dict) -> None:
    user_id = str(event.get("user_id") or "")
    name = event.get("user_name") or "Maid"
    profile = kv.load_profile(ctx, user_id)
    embed = embeds.profile_embed(profile, display_name=name)
    ctx.interaction.respond(embeds=[embed], ephemeral=True)
