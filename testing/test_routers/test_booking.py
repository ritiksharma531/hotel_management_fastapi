from datetime import date
from unittest.mock import AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from dependencies import get_current_user, get_booking_service
from exceptions.exception_handlers import handle_forbidden, handle_not_found, handle_conflict_error
from exceptions.exceptions import ForbiddenException, NotFoundException, ConflictException
from models import Hotel
from models.booking import Booking
from routers import booking


class TestBookingRouter:
    def setup_method(self):
        self.app = FastAPI()
        self.app.include_router(booking.router)
        self.app.add_exception_handler(ForbiddenException, handle_forbidden)
        self.app.add_exception_handler(NotFoundException, handle_not_found)
        self.app.add_exception_handler(ConflictException, handle_conflict_error)
        self.booking_service = AsyncMock()
        self.client = TestClient(self.app)
        self.user = {'email': 'temp@gmail.com', 'uid': 1, 'role': 'user'}
        self.app.dependency_overrides[get_current_user] = lambda: self.user
        self.app.dependency_overrides[get_booking_service] = lambda: self.booking_service

    def test_book_room(self):
        result = Booking(bid=1, uid=2, room_id=2, booking_date=date(2026, 11, 17), check_in_date=date(2026, 11, 18),
                         check_out_date=date(2026, 9, 19), status='booked', price=1000)
        self.booking_service.book_room.return_value = result
        response = self.client.post(
            '/bookings',
            json={"room_id": 1, "check_in_date": "2026-11-17", "check_out_date": "2026-11-18"}
        )

        assert response.status_code == 200
        assert response.json().get('success') == True
        assert response.json().get('message') == 'Room booked successfully'


    def test_book_room_forbidden(self):
        self.booking_service.book_room.side_effect = ForbiddenException('Only admin can add hotels')
        response = self.client.post(
            '/bookings',
            json={"room_id": 1, "check_in_date": "2026-11-17", "check_out_date": "2026-11-18"}
        )

        assert response.status_code == 403
        assert response.json().get('success') == False



    def test_get_bookings(self):
        result = [
            Booking(bid=1, uid = 2, room_id = 2, booking_date = date(2026, 9, 17), check_in_date = date(2026, 9, 18), check_out_date = date(2026, 9, 19), status = 'booked', price = 1000),
            Booking(bid=1, uid = 2, room_id = 2, booking_date = date(2026, 9, 17), check_in_date = date(2026, 9, 18), check_out_date = date(2026, 9, 19), status = 'booked', price = 1000)
        ]
        self.booking_service.get_bookings.return_value = result

        response = self.client.get('/bookings')
        assert response.status_code == 200
        assert response.json().get('success') == True
        assert response.json().get('message') == 'Bookings fetched successfully'


    def test_update_booking_status(self):
        result = Booking(bid=1, uid = 2, room_id = 2, booking_date = date(2026, 11, 17), check_in_date = date(2026, 11, 18), check_out_date = date(2026, 9, 19), status = 'booked', price=1000)
        self.booking_service.book_room.return_value = result
        response = self.client.post(
            '/bookings',
            json={"room_id": 1, "check_in_date": "2026-11-17", "check_out_date": "2026-11-18"}
        )

        assert response.status_code == 200
        assert response.json().get('success') == True
        assert response.json().get('message') == 'Room booked successfully'


    def test_update_booking_status_not_found(self):
        self.booking_service.update_booking_status.side_effect = NotFoundException('Booking not found')

        response = self.client.patch(
            '/bookings/1',
            json={
                'status': 'checked_in'
            }
        )

        assert response.status_code == 404
        assert response.json().get('success') == False

    def test_update_booking_status_check_in_after_check_in(self):
        self.booking_service.update_booking_status.side_effect = ConflictException('Already checked in')

        response = self.client.patch(
            '/bookings/1',
            json={
                'status': 'checked_in'
            }
        )

        assert response.status_code == 409
        assert response.json().get('success') == False

    def test_update_booking_status_cancel_after_cancel(self):
        self.booking_service.update_booking_status.side_effect = ConflictException('Booking has been already cancelled')

        response = self.client.patch(
            '/bookings/1',
            json={
                'status': 'cancelled'
            }
        )

        assert response.status_code == 409
        assert response.json().get('success') == False