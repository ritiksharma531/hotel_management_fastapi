from exceptions.exceptions import UnauthenticatedException, NotFoundException, ForbiddenException, ConflictException
from logs.logger import logger
from models import Room
from repositories.room_repository import RoomRepository
from repositories.hotel_repository import HotelRepository
from schemas.room import AddRoomRequest


class RoomService:
    def __init__(self, room_repository: RoomRepository, hotel_repository: HotelRepository):
        self.room_repository = room_repository
        self.hotel_repository = hotel_repository

    async def is_hotel_available(self, hid: int):
        return await self.hotel_repository.is_hotel_available(hid)

    async def add_room(self, hid: int, new_room: AddRoomRequest, user: dict):
        if user.get('role') != 'admin':
            logger.error(f'User with id {user.get('uid')} tried to add room')
            raise ForbiddenException('Only admin allowed')

        if not await self.is_hotel_available(hid):
            logger.error('admin tried to add room but hotel not found')
            raise NotFoundException('Hotel not found')

        new_room_model = Room(
            room_type = new_room.room_type,
            price = new_room.price,
            hid = hid
        )

        result = await self.room_repository.add_room(new_room_model)
        logger.info(f'User with id {user.get('uid')} added room')
        return result