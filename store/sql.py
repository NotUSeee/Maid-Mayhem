"""Sandboxed SQL wrappers + schema install.

Schema bootstrap: the host's `on_install` lifecycle signal is not reliably
fired for marketplace installs on this platform (verified by grepping
`core/` — nothing posts to plugin_runner /v1/lifecycle). So we ALSO call
``ensure_schema`` from ``on_ready`` and guard it with a KV flag — first
boot per server creates tables, subsequent boots skip the DDL entirely.

This keeps us well inside the host's 5-DDL/hour cap: the flag is set
once and persists, so the 4 CREATE statements run exactly once per
server install, not on every worker restart.

Bump SCHEMA_VERSION when adding or changing tables so the next boot
re-runs install (and budget the new DDL against the 5/hour cap).
"""
from __future__ import annotations

from typing import Any

from mmo_maid_sdk import Context

SCHEMA_VERSION = "v1"
_SCHEMA_FLAG_KEY = "mm:schema_installed"


_DDL_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS mm_inventory (
        user_id   TEXT NOT NULL,
        card_type TEXT NOT NULL,
        card_id   TEXT NOT NULL,
        count     INT  NOT NULL DEFAULT 1,
        level     INT  NOT NULL DEFAULT 1,
        xp        INT  NOT NULL DEFAULT 0,
        PRIMARY KEY (user_id, card_type, card_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS mm_battle_log (
        id       BIGSERIAL PRIMARY KEY,
        user_id  TEXT NOT NULL,
        result   TEXT NOT NULL,
        coins    INT  NOT NULL,
        xp       INT  NOT NULL,
        ended_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS mm_player_stats (
        user_id TEXT PRIMARY KEY,
        xp      INT NOT NULL DEFAULT 0,
        wins    INT NOT NULL DEFAULT 0,
        losses  INT NOT NULL DEFAULT 0
    )
    """,
    "CREATE INDEX IF NOT EXISTS mm_player_stats_xp_idx ON mm_player_stats (xp DESC)",
]


def install_schema(ctx: Context) -> None:
    """Run the 4 idempotent DDL statements. Safe to re-run on reinstall."""
    for stmt in _DDL_STATEMENTS:
        ctx.sql.execute(stmt)
    ctx.kv.set(_SCHEMA_FLAG_KEY, SCHEMA_VERSION)


def ensure_schema(ctx: Context) -> bool:
    """Run schema DDL if (and only if) it hasn't been installed at this version.

    Returns True if DDL was executed, False if it was skipped.

    Call this from BOTH on_install and on_ready — the KV flag prevents the
    DDL from running more than once per server install, so we don't burn
    the host's 5-statements-per-hour DDL budget on worker restarts.
    """
    if ctx.kv.get(_SCHEMA_FLAG_KEY) == SCHEMA_VERSION:
        return False
    install_schema(ctx)
    return True


# ── Inventory ───────────────────────────────────────────────────────────────

def grant_card(ctx: Context, user_id: str, card_type: str, card_id: str, qty: int = 1) -> None:
    """Add `qty` copies of a card to a user's inventory (UPSERT)."""
    ctx.sql.execute(
        """
        INSERT INTO mm_inventory (user_id, card_type, card_id, count)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id, card_type, card_id)
        DO UPDATE SET count = mm_inventory.count + EXCLUDED.count
        """,
        [user_id, card_type, card_id, qty],
    )


def get_inventory(ctx: Context, user_id: str) -> list[dict[str, Any]]:
    """Return all owned cards for a user, ordered for display."""
    return ctx.sql.query(
        """
        SELECT card_type, card_id, count, level, xp
        FROM mm_inventory
        WHERE user_id = %s
        ORDER BY card_type, card_id
        """,
        [user_id],
        limit=500,
    )


def owns_card(ctx: Context, user_id: str, card_type: str, card_id: str) -> bool:
    n = ctx.sql.scalar(
        "SELECT count FROM mm_inventory WHERE user_id=%s AND card_type=%s AND card_id=%s",
        [user_id, card_type, card_id],
    )
    return bool(n and int(n) > 0)


def consume_card(ctx: Context, user_id: str, card_type: str, card_id: str, qty: int) -> None:
    """Decrement ``count`` by ``qty``. Deletes the row if count hits zero.

    Used by fusion; assumes the caller already verified the user owns at
    least ``qty`` of this card.
    """
    if qty <= 0:
        return
    ctx.sql.execute(
        """
        UPDATE mm_inventory
        SET count = count - %s
        WHERE user_id = %s AND card_type = %s AND card_id = %s
        """,
        [int(qty), user_id, card_type, card_id],
    )
    ctx.sql.execute(
        """
        DELETE FROM mm_inventory
        WHERE user_id = %s AND card_type = %s AND card_id = %s AND count <= 0
        """,
        [user_id, card_type, card_id],
    )


# ── Player stats + battle log ───────────────────────────────────────────────

def record_battle(
    ctx: Context, user_id: str, *, result: str, coins: int, xp: int,
) -> None:
    """Append a battle_log row and bump mm_player_stats in one transaction."""
    ctx.sql.execute(
        "INSERT INTO mm_battle_log (user_id, result, coins, xp) VALUES (%s, %s, %s, %s)",
        [user_id, result, coins, xp],
    )
    won = 1 if result == "win" else 0
    lost = 1 if result == "loss" else 0
    ctx.sql.execute(
        """
        INSERT INTO mm_player_stats (user_id, xp, wins, losses)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE
        SET xp     = mm_player_stats.xp     + EXCLUDED.xp,
            wins   = mm_player_stats.wins   + EXCLUDED.wins,
            losses = mm_player_stats.losses + EXCLUDED.losses
        """,
        [user_id, xp, won, lost],
    )


def top_players(ctx: Context, limit: int = 25) -> list[dict[str, Any]]:
    return ctx.sql.query(
        "SELECT user_id, xp, wins, losses FROM mm_player_stats ORDER BY xp DESC LIMIT %s",
        [int(limit)],
    )
