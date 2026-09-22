from sqlalchemy import select, exists

from models import Booking
from models.room import Room
from schemas.room import BookRoomRequest


class RoomRepository:

    def __init__(self, db):
        self.db = db

    async def add_room(self, room: Room):
        self.db.add(room)
        await self.db.commit()
        return room

    async def is_room_available(self, room: BookRoomRequest):
        query = (
            select(Room)
            .where(Room.room_id == room.room_id)
            .where(
                ~exists(
                    select(1)
                    .where(Booking.room_id == Room.room_id)
                    .where(Booking.status.in_(["booked", "checked_in"]))
                    .where(Booking.check_in_date < room.check_out_date)
                    .where(Booking.check_out_date > room.check_in_date)
                )
            ).with_for_update()
        )
        result = await self.db.execute(query)
        return result.scalar()