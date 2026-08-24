from pydantic import BaseModel, EmailStr
from typing import Optional


class SigninRequest(BaseModel):
    username: str
    password: str


class SignupRequest(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    password: str
    username: str
    email: EmailStr
