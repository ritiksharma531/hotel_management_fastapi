from datetime import date

from sqlalchemy import select, exists

from models import Room, Booking
from models.hotel import Hotel


class HotelRepository:

    def __init__(self, db):
        self.db = db


    async def is_hotel_available(self, hid: int):
        result = await self.db.execute(select(Hotel).where(Hotel.hid == hid))
        return result.scalars().all()


    async def add_hotel(self, hotel: Hotel):
        self.db.add(hotel)
        await self.db.commit()
        await self.db.refresh(hotel)
        return hotel


    async def get_hotels(self):
        result = await self.db.execute(select(Hotel))
        return result.scalars().all()

    async def get_available_rooms(self, hid: int, check_in_date: date, check_out_date: date):
        query = (
            select(Room)
            .where(Room.hid == hid)
            .where(
                ~exists(
                    select(1)
                    .where(Booking.room_id == Room.room_id)
                    .where(Booking.status.in_(["booked", "checked_in"]))
                    .where(Booking.check_in_date < check_out_date)
                    .where(Booking.check_out_date > check_in_date)
                )
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()