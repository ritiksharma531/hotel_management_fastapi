import pytest
from unittest.mock import AsyncMock, Mock
from models.booking import Booking
from repositories.booking_repository import BookingRepository


class TestBookingRepository:
    def setup_method(self):
        self.db = AsyncMock()
        self.repo = BookingRepository(self.db)

    @pytest.mark.asyncio
    async def test_book_room(self):
        booking = Booking(uid=1, room_id=1, status="booked")

        response = await self.repo.book_room(booking)

        self.db.add.assert_called_once_with(booking)
        self.db.commit.assert_awaited_once()
        assert response == booking

    @pytest.mark.asyncio
    async def test_get_booking(self):
        booking = Booking(bid=1, uid=1, room_id=1, status="booked")
        result = Mock()
        result.scalar_one_or_none.return_value = booking
        self.db.execute.return_value = result

        response = await self.repo.get_booking(1)

        assert response == booking
        self.db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_all_bookings(self):
        bookings = [
            Booking(bid=1, uid=1, room_id=1, status="booked"),
            Booking(bid=2, uid=2, room_id=2, status="checked_in"),
        ]
        result = Mock()
        result.scalars.return_value.all.return_value = bookings
        self.db.execute.return_value = result

        response = await self.repo.get_all_bookings()

        assert response == bookings
        self.db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_my_bookings(self):
        bookings = [Booking(bid=1, uid=1, room_id=1, status="booked")]
        result = Mock()
        result.scalars.return_value.all.return_value = bookings
        self.db.execute.return_value = result

        response = await self.repo.get_my_bookings(1)

        assert response == bookings
        self.db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_update_booking_status(self):
        booking = Booking(bid=1, uid=1, room_id=1, status="booked")

        response = await self.repo.update_booking_status(booking, "checked_in")

        assert response.status == "checked_in"
        self.db.commit.assert_awaited_once()
        assert response == booking