from datetime import datetime, timezone

from .db import User as UserModel


class User:
    @staticmethod
    def ensure_user(session_factory, guild_id: int, user_id: int) -> None:
        """Ensure a user exists in the database, creating if necessary."""
        with session_factory() as session:
            user = session.query(UserModel).filter_by(guild_id=guild_id, user_id=user_id).first()
            if not user:
                user = UserModel(guild_id=guild_id, user_id=user_id)
                session.add(user)
                session.commit()

    @staticmethod
    def get_user(session_factory, guild_id: int, user_id: int) -> UserModel | None:
        """Get a user by guild_id and user_id."""
        with session_factory() as session:
            return session.query(UserModel).filter_by(guild_id=guild_id, user_id=user_id).first()

    @staticmethod
    def has_focus_rolled_today(session_factory, guild_id: int, user_id: int, now_ts: int) -> bool:
        """Check if user has already focus rolled today."""
        with session_factory() as session:
            user = session.query(UserModel).filter_by(guild_id=guild_id, user_id=user_id).first()

            if user is None or user.last_focus_roll_at is None:
                return False

            return same_utc_day(user.last_focus_roll_at, now_ts)

    @staticmethod
    def record_roll(session_factory, guild_id: int, user_id: int, now_ts: int) -> None:
        """Record a roll timestamp for the user."""
        with session_factory() as session:
            user = session.query(UserModel).filter_by(guild_id=guild_id, user_id=user_id).first()
            if user:
                user.last_roll_at = now_ts
                session.commit()

    @staticmethod
    def record_reroll(session_factory, guild_id: int, user_id: int, now_ts: int) -> None:
        """Record a reroll timestamp for the user."""
        with session_factory() as session:
            user = session.query(UserModel).filter_by(guild_id=guild_id, user_id=user_id).first()
            if user:
                user.last_reroll_at = now_ts
                session.commit()

    @staticmethod
    def record_focus_roll(session_factory, guild_id: int, user_id: int, now_ts: int) -> None:
        """Record a focus roll timestamp for the user."""
        with session_factory() as session:
            user = session.query(UserModel).filter_by(guild_id=guild_id, user_id=user_id).first()
            if user:
                user.last_focus_roll_at = now_ts
                session.commit()

    @staticmethod
    def update_last_claim_at(session_factory, guild_id: int, user_id: int, timestamp: int) -> None:
        """Update the last claim timestamp."""
        with session_factory() as session:
            user = session.query(UserModel).filter_by(guild_id=guild_id, user_id=user_id).first()
            if user:
                user.last_claim_at = timestamp
                session.commit()

    @staticmethod
    def update_last_daily_at(session_factory, guild_id: int, user_id: int, timestamp: int) -> None:
        """Update the last daily command timestamp."""
        with session_factory() as session:
            user = session.query(UserModel).filter_by(guild_id=guild_id, user_id=user_id).first()
            if user:
                user.last_daily_at = timestamp
                session.commit()

    @staticmethod
    def add_emeralds(session_factory, guild_id: int, user_id: int, amount: int) -> None:
        """Add emeralds to a user."""
        with session_factory() as session:
            user = session.query(UserModel).filter_by(guild_id=guild_id, user_id=user_id).first()
            if user:
                user.emeralds += amount
                session.commit()

    @staticmethod
    def get_emeralds(session_factory, guild_id: int, user_id: int) -> int | None:
        """Get the number of emeralds a user has."""
        with session_factory() as session:
            user = session.query(UserModel).filter_by(guild_id=guild_id, user_id=user_id).first()
            return user.emeralds if user else None

    @staticmethod
    def get_trading_hall_level(session_factory, guild_id: int, user_id: int) -> int | None:
        """Get the trading hall level for a user."""
        with session_factory() as session:
            user = session.query(UserModel).filter_by(guild_id=guild_id, user_id=user_id).first()
            return user.trading_hall_level if user else None

    @staticmethod
    def upgrade_trading_hall(session_factory, guild_id: int, user_id: int) -> None:
        """Upgrade a user's trading hall level."""
        with session_factory() as session:
            user = session.query(UserModel).filter_by(guild_id=guild_id, user_id=user_id).first()
            if user:
                user.trading_hall_level += 1
                session.commit()


def same_utc_day(ts1: int, ts2: int) -> bool:
    """Check if two timestamps are on the same UTC day."""
    d1 = datetime.fromtimestamp(ts1, tz=timezone.utc).date()
    d2 = datetime.fromtimestamp(ts2, tz=timezone.utc).date()
    return d1 == d2
