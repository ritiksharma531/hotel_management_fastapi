from datetime import date
from unittest.mock import AsyncMock

import pytest

from exceptions.exceptions import ForbiddenException, UnauthenticatedException, ConflictException, NotFoundException
from models import Booking, Room
from schemas.room import BookRoomRequest
from services.booking_service import BookingService


class TestBooking:
    def setup_method(self):
        self.user = {'email': 'temp@gmail.com', 'uid': 1, 'role': 'user'}
        self.admin = {'email': 'temp@gmail.com', 'uid': 1, 'role': 'admin'}
        self.booking_repository = AsyncMock()
        self.hotel_repository = AsyncMock()
        self.room_repository = AsyncMock()
        self.booking_service = BookingService(self.booking_repository, self.hotel_repository, self.room_repository)

    @pytest.mark.asyncio
    async def test_book_room(self):
        booking_request = BookRoomRequest(
            room_id=1, check_in_date=date(2026, 11, 18), check_out_date=date(2026, 11, 19)
        )
        result = Booking(bid=1, uid=2, room_id=2, booking_date=date(2026, 11, 17), check_in_date=date(2026, 11, 18),
                    check_out_date=date(2026, 11, 19), status='booked', price = 1000)
        self.booking_repository.book_room.return_value = result
        self.room_repository.is_room_available.return_value = Room(room_id = 1, room_type = 'regular', price = 1000, hid = 1)

        response = await self.booking_service.book_room(booking_request, self.user)

        assert response.bid == 1
        assert response.price == 1000



    @pytest.mark.asyncio
    async def test_book_room_forbidden_for_admin(self):
        booking_request = BookRoomRequest(
            room_id=1, check_in_date=date(2026, 11, 18), check_out_date=date(2026, 11, 19)
        )
        with pytest.raises(ForbiddenException):
            await self.booking_service.book_room(booking_request, self.admin)

    @pytest.mark.asyncio
    async def test_book_room_not_available(self):
        booking_request = BookRoomRequest(
            room_id=1, check_in_date=date(2026, 11, 18), check_out_date=date(2026, 11, 19)
        )
        self.room_repository.is_room_available.return_value = None

        with pytest.raises(NotFoundException):
            await self.booking_service.book_room(booking_request, self.user)



    @pytest.mark.asyncio
    async def test_update_booking_status_forbidden_for_admin(self):
        with pytest.raises(ForbiddenException):
            await self.booking_service.update_booking_status(1, self.admin, 'completed')

    @pytest.mark.asyncio
    async def test_update_booking_status_not_found(self):
        self.booking_repository.get_booking.return_value = None

        with pytest.raises(NotFoundException):
            await self.booking_service.update_booking_status(1, self.user, 'completed')

    @pytest.mark.asyncio
    async def test_update_booking_status_already_checked_in(self):
        booking = Booking(bid=1, uid=2, room_id=2, booking_date=date(2026, 9, 17), check_in_date=date(2026, 9, 18),
                          check_out_date=date(2026, 9, 20), status='checked_in')
        self.booking_repository.get_booking.return_value = booking

        with pytest.raises(ConflictException):
            await self.booking_service.update_booking_status(1, self.user, 'checked_in')

    @pytest.mark.asyncio
    async def test_update_booking_status_already_cancelled(self):
        booking = Booking(bid=1, uid=2, room_id=2, booking_date=date(2026, 9, 17), check_in_date=date(2026, 9, 18),
                          check_out_date=date(2026, 9, 20), status='cancelled')
        self.booking_repository.get_booking.return_value = booking

        with pytest.raises(ConflictException):
            await self.booking_service.update_booking_status(1, self.user, 'completed')

    @pytest.mark.asyncio
    async def test_update_booking_status_already_completed(self):
        booking = Booking(bid=1, uid=2, room_id=2, booking_date=date(2026, 9, 17), check_in_date=date(2026, 9, 18),
                          check_out_date=date(2026, 9, 20), status='completed')
        self.booking_repository.get_booking.return_value = booking

        with pytest.raises(ConflictException):
            await self.booking_service.update_booking_status(1, self.user, 'cancelled')


    @pytest.mark.asyncio
    async def test_get_bookings_admin_uses_get_all_bookings(self):
        result = [
            Booking(bid=1, uid=2, room_id=2, booking_date=date(2026, 9, 17), check_in_date=date(2026, 9, 18),
                    check_out_date=date(2026, 9, 19), status='booked')
        ]
        self.booking_repository.get_all_bookings.return_value = result

        response = await self.booking_service.get_bookings(self.admin)

        self.booking_repository.get_all_bookings.assert_awaited_once()
        self.booking_repository.get_my_bookings.assert_not_called()
        assert response == result

    @pytest.mark.asyncio
    async def test_get_bookings_user_uses_get_my_bookings(self):
        result = [
            Booking(bid=1, uid=1, room_id=2, booking_date=date(2026, 9, 17), check_in_date=date(2026, 9, 18),
                    check_out_date=date(2026, 9, 19), status='booked')
        ]
        self.booking_repository.get_my_bookings.return_value = result

        response = await self.booking_service.get_bookings(self.user)

        self.booking_repository.get_my_bookings.assert_awaited_once_with(self.user.get('uid'))
        self.booking_repository.get_all_bookings.assert_not_called()
        assert response == result


    def test_get_updated_price_regular_day(self):
        price = self.booking_service.get_updated_price(date(2026, 11, 18), 1000)
        assert price == 1000

    def test_get_updated_price_sunday(self):
        price = self.booking_service.get_updated_price(date(2026, 11, 22), 1000)
        assert price == 800

    def test_get_updated_price_special_date(self):
        price = self.booking_service.get_updated_price(date(2026, 12, 25), 1000)
        assert price == 800

    @pytest.mark.asyncio
    async def test_book_room_multi_day_price_sums_correctly(self):
        booking_request = BookRoomRequest(
            room_id=1, check_in_date=date(2026, 11, 21), check_out_date=date(2026, 11, 23)
        )
        result = Booking(bid=1, uid=2, room_id=2, booking_date=date(2026, 11, 17), check_in_date=date(2026, 11, 21),
                         check_out_date=date(2026, 11, 23), status='booked', price = 1800)
        self.booking_repository.book_room.return_value = result
        self.room_repository.is_room_available.return_value = Room(room_id=1, room_type='regular', price=1000, hid=1)

        response = await self.booking_service.book_room(booking_request, self.user)

        assert response.price == 1800