from datetime import date
from typing import Literal

from pydantic import BaseModel


class BookingResponse(BaseModel):

    bid: int
    uid: int
    room_id: int
    booking_date: date
    check_in_date: date
    check_out_date: date
    status: str

    model_config = {"from_attributes": True}

class BookingStatus(BaseModel):
    status: Literal['checked_in', 'completed', 'cancelled']