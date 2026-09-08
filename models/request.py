from pydantic import BaseModel, EmailStr
from typing import Optional, List, TYPE_CHECKING
from .game import GameType
from datetime import datetime, time, date as DateType
from .event import RecurrenceType, StatusType, RspvStatus

if TYPE_CHECKING:
    from .user import User
    from .game import Game


class SigninRequest(BaseModel):
    username: str
    password: str


class SignupRequest(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    password: str
    username: str
    email: EmailStr


class AddGameRequest(BaseModel):
    name: str
    min_players: int
    max_players: int
    optimal_players: Optional[int] = None
    gametype: List[GameType]
    last_played: Optional[datetime] = None
    personal_rating: Optional[int] = None
    group_rating: Optional[int] = None
    comments: Optional[str] = None
    owner: str
    playtime: int
    complexity: int


class DeleteGameRequest(BaseModel):
    game_id: int


class UpdateGameRequest(BaseModel):
    game_id: int
    name: str
    min_players: int
    max_players: int
    optimal_players: Optional[int] = None
    gametype: List[GameType]
    last_played: Optional[datetime] = None
    personal_rating: Optional[int] = None
    group_rating: Optional[int] = None
    comments: Optional[str] = None
    playtime: int
    complexity: int


class UpdateGroupRequest(BaseModel):
    group_id: int
    name: str
    desc: Optional[str] = None
    preferred_location: Optional[str] = None
    schedule: Optional[str] = None
    gametype: List[GameType]
    last_played: Optional[datetime] = None


class CreateGroupRequest(BaseModel):
    name: str
    host: str
    desc: Optional[str] = None
    invite_code: str
    preferred_location: Optional[str] = None
    schedule: Optional[str] = None
    gametype: List[GameType]
    last_played: Optional[datetime] = None


class DeleteGroupRequest(BaseModel):
    group_id: int


class JoinGroupRequest(BaseModel):
    username: str
    invite_code: str
    group_name: str


class ConvertUserRequest(BaseModel):
    username: str

class CreateEventRequest(BaseModel):
    name: str
    location: str
    date: DateType
    start_time: time
    end_time: time
    group_id: int
    desc: Optional[str] = None
    recurring: Optional[bool] = False
    recurrence_rule: Optional[RecurrenceType] = None  
    end_date: Optional[DateType] = None
    status: Optional[StatusType] = None

class UpdateRspvRequest(BaseModel):
    event_id: int
    user_id: int
    status: RspvStatus