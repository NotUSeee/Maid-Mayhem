"""Discord embed builders.

Each builder returns a list of embed dicts ready for
`ctx.interaction.respond(embeds=...)`.
"""
from __future__ import annotations

from typing import Any

from data import chaos as chaos_data
from data import elements as elements_data
from data import maids as maids_data
from data import packs as packs_data
from data import rarities as rarities_data
from data import tools as tools_data


# ── Profile ─────────────────────────────────────────────────────────────────

def profile_embed(profile: dict[str, Any], display_name: str) -> dict[str, Any]:
    xp = int(profile.get("xp", 0))
    level = int(profile.get("level", 1))
    wins = int(profile.get("wins", 0))
    losses = int(profile.get("losses", 0))
    coins = int(profile.get("coins", 0))
    next_lvl_xp = 50 * (level + 1) * level
    return {
        "title": f"\U0001F9F9 {display_name}'s Maid Manor",
        "color": 0xCA8A04,
        "fields": [
            {"name": "Level",   "value": f"**{level}**  ({xp}/{next_lvl_xp} XP)", "inline": True},
            {"name": "Coins",   "value": f"\U0001FA99 {coins}", "inline": True},
            {"name": "Record",  "value": f"{wins}W / {losses}L", "inline": True},
        ],
        "footer": {"text": "Use /maid daily to claim today's pack."},
    }


# ── Card details ────────────────────────────────────────────────────────────

def maid_card_embed(maid_id: str, *, owned_count: int | None = None, level: int | None = None) -> dict[str, Any]:
    m = maids_data.BY_ID.get(maid_id)
    if not m:
        return {"title": "Unknown maid", "description": f"`{maid_id}`", "color": 0x6B7280}
    r = rarities_data.BY_ID.get(m.rarity)
    e = elements_data.BY_ID.get(m.element)
    title = f"{(r.emoji + ' ') if r else ''}{m.name}"
    subtitle_bits = []
    if r:
        subtitle_bits.append(f"**{r.label}**")
    if e:
        subtitle_bits.append(f"{e.emoji} {e.label}")
    subtitle_bits.append(f"_{m.role}_")
    desc = " · ".join(subtitle_bits)
    fields = [
        {"name": "Clean Power", "value": f"\U0001F9F9 {m.clean_power}", "inline": True},
        {"name": "Poise",       "value": f"\U0001F6E1 {m.poise}",       "inline": True},
        {"name": "Charm",       "value": f"✨ {m.charm}",       "inline": True},
        {"name": "Speed",       "value": f"⚡ {m.speed}",       "inline": True},
        {"name": m.ability_name, "value": m.ability_text, "inline": False},
    ]
    if owned_count is not None:
        owned_str = f"x{owned_count}"
        if level is not None:
            owned_str += f"  · Lv {level}"
        fields.append({"name": "Owned", "value": owned_str, "inline": True})
    return {
        "title": title,
        "description": desc + (f"\n\n_{m.flavor}_" if m.flavor else ""),
        "color": (r.color if r else 0x6B7280),
        "fields": fields,
    }


def tool_card_embed(tool_id: str, *, owned_count: int | None = None) -> dict[str, Any]:
    t = tools_data.BY_ID.get(tool_id)
    if not t:
        return {"title": "Unknown tool", "description": f"`{tool_id}`", "color": 0x6B7280}
    r = rarities_data.BY_ID.get(t.rarity)
    title = f"{(r.emoji + ' ') if r else ''}{t.name}"
    subtitle = f"**{r.label}**  ·  _Tool_" if r else "_Tool_"
    fields = [{"name": "Effect", "value": t.description, "inline": False}]
    if owned_count is not None:
        fields.append({"name": "Owned", "value": f"x{owned_count}", "inline": True})
    return {
        "title": title,
        "description": subtitle + (f"\n\n_{t.flavor}_" if t.flavor else ""),
        "color": (r.color if r else 0x6B7280),
        "fields": fields,
    }


# ── Daily pack reveal ───────────────────────────────────────────────────────

def _pack_lines(drops: list[tuple[str, str]]) -> list[str]:
    lines: list[str] = []
    for card_type, card_id in drops:
        if card_type == "maid":
            m = maids_data.BY_ID.get(card_id)
            if not m:
                continue
            r = rarities_data.BY_ID.get(m.rarity)
            e = elements_data.BY_ID.get(m.element)
            tag = f"{r.emoji} **{r.label}**" if r else ""
            elem = f"{e.emoji}" if e else ""
            lines.append(f"{tag} · {elem} **{m.name}** — _{m.role}_")
        else:
            t = tools_data.BY_ID.get(card_id)
            if not t:
                continue
            r = rarities_data.BY_ID.get(t.rarity)
            tag = f"{r.emoji} **{r.label}**" if r else ""
            lines.append(f"{tag} · \U0001F527 **{t.name}**")
    return lines


def daily_pack_embed(drops: list[tuple[str, str]]) -> dict[str, Any]:
    """drops: list of (card_type, card_id) pairs."""
    lines = _pack_lines(drops)
    return {
        "title": "\U0001F381 Daily Dust Pack",
        "description": "\n".join(lines) if lines else "_(empty pack — this is a bug)_",
        "color": 0xCA8A04,
        "footer": {"text": "Come back tomorrow for another pack."},
    }


def pack_reveal_embed(pack_id: str, drops: list[tuple[str, str]], *, coins_left: int) -> dict[str, Any]:
    """Result of a shop purchase. Includes remaining coin balance."""
    pack = packs_data.BY_ID.get(pack_id)
    title = f"{pack.emoji} {pack.name}" if pack else "Pack"
    lines = _pack_lines(drops)
    return {
        "title": title,
        "description": "\n".join(lines) if lines else "_(empty pack — this is a bug)_",
        "color": 0xCA8A04,
        "footer": {"text": f"Remaining: \U0001FA99 {coins_left} coins."},
    }


def fusion_menu_embed(totals_by_rarity: dict[str, int]) -> dict[str, Any]:
    """Show every fusable tier, with current owned count and recipe cost."""
    from data import fusion as fusion_data
    lines = []
    for rcp in fusion_data.RECIPES:
        from_r = rarities_data.BY_ID.get(rcp.from_rarity)
        to_r   = rarities_data.BY_ID.get(rcp.to_rarity)
        have = int(totals_by_rarity.get(rcp.from_rarity, 0))
        ok = "✅" if have >= rcp.cost else "❌"
        from_tag = f"{from_r.emoji} {from_r.label}" if from_r else rcp.from_rarity
        to_tag   = f"{to_r.emoji} {to_r.label}"   if to_r   else rcp.to_rarity
        lines.append(
            f"{ok} **{rcp.cost}× {from_tag}** → 1× {to_tag}  ·  you have **{have}**"
        )
    return {
        "title": "\U0001F501 Card Fusion",
        "description": "Pick a tier from the menu to combine duplicates.\n\n" + "\n".join(lines),
        "color": 0x6366F1,
        "footer": {"text": "Highest-count copies are consumed first."},
    }


def fusion_confirm_embed(
    from_rarity: str, to_rarity: str, cost: int,
    plan: list[tuple[str, str, int]],
) -> dict[str, Any]:
    from_r = rarities_data.BY_ID.get(from_rarity)
    to_r   = rarities_data.BY_ID.get(to_rarity)
    plan_lines = []
    for card_type, card_id, qty in plan:
        if card_type == "maid":
            m = maids_data.BY_ID.get(card_id)
            name = m.name if m else card_id
        else:
            t = tools_data.BY_ID.get(card_id)
            name = t.name if t else card_id
        plan_lines.append(f"  • **{name}** × {qty}")
    return {
        "title": f"\U0001F501 Fuse {cost}× {from_r.label if from_r else from_rarity} → 1× {to_r.label if to_r else to_rarity}?",
        "description": "These cards will be consumed:\n" + "\n".join(plan_lines),
        "color": 0xA855F7,
        "footer": {"text": "Confirm to fuse, or cancel."},
    }


def fusion_result_embed(
    consumed: list[tuple[str, str, int]],
    result_type: str, result_id: str,
) -> dict[str, Any]:
    if result_type == "maid":
        m = maids_data.BY_ID.get(result_id)
        name = m.name if m else result_id
        rarity = m.rarity if m else ""
        kind_tag = "\U0001F9E0 Maid"
    else:
        t = tools_data.BY_ID.get(result_id)
        name = t.name if t else result_id
        rarity = t.rarity if t else ""
        kind_tag = "\U0001F527 Tool"
    r = rarities_data.BY_ID.get(rarity)
    color = r.color if r else 0x6366F1
    rtag = f"{r.emoji} **{r.label}**" if r else rarity
    return {
        "title": "✨ Fusion complete",
        "description": f"You crafted: {rtag} · {kind_tag} **{name}**",
        "color": color,
        "footer": {"text": "Find it in /maid cards."},
    }


def pack_shop_embed(coins: int) -> dict[str, Any]:
    """List shop packs with prices, contents, and current coin balance."""
    fields = []
    for p in packs_data.ALL:
        affordable = coins >= p.price
        price_tag = f"\U0001FA99 {p.price}" + ("" if affordable else "  _(need more coins)_")
        fields.append({
            "name": f"{p.emoji} {p.name} — {price_tag}",
            "value": f"{p.description}\n_{p.flavor}_" if p.flavor else p.description,
            "inline": False,
        })
    return {
        "title": "\U0001F3EA Maid Manor Shop",
        "description": f"You have **\U0001FA99 {coins}** coins.",
        "color": 0xCA8A04,
        "fields": fields,
        "footer": {"text": "Earn coins by winning battles or claiming /maid daily."},
    }


# ── Collection listing ──────────────────────────────────────────────────────

def collection_embed(
    rows: list[dict[str, Any]],
    *,
    page: int,
    page_size: int,
    total: int,
) -> dict[str, Any]:
    total_pages = max(1, (total + page_size - 1) // page_size)
    lines = []
    for row in rows:
        card_type = row.get("card_type")
        card_id = row.get("card_id")
        count = int(row.get("count", 0))
        lvl = int(row.get("level", 1))
        if card_type == "maid":
            m = maids_data.BY_ID.get(card_id)
            if not m:
                continue
            r = rarities_data.BY_ID.get(m.rarity)
            tag = r.emoji if r else "·"
            lines.append(f"{tag} **{m.name}** — x{count} (Lv {lvl})")
        else:
            t = tools_data.BY_ID.get(card_id)
            if not t:
                continue
            r = rarities_data.BY_ID.get(t.rarity)
            tag = r.emoji if r else "·"
            lines.append(f"{tag} **{t.name}** — x{count}")
    return {
        "title": "\U0001F4D6 Your Collection",
        "description": "\n".join(lines) if lines else "_You don't own any cards yet. Try `/maid daily`._",
        "color": 0x6366F1,
        "footer": {"text": f"Page {page + 1} / {total_pages}  ·  {total} unique cards"},
    }


# ── Deck view ───────────────────────────────────────────────────────────────

def deck_embed(deck: dict[str, list[str]]) -> dict[str, Any]:
    def slot_line(card_type: str, card_id: str, idx: int) -> str:
        if not card_id:
            return f"`{idx + 1}.` _(empty)_"
        if card_type == "maid":
            m = maids_data.BY_ID.get(card_id)
            if not m:
                return f"`{idx + 1}.` Unknown maid `{card_id}`"
            r = rarities_data.BY_ID.get(m.rarity)
            return f"`{idx + 1}.` {r.emoji if r else '·'} **{m.name}**"
        t = tools_data.BY_ID.get(card_id)
        if not t:
            return f"`{idx + 1}.` Unknown tool `{card_id}`"
        r = rarities_data.BY_ID.get(t.rarity)
        return f"`{idx + 1}.` {r.emoji if r else '·'} **{t.name}**"

    maid_lines = [slot_line("maid", c, i) for i, c in enumerate((deck.get("maids") or []) + [""] * 3)][:3]
    tool_lines = [slot_line("tool", c, i) for i, c in enumerate((deck.get("tools") or []) + [""] * 3)][:3]
    return {
        "title": "\U0001F9FA Your Deck",
        "color": 0x16A34A,
        "fields": [
            {"name": "Maids (3)", "value": "\n".join(maid_lines) or "_(empty)_", "inline": False},
            {"name": "Tools (3)", "value": "\n".join(tool_lines) or "_(empty)_", "inline": False},
        ],
        "footer": {"text": "Use the menu below to fill empty slots from your collection."},
    }


# ── Battle ──────────────────────────────────────────────────────────────────

def _team_block(units: list[dict[str, Any]], *, prefix: str) -> str:
    parts = []
    for i, u in enumerate(units):
        name = u.get("name", "?")
        cur = max(0, int(u.get("poise", 0)))
        mx  = max(1, int(u.get("max_poise", cur)))
        bar = _hp_bar(cur, mx)
        line = f"`{prefix}{i + 1}` **{name}** {bar} {cur}/{mx}"
        if cur <= 0:
            line = f"~~{line}~~  💀"
        parts.append(line)
    return "\n".join(parts) or "_(empty)_"


def _hp_bar(cur: int, mx: int, width: int = 10) -> str:
    if mx <= 0:
        return "·" * width
    filled = max(0, min(width, round(cur / mx * width)))
    return "█" * filled + "░" * (width - filled)


def battle_embed(state: dict[str, Any]) -> dict[str, Any]:
    player_team = state.get("player_team") or []
    enemy_team = state.get("enemy_team") or []
    log_lines = state.get("log") or []
    log_text = "\n".join(f"• {line}" for line in log_lines[-5:]) or "_The battle begins._"
    turn = int(state.get("turn", 1))
    return {
        "title": f"⚔️ Maid & Mayhem — Turn {turn}",
        "color": 0xDC2626,
        "fields": [
            {"name": "Your Maids",   "value": _team_block(player_team, prefix="P"), "inline": False},
            {"name": "Chaos",        "value": _team_block(enemy_team,  prefix="E"), "inline": False},
            {"name": "Battle Log",   "value": log_text, "inline": False},
        ],
        "footer": {"text": "Pick a maid, then a target. Defeat all chaos to win."},
    }


def battle_result_embed(state: dict[str, Any], *, won: bool, coins: int, xp: int) -> dict[str, Any]:
    title = "\U0001F3C6 Victory" if won else "\U0001F480 Defeat"
    color = 0x22C55E if won else 0x6B7280
    desc = ("The manor is clean. For now." if won
            else "The chaos wins this round. Regroup at /maid deck and try again.")
    fields = [
        {"name": "Rewards", "value": f"\U0001FA99 {coins} coins\n✨ {xp} XP", "inline": True},
    ]
    return {"title": title, "description": desc, "color": color, "fields": fields}


# ── Leaderboard ─────────────────────────────────────────────────────────────

def leaderboard_embed(rows: list[dict[str, Any]], display_names: dict[str, str]) -> dict[str, Any]:
    if not rows:
        return {
            "title": "\U0001F3C5 Top Maids",
            "description": "_No battles fought yet. Be the first — `/maid battle`._",
            "color": 0xCA8A04,
        }
    lines = []
    for idx, row in enumerate(rows, start=1):
        uid = str(row.get("user_id", ""))
        name = display_names.get(uid, uid)
        xp = int(row.get("xp", 0))
        wins = int(row.get("wins", 0))
        losses = int(row.get("losses", 0))
        medal = {1: "\U0001F947", 2: "\U0001F948", 3: "\U0001F949"}.get(idx, f"`{idx:>2}`")
        lines.append(f"{medal} **{name}** — {xp} XP · {wins}W/{losses}L")
    return {
        "title": "\U0001F3C5 Top Maids",
        "description": "\n".join(lines),
        "color": 0xCA8A04,
    }


# ── Chaos enemy (used during battle render) ─────────────────────────────────

def chaos_summary(enemy_id: str) -> str:
    c = chaos_data.BY_ID.get(enemy_id)
    if not c:
        return enemy_id
    e = elements_data.BY_ID.get(c.element)
    return f"{e.emoji if e else ''} **{c.name}**  (T{c.tier})"
