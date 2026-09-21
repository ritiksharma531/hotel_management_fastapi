from exceptions.exceptions import ForbiddenException, UnauthenticatedException, NotFoundException
from logs.logger import logger
from models.hotel import Hotel
from schemas.hotel import AddHotelRequest, GetAvailabilityRequest


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

    async def get_available_rooms(self, hid, request: GetAvailabilityRequest, user:dict):
        if user is None:
            raise UnauthenticatedException('Register or Login first')
        if not await self.hotel_repository.is_hotel_available(hid):
            raise NotFoundException('Hotel not found')

        rooms = await self.hotel_repository.get_available_rooms(hid, request.check_in_date, request.check_out_date)
        logger.info(f'User with id {user.get('uid')} viewed room availability')
        return rooms