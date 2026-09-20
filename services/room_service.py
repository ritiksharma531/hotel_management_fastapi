from exceptions.exceptions import UnauthenticatedException, NotFoundException, ForbiddenException, ConflictException
from logs.logger import logger
from models import Room
from repositories.room_repository import RoomRepository
from repositories.hotel_repository import HotelRepository
from schemas.hotel import GetAvailabilityRequest
from schemas.room import AddRoomRequest


class RoomService:
    def __init__(self, room_repository: RoomRepository, hotel_repository: HotelRepository):
        self.room_repository = room_repository
        self.hotel_repository = hotel_repository

    async def is_hotel_available(self, hid: int):
        return await self.hotel_repository.is_hotel_available(hid)

    async def get_available_rooms(self, request: GetAvailabilityRequest, user:dict):
        if user is None:
            raise UnauthenticatedException('Register or Login first')
        if not await self.hotel_repository.is_hotel_available(request.hid):
            raise NotFoundException('Hotel not found')

        rooms = await self.hotel_repository.get_available_rooms(request.hid, request.check_in_date, request.check_out_date)
        logger.info(f'User with id {user.get('uid')} viewed room availability')
        return rooms

    async def add_room(self, new_room: AddRoomRequest, user: dict):
        if user is None:
            raise UnauthenticatedException('Register or Login first')

        if user.get('role') != 'admin':
            raise ForbiddenException('Only admin allowed')

        if not await self.is_hotel_available(new_room.hid):
            raise NotFoundException('Hotel not found')

        new_room_model = Room(
            room_type = new_room.room_type,
            price = new_room.price,
            hid = new_room.hid
        )

        result = await self.room_repository.add_room(new_room_model)
        logger.info(f'User with id {user.get('uid')} added room')
        return result