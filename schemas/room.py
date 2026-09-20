from typing import Literal
from pydantic import BaseModel, Field, model_validator, field_validator
from datetime import date

class AddRoomRequest(BaseModel):
    room_type: str
    price: int = Field(gt=0, lt=50000)
    hid: int = Field(gt=-1)

    @field_validator('room_type')
    @classmethod
    def check_room_type(cls, value: str) -> str:
        if value.lower() in ['regular', 'premium']:
            return value.lower()
        raise ValueError('Allowed room types are regular and premium')

class BookRoomRequest(BaseModel):
    room_id: int = Field(gt=0)
    check_in_date: date
    check_out_date: date


    @model_validator(mode='after')
    def check_dates(self):
        if self.check_in_date < date.today():
            raise ValueError("past dates not allowed")
        if self.check_out_date < date.today():
            raise ValueError("past dates not allowed")
        if self.check_in_date>=self.check_out_date:
            raise ValueError("check in date must be less than check out date")
        return self

class AddRoomResponse(BaseModel):
    room_id: int
    room_type: Literal['regular', 'premium']
    price: int
    hid: int

    model_config = {"from_attributes": True}

class BaseBookingResponse(BaseModel):
    bid: int
    uid: int
    room_id: int
    booking_date: date
    check_in_date: date
    check_out_date: date
    status: str

    model_config = {"from_attributes": True}

class BookRoomResponse(BaseBookingResponse):
    price: int

class UpdateStatusResponse(BaseBookingResponse):
    pass


class RoomResponse(BaseModel):
    room_id: int
    room_type: str
    price: int
    hid: int

    model_config = {"from_attributes": True}