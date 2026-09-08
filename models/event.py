from .base import Base
from sqlalchemy import DateTime, ForeignKey, String, Enum, text, Table, Column, Integer, Boolean, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING
from .game import GameType
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime, time
from enum import Enum as PythonEnum

if TYPE_CHECKING:
    from .user import User
    from .game import Game
    from .group import Group

class RecurrenceType(str, PythonEnum):
    daily = 'daily'
    weekly = 'weekly'
    monthly = 'monthly'

class StatusType(str, PythonEnum):
    confirmed = 'confirmed'
    cancelled = 'cancelled'

class Event(Base):
    __tablename__ = 'events'
    __table_args__ = ()
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    desc: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(1000))
    recurring: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    recurrence_rule: Mapped[RecurrenceType] = mapped_column(Enum(RecurrenceType, name="recurrencetype_enum"), nullable=True)
    date: Mapped[datetime] = mapped_column(
        DateTime)
    end_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    group: Mapped["Group"] = relationship("Group", backref='events')
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    status: Mapped[Optional[StatusType]] = mapped_column(Enum(StatusType, name='statustype_enum'), nullable=True)

class RspvStatus(str, PythonEnum):
    pending = 'pending'
    confirmed = 'confirmed'
    declined = 'declined'
    maybe = 'maybe'

class EventParticipant(Base):
    __tablename__ = 'event_participants'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=True)
    status: Mapped[RspvStatus] = mapped_column(
        Enum(
            RspvStatus, 
            name="rspvstatus_enum", 
            values_callable=lambda x: [e.value for e in x]
        ), 
        nullable=False, 
        default=RspvStatus.pending
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    event = relationship("Event", backref="participants")
    user = relationship("User", backref="event_responses")

