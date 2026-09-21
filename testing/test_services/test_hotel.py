from datetime import date
from unittest.mock import AsyncMock

import pytest

from exceptions.exceptions import ForbiddenException, UnauthenticatedException, NotFoundException
from models import Hotel, Room
from schemas.hotel import AddHotelRequest, GetAvailabilityRequest
from services.hotel_service import HotelService


class TestHotel:
    def setup_method(self):
        self.user = {'email': 'temp@gmail.com', 'uid': 1, 'role': 'user'}
        self.admin = {'email': 'temp@gmail.com', 'uid': 1, 'role': 'admin'}
        self.hotel_repository = AsyncMock()
        self.hotel_service = HotelService(self.hotel_repository)

    @pytest.mark.asyncio
    async def test_add_hotel(self):
        add_hotel_request = AddHotelRequest(hname='Taj', rating=5)
        result = Hotel(hid=1, hname='Taj', rating=5)
        self.hotel_repository.add_hotel.return_value = result

        response = await self.hotel_service.add_hotel(self.admin, add_hotel_request)

        assert response.hid == 1
        assert response.hname == 'Taj'
        assert response.rating == 5

    @pytest.mark.asyncio
    async def test_view_all_hotels(self):
        result = [
            Hotel(hid=1, hname='Taj', rating=5),
            Hotel(hid=2, hname='Oberoi', rating=4)
        ]
        self.hotel_repository.get_hotels.return_value = result

        response = await self.hotel_service.view_all_hotels(self.user)

        assert response[0].hid == 1
        assert response[0].hname == 'Taj'
        assert response[1].hid == 2
        assert response[1].hname == 'Oberoi'

    @pytest.mark.asyncio
    async def test_add_hotel_unauthenticated(self):
        add_hotel_request = AddHotelRequest(hname='Taj', rating=5)
        with pytest.raises(UnauthenticatedException):
            await self.hotel_service.add_hotel(None, add_hotel_request)

    @pytest.mark.asyncio
    async def test_add_hotel_forbidden_for_user(self):
        add_hotel_request = AddHotelRequest(hname='Taj', rating=5)
        with pytest.raises(ForbiddenException):
            await self.hotel_service.add_hotel(self.user, add_hotel_request)

    @pytest.mark.asyncio
    async def test_view_all_hotels_unauthenticated(self):
        with pytest.raises(UnauthenticatedException):
            await self.hotel_service.view_all_hotels(None)

    @pytest.mark.asyncio
    async def test_get_available_rooms(self):
        availability_request = GetAvailabilityRequest(
            check_in_date=date(2026, 11, 18), check_out_date=date(2026, 11, 19)
        )
        result = [
            Room(room_id=1, room_type='regular', price=1000, hid=1)
        ]
        self.hotel_repository.is_hotel_available.return_value = True
        self.hotel_repository.get_available_rooms.return_value = result

        response = await self.hotel_service.get_available_rooms(1, availability_request, self.user)

        assert response[0].room_id == 1
        assert response[0].room_type == 'regular'
        assert response[0].price == 1000

    @pytest.mark.asyncio
    async def test_get_available_rooms_unauthenticated(self):
        availability_request = GetAvailabilityRequest(
            check_in_date=date(2026, 11, 18), check_out_date=date(2026, 11, 19)
        )
        with pytest.raises(UnauthenticatedException):
            await self.hotel_service.get_available_rooms(1, availability_request, None)

    @pytest.mark.asyncio
    async def test_get_available_rooms_hotel_not_found(self):
        availability_request = GetAvailabilityRequest(
            check_in_date=date(2026, 11, 18), check_out_date=date(2026, 11, 19)
        )
        self.hotel_repository.is_hotel_available.return_value = False

        with pytest.raises(NotFoundException):
            await self.hotel_service.get_available_rooms(1, availability_request, self.user)