import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import BigInteger, ForeignKeyConstraint, Integer, String, create_engine
from sqlalchemy.orm import Mapped, Session, declarative_base, mapped_column, sessionmaker
from sqlalchemy.pool import NullPool

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL, poolclass=NullPool, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)

    emeralds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    trading_hall_level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    last_roll_at: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_claim_at: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_focus_roll_at: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_reroll_at: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_daily_at: Mapped[int | None] = mapped_column(Integer, nullable=True)


class Collection(Base):
    __tablename__ = "collections"

    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    mob_id: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)

    amount: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (
        ForeignKeyConstraint(
            ["guild_id", "user_id"],
            ["users.guild_id", "users.user_id"],
            ondelete="CASCADE",
        ),
    )


class Inventory(Base):
    __tablename__ = "inventory"

    guild_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    item_id: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)

    amount: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (
        ForeignKeyConstraint(
            ["guild_id", "user_id"],
            ["users.guild_id", "users.user_id"],
            ondelete="CASCADE",
        ),
    )


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Context manager for database sessions."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)
