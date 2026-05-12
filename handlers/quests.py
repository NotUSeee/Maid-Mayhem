"""/maid quests — view daily + weekly quests and claim rewards."""
from __future__ import annotations

from mmo_maid_sdk import ActionRow, Button, Context

from data import quests as quests_data
from engine import manor as manor_engine
from engine import quests as quests_engine
from store import kv
from ui import embeds


def _components(state: dict) -> list[ActionRow]:
    """One Claim button per quest that's complete-and-unclaimed.
    Discord caps an ActionRow at 5 buttons, so we wrap if needed."""
    ready: list[tuple[str, str]] = []
    for bucket in ("daily", "weekly"):
        for q in state.get(bucket, []) or []:
            if q.get("claimed"):
                continue
            if int(q.get("progress", 0)) < int(q.get("target", 1)):
                continue
            t = quests_data.by_id(q.get("id", ""))
            label = f"Claim: {t.name if t else q['id']}"
            ready.append((q["id"], label))
    rows: list[ActionRow] = []
    for i in range(0, len(ready), 5):
        chunk = ready[i:i + 5]
        rows.append(ActionRow(*[
            Button(label[:80], custom_id=f"mm:quests:claim:{qid}", style="success")
            for qid, label in chunk
        ]))
    return rows


def run(ctx: Context, event: dict) -> None:
    user_id = str(event.get("user_id") or "")
    if not user_id:
        ctx.interaction.respond(content="Could not identify user.", ephemeral=True)
        return
    state = quests_engine.load(ctx, user_id)
    ctx.interaction.respond(
        embeds=[embeds.quests_embed(state)],
        components=_components(state),
        ephemeral=True,
    )


def on_component(ctx: Context, event: dict, tail: list[str]) -> None:
    if not tail or tail[0] != "claim" or len(tail) < 2:
        return
    user_id = str(event.get("user_id") or "")
    if not user_id:
        return
    qid = tail[1]

    if not ctx.ephemeral.dedup(f"mm:quests:claim:{user_id}:{qid}", ttl_seconds=3):
        return

    reward = quests_engine.claim(ctx, user_id, qid)
    if reward is None:
        ctx.interaction.respond(content="That quest isn't ready to claim.", ephemeral=True)
        return

    # Apply manor bonuses to coin/xp before crediting.
    coins, xp = manor_engine.reward_bonuses_for_user(
        ctx, user_id, coins=int(reward.get("coins", 0)), xp=int(reward.get("xp", 0)),
        is_battle_win=False,
    )
    kv.add_rewards(ctx, user_id, coins=coins, xp=xp, won=False)
    if int(reward.get("polish", 0)) > 0:
        kv.add_polish(ctx, user_id, int(reward["polish"]))

    state = quests_engine.load(ctx, user_id)
    ctx.interaction.respond(
        embeds=[
            embeds.quest_claim_embed(reward, coins=coins, xp=xp),
            embeds.quests_embed(state),
        ],
        components=_components(state),
        ephemeral=True,
    )
