from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.db import Collection, Inventory, User

sqlite_engine = create_engine("sqlite:////app/data/minedex.db")
postgres_engine = create_engine("postgresql+psycopg://minedex:password@postgres:5432/minedex")

SqliteSession = sessionmaker(bind=sqlite_engine)
PostgresSession = sessionmaker(bind=postgres_engine)


def migrate_users():
    sqlite = SqliteSession()
    pg = PostgresSession()

    try:
        users = sqlite.query(User).all()

        for user in users:
            pg.merge(
                User(
                    guild_id=user.guild_id,
                    user_id=user.user_id,
                    emeralds=user.emeralds,
                    trading_hall_level=user.trading_hall_level,
                    last_roll_at=user.last_roll_at,
                    last_claim_at=user.last_claim_at,
                    last_focus_roll_at=user.last_focus_roll_at,
                    last_reroll_at=user.last_reroll_at,
                    last_daily_at=user.last_daily_at,
                )
            )

        pg.commit()

    finally:
        sqlite.close()
        pg.close()


def migrate_collections():
    sqlite = SqliteSession()
    pg = PostgresSession()

    try:
        rows = sqlite.query(Collection).all()

        for row in rows:
            pg.merge(
                Collection(
                    guild_id=row.guild_id,
                    user_id=row.user_id,
                    mob_id=row.mob_id,
                    amount=row.amount,
                )
            )

        pg.commit()

    finally:
        sqlite.close()
        pg.close()


def migrate_inventory():
    sqlite = SqliteSession()
    pg = PostgresSession()

    try:
        rows = sqlite.query(Inventory).all()

        for row in rows:
            pg.merge(
                Inventory(
                    guild_id=row.guild_id,
                    user_id=row.user_id,
                    item_id=row.item_id,
                    amount=row.amount,
                )
            )

        pg.commit()

    finally:
        sqlite.close()
        pg.close()


if __name__ == "__main__":
    migrate_users()
    migrate_collections()
    migrate_inventory()
