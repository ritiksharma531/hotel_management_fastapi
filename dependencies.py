from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings
from database.database import get_db
from exceptions.exceptions import UnauthenticatedException
from repositories.auth_repository import AuthRepository
from repositories.booking_repository import BookingRepository
from repositories.hotel_repository import HotelRepository
from repositories.room_repository import RoomRepository
from services.auth_service import AuthService
from services.booking_service import BookingService
from services.hotel_service import HotelService
from services.room_service import RoomService

db_dependency = Annotated[AsyncSession, Depends(get_db)]

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/login', auto_error=False)

def get_room_repository(db: db_dependency):
    return RoomRepository(db)

def get_hotel_repository(db: db_dependency):
    return HotelRepository(db)

def get_booking_repository(db: db_dependency):
    return BookingRepository(db)

def get_auth_repository(db: db_dependency):
    return AuthRepository(db)

def get_auth_service(auth_repository: AuthRepository = Depends(get_auth_repository)):
    auth_service = AuthService(auth_repository)
    return auth_service

def get_room_service(room_repository: RoomRepository = Depends(get_room_repository), hotel_repository: HotelRepository = Depends(get_hotel_repository)):
    room_service = RoomService(room_repository, hotel_repository)
    return room_service

def get_hotel_service(hotel_repository: HotelRepository = Depends(get_hotel_repository)):
    hotel_service = HotelService(hotel_repository)
    return hotel_service

def get_booking_service(room_repository: RoomRepository = Depends(get_room_repository), hotel_repository: HotelRepository = Depends(get_hotel_repository), booking_repository: BookingRepository = Depends(get_booking_repository)):
    booking_service = BookingService(booking_repository=booking_repository, hotel_repository=hotel_repository, room_repository=room_repository)
    return booking_service


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        if token is None:
            raise UnauthenticatedException('Register or Login first')
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email = payload.get('sub')
        user_id = payload.get('id')
        role = payload.get('role')
        if email is None or user_id is None:
            raise UnauthenticatedException('Register or Login first')
        return {'email': email, 'uid': user_id, 'role': role}
    except JWTError:
        raise UnauthenticatedException('Could not validate user')