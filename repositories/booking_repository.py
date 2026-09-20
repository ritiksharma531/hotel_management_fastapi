from sqlalchemy import select

from models import Booking
class BookingRepository:

    def __init__(self, db):
        self.db = db


    async def book_room(self, booking_model: Booking):
        self.db.add(booking_model)
        await self.db.commit()
        return booking_model

    async def get_booking(self, bid: int):
        result = await self.db.execute(select(Booking).where(Booking.bid == bid))
        return result.scalar_one_or_none()

    async def get_all_bookings(self):
        result = await self.db.execute(select(Booking))
        return result.scalars().all()

    async def get_my_bookings(self, uid: int):
        result = await self.db.execute(select(Booking).where(Booking.uid == uid))
        bookings = result.scalars().all()
        return bookings

    async def update_booking_status(self, booking: Booking, status: str):
        booking_model = booking
        booking_model.status = status

        await self.db.commit()
        return booking_model