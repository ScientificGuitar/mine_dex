class Collection:
    def add_to_collection(conn, guild_id: int, user_id: int, mob_id: str) -> None:
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

    def get_collection(conn, guild_id: int, user_id: int):
        with conn:
            return conn.execute(
                """
                SELECT mob_id, amount
                FROM collections
                WHERE guild_id = ? AND user_id = ?
                """,
                (guild_id, user_id),
            ).fetchall()
