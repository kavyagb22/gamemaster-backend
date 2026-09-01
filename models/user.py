from datetime import datetime
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Table, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING
from enum import Enum as PythonEnum

from .base import Base

if TYPE_CHECKING:
    from .game import Game


class UserType(str, PythonEnum):
    host = "host"
    player = "player"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    firstname: Mapped[Optional[str]] = mapped_column(String(100))
    lastname: Mapped[Optional[str]] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100),
                                       unique=True,
                                       nullable=False)
    password_hash: Mapped[str] = mapped_column(String(225), nullable=False)
    username: Mapped[str] = mapped_column(String(100),
                                          unique=True,
                                          nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP"))
    usertype: Mapped[UserType] = mapped_column(
        Enum(UserType, name="usertype_enum"),
        nullable=False,
        server_default=UserType.player.value)
    owned_games: Mapped[List["Game"]] = relationship("Game",
                                                     back_populates="owner")
