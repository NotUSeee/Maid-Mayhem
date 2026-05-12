"""Quest planner + progression.

Daily quests roll over at UTC midnight; weekly quests roll over on
Monday UTC. Both lineups are date-seeded, so every player on the
server sees the same quests on the same day — handy for "did you do
the dailies?" chat in the server.

KV state shape (``quests:{user_id}``)::

    {
      "daily_date":  "2026-05-12",
      "daily":  [{"id": "d_pve_wins", "target": 3, "progress": 1, "claimed": False}, ...],
      "weekly_date": "2026-W19",
      "weekly": [{"id": "w_pve_run", "target": 20, "progress": 7, "claimed": False}],
    }
"""
from __future__ import annotations

import datetime as _dt
import random
from typing import Any, TYPE_CHECKING

from data import quests as quests_data

if TYPE_CHECKING:
    from mmo_maid_sdk import Context


def _today_id(now: _dt.datetime | None = None) -> str:
    n = now or _dt.datetime.utcnow()
    return n.strftime("%Y-%m-%d")


def _week_id(now: _dt.datetime | None = None) -> str:
    n = now or _dt.datetime.utcnow()
    iso_year, iso_week, _ = n.isocalendar()
    return f"{iso_year}-W{int(iso_week):02d}"


def _pick_dailies(date_id: str) -> list[dict[str, Any]]:
    rng = random.Random(f"daily:{date_id}")
    chosen = rng.sample(list(quests_data.DAILY), k=min(quests_data.DAILY_PICKS, len(quests_data.DAILY)))
    out = []
    for t in chosen:
        target = rng.choice(list(t.target_choices))
        out.append({"id": t.id, "target": int(target), "progress": 0, "claimed": False})
    return out


def _pick_weeklies(week_id: str) -> list[dict[str, Any]]:
    rng = random.Random(f"weekly:{week_id}")
    chosen = rng.sample(list(quests_data.WEEKLY), k=min(quests_data.WEEKLY_PICKS, len(quests_data.WEEKLY)))
    out = []
    for t in chosen:
        target = rng.choice(list(t.target_choices))
        out.append({"id": t.id, "target": int(target), "progress": 0, "claimed": False})
    return out


# ── KV plumbing ─────────────────────────────────────────────────────────────

def _key(user_id: str) -> str:
    return f"quests:{user_id}"


def _refresh(state: dict[str, Any]) -> dict[str, Any]:
    """Reset daily/weekly slots when the calendar has rolled past stored IDs."""
    today = _today_id()
    week  = _week_id()
    if state.get("daily_date") != today:
        state["daily_date"] = today
        state["daily"] = _pick_dailies(today)
    if state.get("weekly_date") != week:
        state["weekly_date"] = week
        state["weekly"] = _pick_weeklies(week)
    return state


def load(ctx: "Context", user_id: str) -> dict[str, Any]:
    raw = ctx.kv.get(_key(user_id))
    state = raw if isinstance(raw, dict) else {}
    state = _refresh(state)
    ctx.kv.set(_key(user_id), state)
    return state


def save(ctx: "Context", user_id: str, state: dict[str, Any]) -> None:
    ctx.kv.set(_key(user_id), state)


# ── Counter bumps from handlers ─────────────────────────────────────────────

def bump(ctx: "Context", user_id: str, counter: str, amount: int = 1) -> list[str]:
    """Add ``amount`` to all active quests matching ``counter``. Returns
    a list of quest IDs that just newly hit their target (ready to claim).
    """
    if amount <= 0 or not user_id:
        return []
    state = load(ctx, user_id)
    newly_ready: list[str] = []
    for bucket in ("daily", "weekly"):
        for q in state.get(bucket, []) or []:
            t = quests_data.by_id(q.get("id", ""))
            if not t or t.counter != counter:
                continue
            if q.get("claimed"):
                continue
            old = int(q.get("progress", 0))
            new = old + amount
            target = int(q.get("target", 1))
            q["progress"] = min(target, new)
            if old < target and q["progress"] >= target:
                newly_ready.append(str(q["id"]))
    save(ctx, user_id, state)
    return newly_ready


def claim(ctx: "Context", user_id: str, quest_id: str) -> dict[str, Any] | None:
    """If the named quest is completed-and-unclaimed, mark it claimed and
    return the QuestTemplate's reward bundle. Otherwise returns None.
    """
    state = load(ctx, user_id)
    for bucket in ("daily", "weekly"):
        for q in state.get(bucket, []) or []:
            if q.get("id") != quest_id:
                continue
            if q.get("claimed"):
                return None
            if int(q.get("progress", 0)) < int(q.get("target", 1)):
                return None
            t = quests_data.by_id(quest_id)
            if not t:
                return None
            q["claimed"] = True
            save(ctx, user_id, state)
            return {
                "id": t.id,
                "name": t.name,
                "coins": t.reward_coins,
                "xp": t.reward_xp,
                "polish": t.reward_polish,
            }
    return None
