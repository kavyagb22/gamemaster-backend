from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Table, text, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING
from enum import Enum as PythonEnum
from sqlalchemy.dialects.postgresql import ARRAY
from .base import Base

if TYPE_CHECKING:
    from .user import User


class GameType(str, PythonEnum):
    cooperative = "cooperative"
    strategic = "strategic"
    party = "party"
    deduction = "deduction"
    deckbuilder = 'deckbuilder'
    filler = 'filler'
    other = 'other'


class Game(Base):
    __tablename__ = "games"
    __table_args__ = (
        CheckConstraint("personal_rating >= 1 AND personal_rating <= 5",
                        name="check_personal_rating"),
        CheckConstraint("group_rating >= 1 AND group_rating <= 5",
                        name="check_group_rating"),
        CheckConstraint("complexity >= 1 AND complexity <= 5",
                        name="check_complexity"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    min_players: Mapped[int] = mapped_column()
    max_players: Mapped[int] = mapped_column()
    optimal_players: Mapped[Optional[int]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"))
    last_played: Mapped[Optional[datetime]] = mapped_column(DateTime,
                                                            nullable=True)
    gametype: Mapped[List[GameType]] = mapped_column(ARRAY(
        Enum(GameType, name="gametype_enum")),
                                                     nullable=False)
    personal_rating: Mapped[Optional[int]] = mapped_column(nullable=True)
    group_rating: Mapped[Optional[int]] = mapped_column(nullable=True)
    comments: Mapped[Optional[str]] = mapped_column(String(1000),
                                                    nullable=True)
    playtime: Mapped[int] = mapped_column()
    complexity: Mapped[int] = mapped_column()
    owner_username: Mapped[str] = mapped_column(String(100),
                                                ForeignKey("users.username",
                                                           ondelete="CASCADE"),
                                                nullable=False)
    owner: Mapped["User"] = relationship("User", back_populates="owned_games")
