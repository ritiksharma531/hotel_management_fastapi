import pytest
from datetime import date
from unittest.mock import AsyncMock, Mock
from models.hotel import Hotel
from models.room import Room
from repositories.hotel_repository import HotelRepository


class TestHotelRepository:
    def setup_method(self):
        self.db = AsyncMock()
        self.repo = HotelRepository(self.db)

    @pytest.mark.asyncio
    async def test_is_hotel_available(self):
        hotel = Hotel(hid=1, hname="Taj Palace", rating=5)
        result = Mock()
        result.scalars.return_value.all.return_value = [hotel]
        self.db.execute.return_value = result

        response = await self.repo.is_hotel_available(1)

        assert response == [hotel]
        self.db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_add_hotel(self):
        hotel = Hotel(hname="Taj Palace", rating=5)

        response = await self.repo.add_hotel(hotel)

        self.db.add.assert_called_once_with(hotel)
        self.db.commit.assert_awaited_once()
        self.db.refresh.assert_awaited_once_with(hotel)
        assert response == hotel

    @pytest.mark.asyncio
    async def test_get_hotels(self):
        hotels = [
            Hotel(hid=1, hname="Taj Palace", rating=5),
            Hotel(hid=2, hname="Oberoi", rating=4),
        ]
        result = Mock()
        result.scalars.return_value.all.return_value = hotels
        self.db.execute.return_value = result

        response = await self.repo.get_hotels()

        assert response == hotels
        self.db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_available_rooms(self):
        rooms = [
            Room(room_id=1, room_type="regular", price=1500, hid=1),
            Room(room_id=2, room_type="premium", price=3000, hid=1),
        ]
        result = Mock()
        result.scalars.return_value.all.return_value = rooms
        self.db.execute.return_value = result

        response = await self.repo.get_available_rooms(1, date(2026, 9, 18), date(2026, 9, 19))

        assert response == rooms
        self.db.execute.assert_awaited_once()