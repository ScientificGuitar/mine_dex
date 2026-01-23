from datetime import datetime, timezone


class User:
    def ensure_user(conn, guild_id: int, user_id: int) -> None:
        with conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO users (guild_id, user_id)
                VALUES (?, ?)
                """,
                (guild_id, user_id),
            )

    def has_claimed_today(conn, guild_id: int, user_id: int, now_ts: int) -> bool:
        with conn:
            row = conn.execute(
                """
                SELECT last_claim_at
                FROM users
                WHERE guild_id = ? AND user_id = ?
                """,
                (guild_id, user_id),
            ).fetchone()

            if row is None or row["last_claim_at"] is None:
                return False

            return same_utc_day(row["last_claim_at"], now_ts)

    def has_rerolled_today(conn, guild_id: int, user_id: int, now_ts: int) -> bool:
        with conn:
            row = conn.execute(
                """
                SELECT last_reroll_at
                FROM users
                WHERE guild_id = ? AND user_id = ?
                """,
                (guild_id, user_id),
            ).fetchone()

            if row is None or row["last_reroll_at"] is None:
                return False

            return same_utc_day(row["last_reroll_at"], now_ts)

    def has_focus_rolled_today(conn, guild_id: int, user_id: int, now_ts: int) -> bool:
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

    def get_roll_cooldown(conn, guild_id, user_id, now_ts):
        with conn:
            row = conn.execute(
                """
                SELECT last_roll_at
                FROM users
                WHERE guild_id = ? AND user_id = ?
                """,
                (guild_id, user_id),
            ).fetchone()

        if row is None or row["last_roll_at"] is None:
            return 0

        elapsed = now_ts - row["last_roll_at"]
        return max(0, 3600 - elapsed)

    def record_roll(conn, guild_id, user_id, now_ts):
        with conn:
            conn.execute(
                """
                UPDATE users
                SET last_roll_at = ?
                WHERE guild_id = ? AND user_id = ?
                """,
                (now_ts, guild_id, user_id),
            )

    def record_reroll(conn, guild_id, user_id, now_ts):
        with conn:
            conn.execute(
                """
                UPDATE users
                SET last_reroll_at = ?
                WHERE guild_id = ? AND user_id = ?
                """,
                (now_ts, guild_id, user_id),
            )

    def record_focus_roll(conn, guild_id, user_id, now_ts):
        with conn:
            conn.execute(
                """
                UPDATE users
                SET last_focus_roll_at = ?
                WHERE guild_id = ? AND user_id = ?
                """,
                (now_ts, guild_id, user_id),
            )

    def update_last_claim_at(conn, guild_id: int, user_id: int, timestamp: int) -> None:
        with conn:
            conn.execute(
                """
                UPDATE users
                SET last_claim_at = ?
                WHERE guild_id = ? AND user_id = ?
                """,
                (timestamp, guild_id, user_id),
            )

    def add_emeralds(conn, guild_id: int, user_id: int, amount: int) -> None:
        with conn:
            conn.execute(
                """
                UPDATE users
                SET emeralds = emeralds + ?
                WHERE guild_id = ? AND user_id = ?
                """,
                (amount, guild_id, user_id),
            )

    def get_emeralds(conn, guild_id: int, user_id: int) -> None:
        with conn:
            return conn.execute(
                """
                SELECT emeralds
                FROM users
                WHERE guild_id = ? AND user_id = ?
                """,
                (guild_id, user_id),
            ).fetchone()


def same_utc_day(ts1: int, ts2: int) -> bool:
    d1 = datetime.fromtimestamp(ts1, tz=timezone.utc).date()
    d2 = datetime.fromtimestamp(ts2, tz=timezone.utc).date()
    return d1 == d2
