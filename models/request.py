from pydantic import BaseModel, EmailStr
from typing import Optional, List
from .game import GameType
from datetime import datetime


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