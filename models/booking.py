from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from database.database import Base


class Booking(Base):
    __tablename__ = 'bookings'

    bid = Column(Integer, primary_key=True, index=True)
    uid = Column(Integer, ForeignKey("users.uid"))
    room_id = Column(Integer, ForeignKey("rooms.room_id"))
    booking_date = Column(DateTime)
    check_in_date = Column(DateTime)
    check_out_date = Column(DateTime)
    status = Column(Enum("booked", "checked_in", "cancelled", "completed", name="booking_type_enum"))
    price = Column(Integer)