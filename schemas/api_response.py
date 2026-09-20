from typing import Any

from pydantic import BaseModel


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Any = None
    errors: Any = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str