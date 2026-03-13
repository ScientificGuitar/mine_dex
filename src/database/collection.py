from typing import Any

from .db import Collection as CollectionModel


class Collection:
    @staticmethod
    def add_to_collection(session_factory, guild_id: int, user_id: int, mob_id: str) -> None:
        """Add a mob to a user's collection or increment its count."""
        with session_factory() as session:
            collection = (
                session.query(CollectionModel).filter_by(guild_id=guild_id, user_id=user_id, mob_id=mob_id).first()
            )

            if collection:
                collection.amount += 1
            else:
                collection = CollectionModel(guild_id=guild_id, user_id=user_id, mob_id=mob_id, amount=1)
                session.add(collection)

            session.commit()

    @staticmethod
    def get_collection(session_factory, guild_id: int, user_id: int) -> list[dict[str, Any]]:
        """Get all mobs in a user's collection."""
        with session_factory() as session:
            collections = (
                session.query(CollectionModel.mob_id, CollectionModel.amount)
                .filter_by(guild_id=guild_id, user_id=user_id)
                .all()
            )

            return [{"mob_id": c[0], "amount": c[1]} for c in collections]

    @staticmethod
    def get_mob_count(session_factory, guild_id: int, user_id: int, mob_id: str) -> int | None:
        """Get the count of a specific mob in a user's collection."""
        with session_factory() as session:
            collection = (
                session.query(CollectionModel).filter_by(guild_id=guild_id, user_id=user_id, mob_id=mob_id).first()
            )

            return collection.amount if collection else None

    @staticmethod
    def remove_mob(session_factory, guild_id: int, user_id: int, mob_id: str, amount: int) -> None:
        """Reduce the amount of a mob in a user's collection."""
        with session_factory() as session:
            collection = (
                session.query(CollectionModel).filter_by(guild_id=guild_id, user_id=user_id, mob_id=mob_id).first()
            )

            if collection:
                collection.amount -= amount
                session.commit()
