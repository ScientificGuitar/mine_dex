from datetime import datetime, timezone
from sqlite3 import Connection


class User:
    def ensure_user(conn: Connection, guild_id: int, user_id: int) -> None:
        with conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO users (guild_id, user_id)
                VALUES (?, ?)
                """,
                (guild_id, user_id),
            )

    def get_user(conn: Connection, guild_id: int, user_id: int) -> tuple:
        with conn:
            return conn.execute(
                """
                SELECT *
                FROM users
                WHERE guild_id = ? AND user_id = ?
                """,
                (guild_id, user_id),
            ).fetchone()

    def has_focus_rolled_today(conn: Connection, guild_id: int, user_id: int, now_ts: int) -> bool:
        with conn:
            row = conn.execute(
                """
                SELECT last_focus_roll_at
                FROM users
                WHERE guild_id = ? AND user_id = ?
                """,
                (guild_id, user_id),
            ).fetchone()

            if row is None or row["last_focus_roll_at"] is None:
                return False

            return same_utc_day(row["last_focus_roll_at"], now_ts)

    def record_roll(conn: Connection, guild_id, user_id, now_ts) -> None:
        with conn:
            conn.execute(
                """
                UPDATE users
                SET last_roll_at = ?
                WHERE guild_id = ? AND user_id = ?
                """,
                (now_ts, guild_id, user_id),
            )

    def record_reroll(conn: Connection, guild_id, user_id, now_ts) -> None:
        with conn:
            conn.execute(
                """
                UPDATE users
                SET last_reroll_at = ?
                WHERE guild_id = ? AND user_id = ?
                """,
                (now_ts, guild_id, user_id),
            )

    def record_focus_roll(conn: Connection, guild_id, user_id, now_ts) -> None:
        with conn:
            conn.execute(
                """
                UPDATE users
                SET last_focus_roll_at = ?
                WHERE guild_id = ? AND user_id = ?
                """,
                (now_ts, guild_id, user_id),
            )

    def update_last_claim_at(conn: Connection, guild_id: int, user_id: int, timestamp: int) -> None:
        with conn:
            conn.execute(
                """
                UPDATE users
                SET last_claim_at = ?
                WHERE guild_id = ? AND user_id = ?
                """,
                (timestamp, guild_id, user_id),
            )

    def update_last_daily_at(conn: Connection, guild_id: int, user_id: int, timestamp: int) -> None:
        with conn:
            conn.execute(
                """
                UPDATE users
                SET last_daily_at = ?
                WHERE guild_id = ? AND user_id = ?
                """,
                (timestamp, guild_id, user_id),
            )

    def add_emeralds(conn: Connection, guild_id: int, user_id: int, amount: int) -> None:
        with conn:
            conn.execute(
                """
                UPDATE users
                SET emeralds = emeralds + ?
                WHERE guild_id = ? AND user_id = ?
                """,
                (amount, guild_id, user_id),
            )

    def get_emeralds(conn: Connection, guild_id: int, user_id: int) -> tuple | None:
        with conn:
            return conn.execute(
                """
                SELECT emeralds
                FROM users
                WHERE guild_id = ? AND user_id = ?
                """,
                (guild_id, user_id),
            ).fetchone()

    def get_trading_hall_level(conn: Connection, guild_id: int, user_id: int) -> tuple | None:
        with conn:
            return conn.execute(
                """
                SELECT trading_hall_level
                FROM users
                WHERE guild_id = ? AND user_id = ?
                """,
                (guild_id, user_id),
            ).fetchone()

    def upgrade_trading_hall(conn: Connection, guild_id: int, user_id: int) -> None:
        with conn:
            conn.execute(
                """
                UPDATE users
                SET trading_hall_level = trading_hall_level + 1
                WHERE guild_id = ? AND user_id = ?
                """,
                (guild_id, user_id),
            )


def same_utc_day(ts1: int, ts2: int) -> bool:
    d1 = datetime.fromtimestamp(ts1, tz=timezone.utc).date()
    d2 = datetime.fromtimestamp(ts2, tz=timezone.utc).date()
    return d1 == d2
