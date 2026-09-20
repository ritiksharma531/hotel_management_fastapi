from datetime import date, timedelta
from exceptions.exceptions import UnauthenticatedException, ForbiddenException, NotFoundException, ConflictException
from logs.logger import logger
from models import Booking
from repositories.booking_repository import BookingRepository
from repositories.hotel_repository import HotelRepository
from repositories.room_repository import RoomRepository
from schemas.room import BookRoomRequest


class BookingService:
    def __init__(self, booking_repository: BookingRepository, hotel_repository: HotelRepository, room_repository: RoomRepository):
        self.booking_repository = booking_repository
        self.hotel_repository = hotel_repository
        self.room_repository = room_repository
        self.special_dates = [(26, 1), (15, 8), (2, 10), (25, 12)]

    def get_updated_price(self, day: date, base_price: float):
        is_special = (day.day, day.month) in self.special_dates
        is_sunday = day.weekday() == 6

        if is_special or is_sunday:
            return base_price * 0.8
        return base_price

    async def book_room(self, book_room_request: BookRoomRequest, user: dict):
        if user is None:
            raise UnauthenticatedException('Register or Login first')

        if user.get('role') != 'user':
            raise ForbiddenException('Admin not allowed')

        room = await self.room_repository.is_room_available(book_room_request)
        if room is None :
            raise NotFoundException('Room not available')

        check_in_date = book_room_request.check_in_date
        check_out_date = book_room_request.check_out_date

        final_price = 0
        current = check_in_date
        while current < check_out_date:
            final_price += self.get_updated_price(current, room.price)
            current += timedelta(days=1)

        add_booking_model = Booking(
            uid = user.get('uid'),
            room_id = room.room_id,
            booking_date = date.today(),
            check_in_date = book_room_request.check_in_date,
            check_out_date = book_room_request.check_out_date,
            status = 'booked'
        )
        result = (await self.booking_repository.book_room(add_booking_model), final_price)
        logger.info(f'User with id {user.get('uid')} booked room')
        return result


    async def update_booking_status(self, bid: int, user: dict, status: str):
        if user is None:
            raise UnauthenticatedException('Register or Login first')

        if user.get('role') != 'user':
            raise ForbiddenException('Admin not allowed')

        booking = await self.booking_repository.get_booking(bid)
        if booking is None:
            raise NotFoundException('Booking not found')

        if status == 'checked_in' and booking.status == 'checked_in':
            raise ConflictException('Already checked in')

        if status in ['checked_in', 'completed', 'cancelled'] and booking.status == 'cancelled':
            raise ConflictException('Booking has been already cancelled')

        if status in ['checked_in', 'completed', 'cancelled'] and booking.status == 'completed':
            raise ConflictException('Already completed the booking')

        result = await self.booking_repository.update_booking_status(booking, status)
        logger.info(f'User with id {user.get('uid')} updated booking status to {status}')
        return result


    async def get_all_bookings(self, user: dict):
        if user is None:
            raise UnauthenticatedException('Register or Login first')

        if user.get('role') != 'admin':
            raise ForbiddenException('Only admin allowed')

        result = await self.booking_repository.get_all_bookings()
        logger.info(f'User with id {user.get('uid')} viewed all bookings')
        return result

    async def get_my_bookings(self, user: dict):
        if user is None:
            raise UnauthenticatedException('Register or Login first')

        if user.get('role') != 'user':
            raise ForbiddenException('Admin not allowed')

        result = await self.booking_repository.get_my_bookings(user.get('uid'))
        logger.info(f'User with id {user.get('uid')} viewed his/her bookings')
        return result