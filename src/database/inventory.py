from sqlite3 import Connection


class Inventory:
    def get_item(conn: Connection, guild_id: int, user_id: int, item_id: str) -> tuple:
        with conn:
            return conn.execute(
                """
                SELECT *
                FROM inventory
                WHERE guild_id = ? AND user_id = ? AND item_id = ?
                """,
                (guild_id, user_id, item_id),
            ).fetchone()

    def add_to_inventory(conn: Connection, guild_id: int, user_id: int, item_id: str, amount: int) -> None:
        with conn:
            conn.execute(
                """
                INSERT INTO inventory (guild_id, user_id, item_id, amount)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(guild_id, user_id, item_id)
                DO UPDATE SET amount = amount + ?
                """,
                (guild_id, user_id, item_id, amount, amount),
            )
