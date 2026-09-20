from datetime import date

from pydantic import BaseModel, Field, model_validator


class AddHotelRequest(BaseModel):
    hname: str = Field(min_length=2, max_length=30)
    rating: int = Field(gt=0, lt=6)


class GetAvailabilityRequest(BaseModel):
    hid: int
    check_in_date: date = date.today()
    check_out_date: date = date.today()

    @model_validator(mode='after')
    def check_dates(self):
        if self.check_in_date >= self.check_out_date:
            raise ValueError("check in date must be less than check out date")
        return self


class HotelResponse(BaseModel):
    hid: int
    hname: str
    rating: int

    model_config = {"from_attributes": True}
