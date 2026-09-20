from datetime import date
from unittest.mock import AsyncMock

import pytest

from exceptions.exceptions import ForbiddenException, UnauthenticatedException, NotFoundException
from models import Room
from schemas.hotel import GetAvailabilityRequest
from schemas.room import AddRoomRequest
from services.room_service import RoomService


class TestRoom:
    def setup_method(self):
        self.user = {'email': 'temp@gmail.com', 'uid': 1, 'role': 'user'}
        self.admin = {'email': 'temp@gmail.com', 'uid': 1, 'role': 'admin'}
        self.room_repository = AsyncMock()
        self.hotel_repository = AsyncMock()
        self.room_service = RoomService(self.room_repository, self.hotel_repository)

    @pytest.mark.asyncio
    async def test_is_hotel_available(self):
        self.hotel_repository.is_hotel_available.return_value = True

        response = await self.room_service.is_hotel_available(1)

        assert response is True

    @pytest.mark.asyncio
    async def test_get_available_rooms(self):
        availability_request = GetAvailabilityRequest(
            hid=1, check_in_date=date(2026, 11, 18), check_out_date=date(2026, 11, 19)
        )
        result = [
            Room(room_id=1, room_type='regular', price=1000, hid=1)
        ]
        self.hotel_repository.is_hotel_available.return_value = True
        self.hotel_repository.get_available_rooms.return_value = result

        response = await self.room_service.get_available_rooms(availability_request, self.user)

        assert response[0].room_id == 1
        assert response[0].room_type == 'regular'
        assert response[0].price == 1000

    @pytest.mark.asyncio
    async def test_add_room(self):
        new_room = AddRoomRequest(room_type='regular', price=1000, hid=1)
        result = Room(room_id=1, room_type='regular', price=1000, hid=1)
        self.hotel_repository.is_hotel_available.return_value = True
        self.room_repository.add_room.return_value = result

        response = await self.room_service.add_room(new_room, self.admin)

        assert response.room_id == 1
        assert response.room_type == 'regular'
        assert response.hid == 1

    @pytest.mark.asyncio
    async def test_get_available_rooms_unauthenticated(self):
        availability_request = GetAvailabilityRequest(
            hid=1, check_in_date=date(2026, 11, 18), check_out_date=date(2026, 11, 19)
        )
        with pytest.raises(UnauthenticatedException):
            await self.room_service.get_available_rooms(availability_request, None)

    @pytest.mark.asyncio
    async def test_get_available_rooms_hotel_not_found(self):
        availability_request = GetAvailabilityRequest(
            hid=1, check_in_date=date(2026, 11, 18), check_out_date=date(2026, 11, 19)
        )
        self.hotel_repository.is_hotel_available.return_value = False

        with pytest.raises(NotFoundException):
            await self.room_service.get_available_rooms(availability_request, self.user)

    @pytest.mark.asyncio
    async def test_add_room_unauthenticated(self):
        new_room = AddRoomRequest(room_type='regular', price=1000, hid=1)
        with pytest.raises(UnauthenticatedException):
            await self.room_service.add_room(new_room, None)

    @pytest.mark.asyncio
    async def test_add_room_forbidden_for_user(self):
        new_room = AddRoomRequest(room_type='regular', price=1000, hid=1)
        with pytest.raises(ForbiddenException):
            await self.room_service.add_room(new_room, self.user)

    @pytest.mark.asyncio
    async def test_add_room_hotel_not_found(self):
        new_room = AddRoomRequest(room_type='regular', price=1000, hid=1)
        self.hotel_repository.is_hotel_available.return_value = False

        with pytest.raises(NotFoundException):
            await self.room_service.add_room(new_room, self.admin)