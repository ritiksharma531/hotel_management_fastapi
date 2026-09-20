from sqlalchemy import Column, Integer, String
from database.database import Base


class User(Base):
    __tablename__ = 'users'

    uid = Column(Integer, primary_key=True, index=True)
    fullname = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    role = Column(String)