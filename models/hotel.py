from sqlalchemy import Column, Integer, String, CheckConstraint, Float
from database.database import Base


class Hotel(Base):
    __tablename__ = 'hotels'

    hid = Column(Integer, primary_key=True, index=True)
    hname = Column(String)
    rating = Column(Float, CheckConstraint("rating >= 1 and rating <= 5"))