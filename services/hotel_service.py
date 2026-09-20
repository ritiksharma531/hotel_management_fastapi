from exceptions.exceptions import ForbiddenException, UnauthenticatedException
from logs.logger import logger
from models.hotel import Hotel
from schemas.hotel import AddHotelRequest


class HotelService:
    def __init__(self, hotel_repository):
        self.hotel_repository = hotel_repository

    async def add_hotel(self, user: dict, add_hotel_request: AddHotelRequest):
        if user is None:
            raise UnauthenticatedException('Register or Login first')
        if user.get('role') != 'admin':
            raise ForbiddenException('Only admin can add hotels')

        hotel_model = Hotel(
            hname=add_hotel_request.hname,
            rating=add_hotel_request.rating
        )
        result = await self.hotel_repository.add_hotel(hotel_model)
        logger.info(f'User with id {user.get('uid')} added a hotel')
        return result


    async def view_all_hotels(self, user: dict):
        if user is None:
            raise UnauthenticatedException('Register or Login first')
        result = await self.hotel_repository.get_hotels()
        logger.info(f'User with id {user.get('uid')} viewed all hotels')
        return result