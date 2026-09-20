import re
from typing import Literal

from pydantic import BaseModel, Field, EmailStr, field_validator


class RegisterUserRequest(BaseModel):
    fullname: str = Field(min_length=3, max_length=20)
    email: EmailStr
    password: str
    role: Literal['user', 'admin'] = 'user'

    @field_validator('password')
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', value):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', value):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*]', value):
            raise ValueError('Password must contain at least one special character among !, @, #, $, %, ^, & and *')
        return value

class UserResponse(BaseModel):
    uid: int
    fullname: str
    email: EmailStr
    role: str

    model_config = {"from_attributes": True}