from datetime import date
from unittest.mock import AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from dependencies import get_current_user, get_booking_service
from models.booking import Booking
from routers import booking


class TestBookingRouter:
    def setup_method(self):
        self.app = FastAPI()
        self.app.include_router(booking.router)
        self.booking_service = AsyncMock()
        self.client = TestClient(self.app)
        self.user = {'email': 'temp@gmail.com', 'uid': 1, 'role': 'user'}
        self.app.dependency_overrides[get_current_user] = lambda: self.user
        self.app.dependency_overrides[get_booking_service] = lambda: self.booking_service

    def test_get_all_bookings(self):
        result = [
            Booking(bid=1, uid = 2, room_id = 2, booking_date = date(2026, 9, 17), check_in_date = date(2026, 9, 18), check_out_date = date(2026, 9, 19), status = 'booked'),
            Booking(bid=1, uid = 2, room_id = 2, booking_date = date(2026, 9, 17), check_in_date = date(2026, 9, 18), check_out_date = date(2026, 9, 19), status = 'booked')
        ]
        self.booking_service.get_all_bookings.return_value = result

        response = self.client.get('/bookings')
        assert response.status_code == 200
        assert response.json().get('success') == True
        assert response.json().get('message') == 'Bookings fetched successfully'


    def test_book_room(self):
        result = (Booking(bid=1, uid = 2, room_id = 2, booking_date = date(2026, 11, 17), check_in_date = date(2026, 11, 18), check_out_date = date(2026, 9, 19), status = 'booked'), 1000)
        self.booking_service.book_room.return_value = result
        response = self.client.post(
            '/bookings',
            json={"room_id": 1, "check_in_date": "2026-11-17", "check_out_date": "2026-11-18"}
        )

        assert response.status_code == 200
        assert response.json().get('success') == True
        assert response.json().get('message') == 'Room booked successfully'


    def test_update_booking_status(self):
        result = (Booking(bid=1, uid = 2, room_id = 2, booking_date = date(2026, 11, 17), check_in_date = date(2026, 11, 18), check_out_date = date(2026, 9, 19), status = 'booked'), 1000)
        self.booking_service.book_room.return_value = result
        response = self.client.post(
            '/bookings',
            json={"room_id": 1, "check_in_date": "2026-11-17", "check_out_date": "2026-11-18"}
        )

        assert response.status_code == 200
        assert response.json().get('success') == True
        assert response.json().get('message') == 'Room booked successfully'

    def test_get_my_bookings(self):
        result = [
            Booking(bid=1, uid = 2, room_id = 2, booking_date = date(2026, 9, 17), check_in_date = date(2026, 9, 18), check_out_date = date(2026, 9, 19), status = 'booked'),
            Booking(bid=1, uid = 2, room_id = 2, booking_date = date(2026, 9, 17), check_in_date = date(2026, 9, 18), check_out_date = date(2026, 9, 19), status = 'booked')
        ]
        self.booking_service.get_all_bookings.return_value = result

        response = self.client.get('/bookings/my_bookings')
        assert response.status_code == 200
        assert response.json().get('success') == True
        assert response.json().get('message') == 'Bookings fetched successfully'