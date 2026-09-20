from pydantic import BaseModel


class ErrorResponse(BaseModel):
    code: int
    details: list