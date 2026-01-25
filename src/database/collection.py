from sqlite3 import Connection
from typing import Any


class Collection:
    def add_to_collection(conn: Connection, guild_id: int, user_id: int, mob_id: str) -> None:
        with conn:
            conn.execute(
                """
                INSERT INTO collections (guild_id, user_id, mob_id, amount)
                VALUES (?, ?, ?, 1)
                ON CONFLICT(guild_id, user_id, mob_id)
                DO UPDATE SET amount = amount + 1
                """,
                (guild_id, user_id, mob_id),
            )

    def get_collection(conn: Connection, guild_id: int, user_id: int) -> list[Any]:
        with conn:
            return conn.execute(
                """
                SELECT mob_id, amount
                FROM collections
                WHERE guild_id = ? AND user_id = ?
                """,
                (guild_id, user_id),
            ).fetchall()

    def get_mob_count(conn: Connection, guild_id: int, user_id: int, mob_id: str) -> tuple:
        with conn:
            return conn.execute(
                """
                SELECT amount
                FROM collections
                WHERE guild_id = ? AND user_id = ? AND mob_id = ?
                """,
                (guild_id, user_id, mob_id),
            ).fetchone()

    def remove_mob(conn: Connection, guild_id: int, user_id: int, mob_id, amount: str) -> None:
        with conn:
            conn.execute(
                """
                UPDATE collections
                SET amount = amount - ?
                WHERE guild_id = ? AND user_id = ? AND mob_id = ?
                """,
                (amount, guild_id, user_id, mob_id),
            )