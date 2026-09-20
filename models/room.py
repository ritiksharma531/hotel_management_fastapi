from sqlalchemy import Column, Integer, Enum, ForeignKey
from database.database import Base


class Room(Base):
    __tablename__ = 'rooms'

    room_id = Column(Integer, primary_key=True, index=True)
    room_type = Column(Enum("regular", "premium", name="room_type_enum"))
    price = Column(Integer)
    hid = Column(Integer, ForeignKey("hotels.hid"))