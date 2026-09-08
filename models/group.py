from .base import Base
from sqlalchemy import DateTime, ForeignKey, String, Enum, text, Table, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING
from .game import GameType
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime

if TYPE_CHECKING:
    from .user import User
    from .game import Game
    from .event import Event

group_members = Table(
    "group_members", Base.metadata,
    Column("group_id",
           Integer,
           ForeignKey("groups.id", ondelete="CASCADE"),
           primary_key=True),
    Column("user_id",
           Integer,
           ForeignKey("users.id", ondelete="CASCADE"),
           primary_key=True),
    Column("joined_at", DateTime, server_default=text("CURRENT_TIMESTAMP")))

group_games = Table(
    "group_games", Base.metadata,
    Column("group_id",
           Integer,
           ForeignKey("groups.id", ondelete="CASCADE"),
           primary_key=True),
    Column("game_id",
           Integer,
           ForeignKey("games.id", ondelete="CASCADE"),
           primary_key=True),
    Column("added_at", DateTime, server_default=text("CURRENT_TIMESTAMP")))


class Group(Base):
    __tablename__ = 'groups'
    __table_args__ = ()
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    desc: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    invite_code: Mapped[str] = mapped_column(String(100), unique=True)
    preferred_location: Mapped[Optional[str]] = mapped_column(String(1000),
                                                              nullable=True)
    schedule: Mapped[Optional[str]] = mapped_column(String(1000),
                                                    nullable=True)
    gametype: Mapped[List[GameType]] = mapped_column(ARRAY(
        Enum(GameType, name="gametype_enum")),
                                                     nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"))
    last_played: Mapped[Optional[datetime]] = mapped_column(DateTime,
                                                            nullable=True)
    host: Mapped[str] = mapped_column(String(100),
                                      ForeignKey("users.username",
                                                 ondelete="CASCADE"),
                                      nullable=False)
    members: Mapped[List["User"]] = relationship("User",
                                                 secondary=group_members,
                                                 backref="groups")
    library: Mapped[List["Game"]] = relationship("Game",
                                                 secondary=group_games,
                                                 backref="groups")
