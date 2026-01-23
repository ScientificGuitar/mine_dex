import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "minedex.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        guild_id            INTEGER NOT NULL,
        user_id             INTEGER NOT NULL,

        emeralds            INTEGER NOT NULL DEFAULT 0,

        last_roll_at        INTEGER,
        last_claim_at       INTEGER,
        last_focus_roll_at  INTEGER,
        last_reroll_at      INTEGER,

        PRIMARY KEY (guild_id, user_id)
    );

    CREATE TABLE IF NOT EXISTS collections (
        guild_id  INTEGER NOT NULL,
        user_id   INTEGER NOT NULL,
        mob_id    TEXT NOT NULL,
        amount  INTEGER NOT NULL DEFAULT 1,
        PRIMARY KEY (guild_id, user_id, mob_id),
        FOREIGN KEY (guild_id, user_id)
            REFERENCES users (guild_id, user_id)
            ON DELETE CASCADE
    );
                         
    CREATE TABLE IF NOT EXISTS villagers (
        guild_id        INTEGER NOT NULL,
        user_id         INTEGER NOT NULL,
        villager_type   TEXT NOT NULL,
        unlocked_at     INTEGER NOT NULL,

        PRIMARY KEY (guild_id, user_id, villager_type),

        FOREIGN KEY (guild_id, user_id)
            REFERENCES users (guild_id, user_id)
            ON DELETE CASCADE
    );
                         
    CREATE TABLE IF NOT EXISTS inventory (
        guild_id     INTEGER NOT NULL,
        user_id      INTEGER NOT NULL,
        item_id      TEXT NOT NULL,
        amount       INTEGER NOT NULL DEFAULT 0,

        PRIMARY KEY (guild_id, user_id, item_id),

        FOREIGN KEY (guild_id, user_id)
            REFERENCES users (guild_id, user_id)
            ON DELETE CASCADE
    );
    """)

    conn.commit()
