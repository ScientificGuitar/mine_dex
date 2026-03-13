from .db import Inventory as InventoryModel


class Inventory:
    @staticmethod
    def get_item(session_factory, guild_id: int, user_id: int, item_id: str) -> InventoryModel | None:
        """Get a specific item from a user's inventory."""
        with session_factory() as session:
            return session.query(InventoryModel).filter_by(guild_id=guild_id, user_id=user_id, item_id=item_id).first()

    @staticmethod
    def get_items(session_factory, guild_id: int, user_id: int) -> list[InventoryModel]:
        """Get all items in a user's inventory."""
        with session_factory() as session:
            return session.query(InventoryModel).filter_by(guild_id=guild_id, user_id=user_id).all()

    @staticmethod
    def add_to_inventory(session_factory, guild_id: int, user_id: int, item_id: str, amount: int) -> None:
        """Add items to a user's inventory or create if doesn't exist."""
        with session_factory() as session:
            inventory = (
                session.query(InventoryModel).filter_by(guild_id=guild_id, user_id=user_id, item_id=item_id).first()
            )

            if inventory:
                inventory.amount += amount
            else:
                inventory = InventoryModel(guild_id=guild_id, user_id=user_id, item_id=item_id, amount=amount)
                session.add(inventory)

            session.commit()
