-- Maid & Mayhem schema. Run once from on_install.
-- Total: 4 DDL statements (host caps DDL at 5/hour, so 1 statement headroom).
-- Tables are namespaced per Discord server by the host's SQL sandbox.

CREATE TABLE IF NOT EXISTS mm_inventory (
    user_id      TEXT NOT NULL,
    card_type    TEXT NOT NULL,        -- 'maid' | 'tool'
    card_id      TEXT NOT NULL,
    count        INT  NOT NULL DEFAULT 1,
    level        INT  NOT NULL DEFAULT 1,
    xp           INT  NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, card_type, card_id)
);

CREATE TABLE IF NOT EXISTS mm_battle_log (
    id           BIGSERIAL PRIMARY KEY,
    user_id      TEXT NOT NULL,
    result       TEXT NOT NULL,        -- 'win' | 'loss' | 'flee'
    coins        INT  NOT NULL,
    xp           INT  NOT NULL,
    ended_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mm_player_stats (
    user_id TEXT PRIMARY KEY,
    xp      INT NOT NULL DEFAULT 0,
    wins    INT NOT NULL DEFAULT 0,
    losses  INT NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS mm_player_stats_xp_idx ON mm_player_stats (xp DESC);
