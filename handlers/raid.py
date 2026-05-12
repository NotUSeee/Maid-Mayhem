"""/maid raid — server-wide chaos boss.

A single boss is active per server at any time. Anyone with a built
deck can run /maid raid to see the current state and click Attack.
Each attack is gated by a 30-minute per-user cooldown.

When the boss dies:
    1. Rewards are computed per contributor by % damage dealt.
    2. Coins + XP + free packs are credited.
    3. The killer gets a +50 RP bonus on top of the tier rewards.
    4. The next boss in the cycle spawns immediately.

All state lives in KV (shared across the server because KV is already
server-scoped on the host).
"""
from __future__ import annotations

from mmo_maid_sdk import ActionRow, Button, Context

from data import raid_bosses as bosses_data
from engine import drops, manor as manor_engine, raid as raid_engine, ranks as ranks_engine
from data import packs as packs_data
from store import kv, raid_state, sql as store_sql
from ui import embeds


_ATTACK_COOLDOWN_S = 30 * 60   # 30 min between raid attacks per user
_BACKSTOP_PACK_FLOOR = packs_data.POLISHED.floor   # used in champion/officer pack opens


def _resolve_names(ctx: Context, user_ids: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for uid in user_ids:
        if not uid:
            continue
        try:
            m = ctx.discord.get_member(user_id=uid)
        except Exception:
            m = None
        if isinstance(m, dict):
            out[uid] = m.get("display_name") or m.get("username") or m.get("name") or uid
        else:
            out[uid] = uid
    return out


def _ensure_raid(ctx: Context) -> dict:
    """Make sure a raid exists. Spawns the first boss if none active."""
    state = raid_state.load(ctx)
    if state is None:
        state = raid_engine.fresh_raid(bosses_data.CYCLE[0].id)
        raid_state.save(ctx, state)
    return state


def _components() -> ActionRow:
    return ActionRow(
        Button("⚔ Attack the boss", custom_id="mm:raid:attack", style="danger"),
        Button("\U0001F504 Refresh",  custom_id="mm:raid:refresh",  style="secondary"),
    )


def _render(ctx: Context, state: dict) -> tuple[dict, list[ActionRow]]:
    top = raid_engine.top_contributors(state, limit=5)
    names = _resolve_names(ctx, [uid for uid, _ in top])
    embed = embeds.raid_embed(state, top, names)
    return embed, [_components()]


def run(ctx: Context, event: dict) -> None:
    state = _ensure_raid(ctx)
    embed, components = _render(ctx, state)
    ctx.interaction.respond(embeds=[embed], components=components, ephemeral=False)


def on_component(ctx: Context, event: dict, tail: list[str]) -> None:
    if not tail:
        return
    action = tail[0]
    user_id = str(event.get("user_id") or "")
    if not user_id:
        return

    if action == "refresh":
        state = _ensure_raid(ctx)
        embed, components = _render(ctx, state)
        ctx.interaction.respond(embeds=[embed], components=components, ephemeral=False)
        return

    if action == "attack":
        _do_attack(ctx, event, user_id)
        return


def _do_attack(ctx: Context, event: dict, user_id: str) -> None:
    # Per-user cooldown
    cd = ctx.ephemeral.cooldown_check(f"mm:raid:atk:{user_id}")
    if cd.get("active"):
        remaining = int(cd.get("remaining_seconds", 0))
        mins = max(1, remaining // 60)
        ctx.interaction.respond(
            content=f"Your maids are recovering — wait **{mins} min** before the next strike.",
            ephemeral=True,
        )
        return

    deck = kv.load_deck(ctx, user_id)
    if not [c for c in (deck.get("maids") or []) if c]:
        ctx.interaction.respond(
            content="You need a deck to attack — build one with `/maid deck`.",
            ephemeral=True,
        )
        return

    state = _ensure_raid(ctx)
    state, dmg, killed = raid_engine.attack(state, user_id, deck)
    raid_state.save(ctx, state)

    attacker_name = event.get("user_name") or "Maid"
    boss = bosses_data.BY_ID.get(state["boss_id"])
    boss_name = boss.name if boss else state["boss_id"]

    # Apply cooldown now (also if killed — fairness).
    ctx.ephemeral.cooldown_set(f"mm:raid:atk:{user_id}", ttl_seconds=_ATTACK_COOLDOWN_S)

    if not killed:
        result = embeds.raid_attack_result_embed(
            damage=dmg, killed=False,
            hp_left=int(state["hp"]), max_hp=int(state["max_hp"]),
            boss_name=boss_name, attacker_name=attacker_name,
        )
        embed, components = _render(ctx, state)
        ctx.interaction.respond(embeds=[result, embed], components=components, ephemeral=False)
        return

    # ── Boss killed: distribute rewards, spawn the next one ────────────────
    rewards = raid_engine.distribute_rewards(state)
    _credit_rewards(ctx, rewards)

    # Killing-blow bonus
    ranks_engine.award_rp(ctx, user_id, 50)

    # Resolve names for the summary embed before we wipe state.
    names = _resolve_names(ctx, list(rewards.keys()))

    # Spawn the next boss
    next_b = bosses_data.next_boss(state["boss_id"])
    new_state = raid_engine.fresh_raid(next_b.id)
    raid_state.save(ctx, new_state)

    summary = embeds.raid_reward_summary_embed(boss_name, rewards, names)
    next_embed, next_components = _render(ctx, new_state)
    ctx.interaction.respond(
        embeds=[
            embeds.raid_attack_result_embed(
                damage=dmg, killed=True,
                hp_left=0, max_hp=int(state["max_hp"]),
                boss_name=boss_name, attacker_name=attacker_name,
            ),
            summary,
            next_embed,
        ],
        components=next_components,
        ephemeral=False,
    )


def _credit_rewards(ctx: Context, rewards: dict[str, dict]) -> None:
    import random
    rng = random.Random()
    for uid, b in rewards.items():
        coins = int(b.get("coins", 0))
        xp    = int(b.get("xp", 0))
        # Apply manor multipliers (Tea Room/Kitchen) — battle-bonus does NOT
        # apply here because this isn't a duel/PvE win.
        coins, xp = manor_engine.reward_bonuses_for_user(
            ctx, uid, coins=coins, xp=xp, is_battle_win=False,
        )
        kv.add_rewards(ctx, uid, coins=coins, xp=xp, won=True)
        # Free packs: open them now and write cards into inventory.
        for _ in range(int(b.get("polished_packs", 0))):
            for ct, cid in drops.roll_pack_with_floor(packs_data.POLISHED.n_cards, packs_data.POLISHED.floor, rng):
                store_sql.grant_card(ctx, uid, ct, cid, qty=1)
        for _ in range(int(b.get("royal_packs", 0))):
            for ct, cid in drops.roll_pack_with_floor(packs_data.ROYAL_SERVICE.n_cards, packs_data.ROYAL_SERVICE.floor, rng):
                store_sql.grant_card(ctx, uid, ct, cid, qty=1)
        # Log as a "win" entry for stats parity with battle/duel.
        store_sql.record_battle(ctx, uid, result="win", coins=coins, xp=xp)
