"""/maid cards — paginated collection viewer."""
from __future__ import annotations

from mmo_maid_sdk import ActionRow, Button, Context

from store import sql as store_sql
from ui import embeds


PAGE_SIZE = 8


def _render(ctx: Context, user_id: str, page: int) -> tuple[dict, list]:
    rows = store_sql.get_inventory(ctx, user_id)
    total = len(rows)
    if total == 0:
        embed = embeds.collection_embed([], page=0, page_size=PAGE_SIZE, total=0)
        return embed, []
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(0, min(page, total_pages - 1))
    start = page * PAGE_SIZE
    view = rows[start:start + PAGE_SIZE]
    embed = embeds.collection_embed(view, page=page, page_size=PAGE_SIZE, total=total)
    row = ActionRow(
        Button("◀ Prev", custom_id=f"mm:cards:page:{page - 1}",
               style="secondary", disabled=(page <= 0)),
        Button("Next ▶", custom_id=f"mm:cards:page:{page + 1}",
               style="secondary", disabled=(page >= total_pages - 1)),
    )
    return embed, [row]


def run(ctx: Context, event: dict) -> None:
    user_id = str(event.get("user_id") or "")
    embed, components = _render(ctx, user_id, page=0)
    ctx.interaction.respond(embeds=[embed], components=components, ephemeral=True)


def on_component(ctx: Context, event: dict, tail: list[str]) -> None:
    if not tail or tail[0] != "page":
        return
    try:
        page = int(tail[1])
    except (IndexError, ValueError):
        page = 0
    user_id = str(event.get("user_id") or "")
    embed, components = _render(ctx, user_id, page=page)
    ctx.interaction.respond(embeds=[embed], components=components, ephemeral=True)
