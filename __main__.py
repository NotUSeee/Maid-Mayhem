"""
Maid & Mayhem — Discord card game plugin for the MMO Maid platform.

Entry point. Defines the single Plugin() singleton, the top-level `/maid`
command dispatcher, and the on_install hook that runs schema DDL.

All real subcommand logic lives in handlers/*.py. Battle-button routing
lives in handlers/battle.py (registered through @plugin.on_component here
because the SDK requires decorators on the singleton).
"""
from __future__ import annotations

from mmo_maid_sdk import Plugin, Context

from handlers import daily, cards, deck, battle, duel, fuse, manor, pack, profile, rank, leaderboard
from engine import ranks as ranks_engine
from store import sql as store_sql
from ui import embeds as ui_embeds

plugin = Plugin()


SUBCOMMANDS = {
    "daily":       daily.run,
    "cards":       cards.run,
    "deck":        deck.run,
    "battle":      battle.run,
    "duel":        duel.run,
    "pack":        pack.run,
    "fuse":        fuse.run,
    "manor":       manor.run,
    "rank":        rank.run,
    "profile":     profile.run,
    "leaderboard": leaderboard.run,
}


@plugin.on_ready
def on_ready(ctx: Context):
    """Boot log.

    NOTE: we do NOT bootstrap the SQL schema here. The on_ready ctx is the
    boot-time context (SDK _plugin.py:363-377 calls fn(self._ctx) directly),
    so ctx.server_id is empty/placeholder — any DDL we ran here would land
    in the wrong sandboxed schema, not the user's real server schema. The
    schema is instead bootstrapped lazily on the first interaction per
    server via store_sql.ensure_schema(ctx) at the top of handle_maid.
    """
    ctx.log("Maid & Mayhem ready — /maid registered.")


@plugin.on_install
def on_install(ctx: Context):
    """Per-server install. The platform doesn't reliably fire this for
    marketplace installs today, but if it does, this runs the schema
    bootstrap with the correct per-server ctx.
    """
    try:
        store_sql.ensure_schema(ctx)
        ctx.log("Maid & Mayhem schema installed via on_install.")
    except Exception as e:
        ctx.log(f"Maid & Mayhem on_install failed: {e!r}", level="error")


@plugin.on_slash_command("maid")
def handle_maid(ctx: Context, event: dict):
    # Lazy schema bootstrap — must run with per-event ctx (real server_id),
    # not the boot-time ctx that on_ready / on_install in non-pool mode use.
    # The KV flag inside ensure_schema is per-server, so DDL fires exactly
    # once per server install across the worker's lifetime.
    try:
        store_sql.ensure_schema(ctx)
    except Exception as e:
        ctx.log(f"ensure_schema failed: {e!r}", level="error")
        ctx.interaction.respond(
            content="The manor is still being set up — try again in a moment.",
            ephemeral=True,
        )
        return

    # Check for a season rollover before any subcommand runs. If we
    # crossed into a new month, deliver the prior season's rewards via an
    # ephemeral announcement, then continue with the user's command.
    user_id = str(event.get("user_id") or "")
    if user_id:
        try:
            rollover = ranks_engine.ensure_season_current(ctx, user_id)
        except Exception as e:
            ctx.log(f"season rollover failed: {e!r}", level="error")
            rollover = None
        if rollover is not None:
            name = event.get("user_name") or "Maid"
            try:
                ctx.interaction.followup(
                    embeds=[ui_embeds.season_rollover_embed(rollover, name)],
                    ephemeral=True,
                )
            except Exception:
                # If followup isn't allowed pre-respond (some interaction
                # states), the next subcommand response will be the user's
                # only message — rewards are still credited.
                pass

    opts = event.get("command_options") or []
    sub = (opts[0].get("name") if opts else "") or ""
    handler = SUBCOMMANDS.get(sub)
    if not handler:
        ctx.interaction.respond(
            content=f"Unknown subcommand `{sub}`. Try /maid profile.",
            ephemeral=True,
        )
        return
    handler(ctx, event)


# ── Component (button / select) routing ─────────────────────────────────────
# We use a single dispatch on a `mm:<area>:<rest>` custom_id prefix so we don't
# have to add a separate @plugin.on_component for every button. The SDK matches
# custom_ids by exact string, so we register one handler per area and parse the
# tail inside.

@plugin.on_event("interaction_create")
def route_components(ctx: Context, event: dict):
    """Catch-all component router. SDK's on_component does exact match only;
    we have many dynamic custom_ids (e.g. mm:battle:attack:2, mm:cards:page:3),
    so we route on prefix from the raw interaction_create event."""
    if event.get("interaction_type") != 3:  # 3 = MESSAGE_COMPONENT
        return
    cid = event.get("custom_id") or ""
    if not cid.startswith("mm:"):
        return
    parts = cid.split(":")
    if len(parts) < 2:
        return
    area = parts[1]
    if area == "battle":
        battle.on_component(ctx, event, parts[2:])
    elif area == "cards":
        cards.on_component(ctx, event, parts[2:])
    elif area == "deck":
        deck.on_component(ctx, event, parts[2:])
    elif area == "pack":
        pack.on_component(ctx, event, parts[2:])
    elif area == "fuse":
        fuse.on_component(ctx, event, parts[2:])
    elif area == "duel":
        duel.on_component(ctx, event, parts[2:])
    elif area == "manor":
        manor.on_component(ctx, event, parts[2:])


if __name__ == "__main__":
    plugin.run()
