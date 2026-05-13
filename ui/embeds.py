"""Discord embed builders.

Each builder returns a list of embed dicts ready for
`ctx.interaction.respond(embeds=...)`.
"""
from __future__ import annotations

from typing import Any

from data import chaos as chaos_data
from data import cosmetics as cosmetics_data
from data import elements as elements_data
from data import maids as maids_data
from data import packs as packs_data
from data import raid_bosses as raid_bosses_data
from data import ranks as ranks_data
from data import rarities as rarities_data
from data import rooms as rooms_data
from data import tools as tools_data


# ── Profile ─────────────────────────────────────────────────────────────────

def profile_embed(
    profile: dict[str, Any], display_name: str,
    cosmetics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    xp = int(profile.get("xp", 0))
    level = int(profile.get("level", 1))
    wins = int(profile.get("wins", 0))
    losses = int(profile.get("losses", 0))
    coins = int(profile.get("coins", 0))
    polish = int(profile.get("polish", 0))
    next_lvl_xp = 50 * (level + 1) * level

    # Equipped cosmetics (optional)
    color = 0xCA8A04
    title_line = ""
    badge_emoji = ""
    if cosmetics:
        eq = cosmetics.get("equipped") or {}
        if int(eq.get("color", 0)) > 0:
            color = int(eq.get("color", 0))
        if eq.get("title"):
            c = cosmetics_data.BY_ID.get(str(eq["title"]))
            if c and c.slot == "title":
                title_line = str(c.value)
        if eq.get("badge"):
            c = cosmetics_data.BY_ID.get(str(eq["badge"]))
            if c and c.slot == "badge":
                badge_emoji = str(c.value)

    title = f"\U0001F9F9 {display_name}'s Maid Manor"
    if title_line:
        title = f"{badge_emoji + ' ' if badge_emoji else ''}{display_name} — {title_line}"
    elif badge_emoji:
        title = f"{badge_emoji} {display_name}'s Maid Manor"

    return {
        "title": title,
        "color": color,
        "fields": [
            {"name": "Level",   "value": f"**{level}**  ({xp}/{next_lvl_xp} XP)", "inline": True},
            {"name": "Coins",   "value": f"\U0001FA99 {coins}", "inline": True},
            {"name": "Polish",  "value": f"✨ {polish}",        "inline": True},
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


def chaos_card_embed(chaos_id: str) -> dict[str, Any]:
    c = chaos_data.BY_ID.get(chaos_id)
    if not c:
        return {"title": "Unknown chaos enemy", "description": f"`{chaos_id}`", "color": 0x6B7280}
    e = elements_data.BY_ID.get(c.element)
    title = f"\U0001F47E {c.name}"
    subtitle_bits = [f"**Chaos · Tier {c.tier}**"]
    if e:
        subtitle_bits.append(f"{e.emoji} {e.label}")
    desc = " · ".join(subtitle_bits)
    fields = [
        {"name": "Poise",        "value": f"\U0001F6E1 {c.poise}",       "inline": True},
        {"name": "Clean Power",  "value": f"\U0001F9F9 {c.clean_power}", "inline": True},
        {"name": "Speed",        "value": f"⚡ {c.speed}",        "inline": True},
        {"name": c.ability_name, "value": c.ability_text,                 "inline": False},
    ]
    return {
        "title": title,
        "description": desc + (f"\n\n_{c.flavor}_" if c.flavor else ""),
        "color": (e.color if e else 0x6B7280),
        "fields": fields,
    }


def raid_boss_card_embed(boss_id: str) -> dict[str, Any]:
    b = raid_bosses_data.BY_ID.get(boss_id)
    if not b:
        return {"title": "Unknown raid boss", "description": f"`{boss_id}`", "color": 0x6B7280}
    e = elements_data.BY_ID.get(b.element)
    title = f"{b.emoji} {b.name}"
    bits = [f"**Raid Boss · Tier {b.tier}**"]
    if e:
        bits.append(f"{e.emoji} {e.label}")
    desc = " · ".join(bits)
    return {
        "title": title,
        "description": desc + f"\n\n**HP:** {b.hp:,}" + (f"\n\n_{b.flavor}_" if b.flavor else ""),
        "color": 0xDC2626,
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


def achievements_embed(state: dict[str, Any]) -> dict[str, Any]:
    from data import achievements as ach_data
    unlocked = set(state.get("unlocked") or [])
    counters = state.get("counters") or {}

    fields = []
    total = len(ach_data.ALL)
    got = sum(1 for a in ach_data.ALL if a.id in unlocked)

    for cat in ach_data.CATEGORIES:
        items = ach_data.by_category(cat)
        if not items:
            continue
        lines = []
        for a in items:
            mark = "✅" if a.id in unlocked else "▫️"
            prog = int(counters.get(a.counter, 0))
            target = int(a.target)
            if a.id in unlocked:
                prog_text = "**unlocked**"
            else:
                prog_text = f"{min(prog, target)}/{target}"
            reward = f"\U0001FA99 +{a.reward_coins}"
            if a.reward_xp:     reward += f" · ✨+{a.reward_xp}xp"
            if a.reward_polish: reward += f" · ✨P+{a.reward_polish}"
            lines.append(f"{mark} **{a.name}** — {a.description}\n  {prog_text}  ·  {reward}")
        fields.append({
            "name":  ach_data.CATEGORY_LABELS.get(cat, cat),
            "value": "\n".join(lines),
            "inline": False,
        })

    return {
        "title": f"\U0001F3C5 Achievements — {got}/{total} unlocked",
        "color": 0xCA8A04 if got == total else 0x6366F1,
        "description": (
            "Each one is permanent and credits its reward the moment you hit the target. "
            "Some counters update automatically from your battles, raids, and shop activity."
        ),
        "fields": fields,
    }


def achievement_unlock_embed(unlocked_ids: list[str]) -> dict[str, Any]:
    """Shown in-line when a player just earned one or more achievements."""
    from data import achievements as ach_data
    if not unlocked_ids:
        return {}
    lines = []
    total_coins = total_xp = total_polish = 0
    for aid in unlocked_ids:
        a = ach_data.BY_ID.get(aid)
        if not a:
            continue
        bits = [f"\U0001FA99 +{a.reward_coins}"]
        if a.reward_xp:     bits.append(f"✨+{a.reward_xp}xp")
        if a.reward_polish: bits.append(f"✨P+{a.reward_polish}")
        lines.append(f"🏅 **{a.name}** — {a.description}\n   _{'  '.join(bits)}_")
        total_coins += a.reward_coins
        total_xp     += a.reward_xp
        total_polish += a.reward_polish
    return {
        "title": "🏅 Achievement unlocked!" if len(unlocked_ids) == 1 else f"🏅 {len(unlocked_ids)} achievements unlocked!",
        "color": 0xF59E0B,
        "description": "\n\n".join(lines),
        "footer": {"text": "Rewards already credited — check /maid profile."},
    }


def quests_embed(state: dict[str, Any]) -> dict[str, Any]:
    from data import quests as quests_data

    def _quest_lines(bucket: list[dict[str, Any]]) -> str:
        if not bucket:
            return "_(none active)_"
        lines = []
        for q in bucket:
            t = quests_data.by_id(q.get("id", ""))
            if not t:
                continue
            prog   = int(q.get("progress", 0))
            target = int(q.get("target", 1))
            pct    = int(round(100 * prog / max(1, target)))
            filled = max(0, min(10, round(pct / 10)))
            bar    = "▰" * filled + "▱" * (10 - filled)
            if q.get("claimed"):
                status = "✅ claimed"
            elif prog >= target:
                status = "🎁 ready to claim"
            else:
                status = f"{prog}/{target}"
            reward = f"\U0001FA99 +{t.reward_coins}  ✨ +{t.reward_xp} XP"
            if t.reward_polish:
                reward += f"  ✨P +{t.reward_polish}"
            lines.append(
                f"**{t.name}**\n  `{bar}` {status} — {t.description.format(target=target)}\n  Reward: {reward}"
            )
        return "\n\n".join(lines)

    daily  = state.get("daily")  or []
    weekly = state.get("weekly") or []
    return {
        "title": "\U0001F4DC Quests",
        "color": 0x6366F1,
        "description": (
            f"Daily — resets at 00:00 UTC ({state.get('daily_date', '?')})\n"
            f"Weekly — resets on Monday ({state.get('weekly_date', '?')})"
        ),
        "fields": [
            {"name": "\U0001F305 Daily",  "value": _quest_lines(daily),  "inline": False},
            {"name": "\U0001F4C5 Weekly", "value": _quest_lines(weekly), "inline": False},
        ],
        "footer": {"text": "Click Claim under each completed quest to collect the reward."},
    }


def quest_claim_embed(reward: dict[str, Any], *, coins: int, xp: int) -> dict[str, Any]:
    lines = [f"  \U0001FA99 +{coins} coins", f"  ✨ +{xp} XP"]
    if int(reward.get("polish", 0)) > 0:
        lines.append(f"  ✨ +{int(reward['polish'])} Polish")
    return {
        "title": f"\U0001F389 Quest claimed: {reward.get('name', '?')}",
        "description": "\n".join(lines),
        "color": 0x22C55E,
    }


def cosmetics_embed(profile: dict[str, Any], cosmetics: dict[str, Any]) -> dict[str, Any]:
    polish = int(profile.get("polish", 0))
    owned = set(cosmetics.get("owned") or [])
    equipped = cosmetics.get("equipped") or {}

    def _slot_section(slot: str) -> str:
        lines = []
        for c in cosmetics_data.by_slot(slot):
            is_owned = c.id in owned
            is_equipped = (
                (slot == "color" and int(equipped.get("color", 0)) == int(c.value))
                or (slot != "color" and equipped.get(slot) == c.id)
            )
            mark = "✅" if is_equipped else ("\U0001F3F7" if is_owned else f"✨{c.polish_cost}")
            preview = f"_{c.value}_" if slot == "title" else (
                str(c.value) if slot == "badge" else f"#{int(c.value):06X}"
            )
            lines.append(f"{mark}  **{c.name}** — {preview}")
        return "\n".join(lines) or "_(none)_"

    return {
        "title": "✨ Cosmetic Shop",
        "color": int(equipped.get("color", 0)) or 0xCA8A04,
        "description": f"You have **✨ {polish}** Polish.",
        "fields": [
            {"name": "Titles",  "value": _slot_section("title"), "inline": False},
            {"name": "Badges",  "value": _slot_section("badge"), "inline": False},
            {"name": "Colors",  "value": _slot_section("color"), "inline": False},
        ],
        "footer": {"text": "✨ = price · 🏷 = owned · ✅ = equipped. Use the menus to buy or equip."},
    }


def cosmetic_buy_result_embed(cosmetic, *, polish_left: int) -> dict[str, Any]:
    return {
        "title": "\U0001F381 Cosmetic acquired",
        "description": f"**{cosmetic.name}** added to your collection.\n_{cosmetic.flavor}_",
        "color": int(cosmetic.value) if cosmetic.slot == "color" else 0xCA8A04,
        "footer": {"text": f"Remaining: ✨ {polish_left}. Equip it via /maid cosmetics."},
    }


def cosmetic_equip_result_embed(cosmetic) -> dict[str, Any]:
    preview = f"_{cosmetic.value}_" if cosmetic.slot == "title" else (
        str(cosmetic.value) if cosmetic.slot == "badge" else f"#{int(cosmetic.value):06X}"
    )
    return {
        "title": f"Equipped: {cosmetic.name}",
        "description": f"Slot: **{cosmetic.slot}** — {preview}",
        "color": int(cosmetic.value) if cosmetic.slot == "color" else 0xCA8A04,
    }


def raid_embed(state: dict[str, Any], top: list[tuple[str, int]], display_names: dict[str, str]) -> dict[str, Any]:
    boss = raid_bosses_data.BY_ID.get(state.get("boss_id", ""))
    if not boss:
        return {"title": "Raid", "description": "_(no active raid)_", "color": 0x6B7280}
    cur = int(state.get("hp", 0))
    mx  = int(state.get("max_hp", boss.hp))
    bar = _hp_bar(cur, mx, width=24)
    contribs = state.get("contributors") or {}
    n_attackers = len([v for v in contribs.values() if int(v) > 0])
    el = elements_data.BY_ID.get(boss.element)
    el_tag = f"{el.emoji} {el.label}" if el else boss.element
    lines = [f"`{bar}` **{cur:,}** / {mx:,} HP",
             f"Element: {el_tag} · Tier: {boss.tier}",
             f"_{boss.flavor}_"]
    if top:
        leader_lines = []
        for idx, (uid, dmg) in enumerate(top, start=1):
            medal = {1: "\U0001F947", 2: "\U0001F948", 3: "\U0001F949"}.get(idx, f"`{idx:>2}`")
            name = display_names.get(uid, uid)
            leader_lines.append(f"{medal} **{name}** — {dmg:,} dmg")
        leaderboard = "\n".join(leader_lines)
    else:
        leaderboard = "_No one has attacked yet — be the first!_"
    return {
        "title": f"{boss.emoji} {boss.name} — Chaos Raid",
        "color": 0xDC2626,
        "description": "\n".join(lines),
        "fields": [
            {"name": f"Top contributors ({n_attackers} total)",
             "value": leaderboard, "inline": False},
        ],
        "footer": {"text": "Click Attack to strike — 30 minute cooldown per player."},
    }


def raid_attack_result_embed(
    *, damage: int, killed: bool, hp_left: int, max_hp: int,
    boss_name: str, attacker_name: str,
) -> dict[str, Any]:
    title = f"💥 {attacker_name} attacks {boss_name}!"
    desc = f"Dealt **{damage:,}** damage."
    if killed:
        title = f"\U0001F389 {boss_name} has been cleaned up!"
        desc += "\nThe killing blow! Rewards will be distributed when the raid embed refreshes."
    else:
        desc += f"\n{boss_name} has **{hp_left:,}** / {max_hp:,} HP remaining."
    color = 0x22C55E if killed else 0xF59E0B
    return {"title": title, "description": desc, "color": color}


def raid_reward_summary_embed(
    boss_name: str, rewards: dict[str, dict[str, Any]],
    display_names: dict[str, str],
) -> dict[str, Any]:
    if not rewards:
        return {"title": "Raid resolved", "description": "_No contributors._", "color": 0x6B7280}
    ordered = sorted(rewards.items(), key=lambda kv: kv[1].get("damage", 0), reverse=True)
    lines = []
    for uid, b in ordered:
        name = display_names.get(uid, uid)
        tier_emoji = {"champion": "\U0001F947", "officer": "\U0001F948", "helper": "\U0001F49B"}.get(b.get("tier"), "·")
        pack_str = ""
        if int(b.get("royal_packs", 0)):    pack_str += f"  +\U0001F451"
        if int(b.get("polished_packs", 0)): pack_str += f"  +\U0001F4E6"
        lines.append(
            f"{tier_emoji} **{name}** — {b.get('damage', 0):,} dmg ({b.get('pct', 0):.0f}%) → "
            f"\U0001FA99 +{b.get('coins', 0)} · ✨ +{b.get('xp', 0)} XP{pack_str}"
        )
    return {
        "title": f"\U0001F3C6 {boss_name} — Raid rewards distributed",
        "description": "\n".join(lines),
        "color": 0xCA8A04,
        "footer": {"text": "A new raid has just begun!"},
    }


def rank_embed(state: dict[str, Any], display_name: str) -> dict[str, Any]:
    """Show current season, rank, RP, and progress to the next tier."""
    from engine import ranks as ranks_engine
    rp = int(state.get("rp", 0))
    rank = ranks_engine.current_rank(rp)
    nxt = ranks_engine.next_rank(rp)
    into, span, pct = ranks_engine.progress_to_next(rp)
    bar_w = 20
    filled = max(0, min(bar_w, round(pct / 100 * bar_w)))
    bar = "█" * filled + "░" * (bar_w - filled)

    if nxt is None:
        progress_line = f"`{bar}` — Top of the ladder."
    else:
        progress_line = f"`{bar}` {into}/{span} RP to **{nxt.name}**"

    peak = ranks_data.BY_ID.get(state.get("peak_rank", "dust_bunny"))
    career = ranks_data.BY_ID.get(state.get("career_peak", "dust_bunny"))
    fields = [
        {"name": "Season RP", "value": f"**{rp}**\n{progress_line}", "inline": False},
        {"name": "Season peak", "value": f"{peak.emoji} {peak.name}" if peak else "—", "inline": True},
        {"name": "Career peak", "value": f"{career.emoji} {career.name}" if career else "—", "inline": True},
        {"name": "Season",      "value": state.get("season", "—"),                           "inline": True},
    ]
    return {
        "title": f"{rank.emoji} {display_name} — {rank.name}",
        "color": rank.color,
        "fields": fields,
        "footer": {"text": "RP resets on the 1st of every month. End-of-season rewards land on your next /maid command."},
    }


def season_rollover_embed(summary: dict[str, Any], display_name: str) -> dict[str, Any]:
    """Shown on the user's first interaction of a new season."""
    peak = ranks_data.BY_ID.get(summary.get("prior_peak", "dust_bunny"))
    peak_str = f"{peak.emoji} {peak.name}" if peak else summary.get("prior_peak", "?")
    lines = [f"Season **{summary.get('prior_season', '?')}** ended at {peak_str}."]
    coins = int(summary.get("coins", 0))
    if coins:
        lines.append(f"  \U0001FA99 +{coins} coins")
    polished = int(summary.get("polished_packs", 0))
    if polished:
        lines.append(f"  \U0001F4E6 {polished}× Polished Pack opened")
    royal = int(summary.get("royal_packs", 0))
    if royal:
        lines.append(f"  \U0001F451 {royal}× Royal Service Pack opened")
    if summary.get("guaranteed_mythic"):
        lines.append("  ❤️‍\U0001F525 Bonus: 1 guaranteed Mythic card")
    polish = int(summary.get("polish", 0))
    if polish:
        lines.append(f"  ✨ +{polish} Polish")
    return {
        "title": "\U0001F389 Season ended — rewards delivered",
        "description": "\n".join(lines) + "\n\nUse `/maid cards` to see the new arrivals.",
        "color": 0xCA8A04,
    }


def manor_embed(manor: dict[str, int], coins: int) -> dict[str, Any]:
    """Show every room with its current level, effect at that level, and
    the price to upgrade to the next level. Highlights affordable upgrades.
    """
    fields = []
    for room in rooms_data.ALL:
        lvl = int(manor.get(room.id, 1))
        at_max = lvl >= rooms_data.MAX_LEVEL
        cost = rooms_data.upgrade_cost(lvl) if not at_max else 0
        affordable = coins >= cost and not at_max
        lvl_bar = "▰" * lvl + "▱" * (rooms_data.MAX_LEVEL - lvl)
        if at_max:
            upgrade_line = "_Maxed._"
        else:
            check = "✅" if affordable else "❌"
            upgrade_line = f"{check} Upgrade to L{lvl + 1} — \U0001FA99 **{cost}**"
        fields.append({
            "name": f"{room.emoji} {room.name} — L{lvl}/{rooms_data.MAX_LEVEL}",
            "value": (
                f"`{lvl_bar}`\n"
                f"{room.description}\n"
                f"_{room.bonus_per_level} per level_\n"
                f"{upgrade_line}"
            ),
            "inline": False,
        })
    return {
        "title": "\U0001F3F0 Your Maid Manor",
        "description": f"You have **\U0001FA99 {coins}** coins.\nUpgrade rooms below to buff future rewards.",
        "color": 0x7C3AED,
        "fields": fields,
    }


def manor_upgrade_result_embed(
    room_id: str, *, from_level: int, to_level: int, coins_left: int,
) -> dict[str, Any]:
    room = rooms_data.BY_ID.get(room_id)
    if not room:
        return {"title": "Upgrade", "description": "Room not found.", "color": 0x6B7280}
    return {
        "title": f"{room.emoji} {room.name} upgraded!",
        "description": (
            f"**L{from_level} → L{to_level}**\n"
            f"_{room.bonus_per_level}_ now stacks {to_level} times."
        ),
        "color": 0x7C3AED,
        "footer": {"text": f"Remaining: \U0001FA99 {coins_left} coins."},
    }


def duel_challenge_embed(
    challenger_id: str, challenger_name: str,
    target_id: str, target_name: str,
    *, expires_in_s: int,
) -> dict[str, Any]:
    return {
        "title": "⚔ Duel Challenge",
        "description": (
            f"**{challenger_name}** has challenged **{target_name}** to a Maid & Mayhem duel.\n\n"
            f"<@{target_id}> — click **Accept** to begin, or **Decline** to refuse.\n"
            f"_Expires in {expires_in_s}s._"
        ),
        "color": 0xCA8A04,
    }


def _duel_team_block(side: dict[str, Any]) -> str:
    units = side.get("team") or []
    parts = []
    for i, u in enumerate(units):
        name = u.get("name", "?")
        cur = max(0, int(u.get("poise", 0)))
        mx  = max(1, int(u.get("max_poise", cur)))
        bar = _hp_bar(cur, mx)
        line = f"`{i + 1}` **{name}** {bar} {cur}/{mx}"
        if cur <= 0:
            line = f"~~{line}~~  💀"
        parts.append(line)
    return "\n".join(parts) or "_(empty)_"


def duel_embed(state: dict[str, Any]) -> dict[str, Any]:
    a = state["a"]; b = state["b"]
    turn_owner = state.get("turn_owner")
    active_name = a["user_name"] if turn_owner == "a" else b["user_name"]
    log_lines = state.get("log") or []
    log_text = "\n".join(f"• {line}" for line in log_lines[-6:]) or "_The duel begins._"
    title = f"⚔ Duel — Round {state.get('turn', 1)} — {active_name}'s turn"
    return {
        "title": title,
        "color": 0xDC2626,
        "fields": [
            {"name": f"{a['user_name']}", "value": _duel_team_block(a), "inline": False},
            {"name": f"{b['user_name']}", "value": _duel_team_block(b), "inline": False},
            {"name": "Log",               "value": log_text,            "inline": False},
        ],
        "footer": {"text": f"Only {active_name} can act this turn."},
    }


def duel_result_embed(state: dict[str, Any]) -> dict[str, Any]:
    result = state.get("result", "")
    a = state["a"]; b = state["b"]
    if result == "a_wins":
        title = f"🏆 {a['user_name']} wins!"
        color = 0x22C55E
    elif result == "b_wins":
        title = f"🏆 {b['user_name']} wins!"
        color = 0x22C55E
    elif result == "a_fled":
        title = f"🏳 {a['user_name']} fled — {b['user_name']} wins by forfeit."
        color = 0x6B7280
    elif result == "b_fled":
        title = f"🏳 {b['user_name']} fled — {a['user_name']} wins by forfeit."
        color = 0x6B7280
    else:
        title = "Duel ended."
        color = 0x6B7280
    fields = []
    lvlups = state.get("_levelups") or {}
    for side_key in ("a", "b"):
        uid = state[side_key]["user_id"]
        side_lvls = lvlups.get(uid) or []
        block = _levelup_lines(side_lvls)
        if block:
            fields.append({"name": f"{state[side_key]['user_name']} — progression", "value": block, "inline": False})
    return {
        "title": title,
        "color": color,
        "description": "Rewards have been credited. Check `/maid profile`.",
        "fields": fields,
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


def _levelup_lines(levelups: list[tuple[str, int, int]]) -> str:
    """Format a list of (card_id, new_level, levels_gained) into a small block."""
    if not levelups:
        return ""
    out = []
    for card_id, new_level, gained in levelups:
        m = maids_data.BY_ID.get(card_id)
        name = m.name if m else card_id
        if gained == 1:
            out.append(f"✨ **{name}** reached Level **{new_level}**.")
        else:
            out.append(f"✨ **{name}** gained {gained} levels — now **L{new_level}**.")
    return "\n".join(out)


def battle_result_embed(
    state: dict[str, Any], *, won: bool, coins: int, xp: int,
    levelups: list[tuple[str, int, int]] | None = None,
) -> dict[str, Any]:
    title = "\U0001F3C6 Victory" if won else "\U0001F480 Defeat"
    color = 0x22C55E if won else 0x6B7280
    desc = ("The manor is clean. For now." if won
            else "The chaos wins this round. Regroup at /maid deck and try again.")
    fields = [
        {"name": "Rewards", "value": f"\U0001FA99 {coins} coins\n✨ {xp} XP", "inline": True},
    ]
    lvl_block = _levelup_lines(levelups or [])
    if lvl_block:
        fields.append({"name": "Card progression", "value": lvl_block, "inline": False})
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
