from unittest.mock import AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from dependencies import get_current_user, get_hotel_service, get_room_service
from exceptions.exception_handlers import handle_forbidden, handle_not_found
from exceptions.exceptions import ForbiddenException, NotFoundException
from models.hotel import Hotel
from models.room import Room
from routers import hotel


class TestHotelRouter:
    def setup_method(self):
        self.app = FastAPI()
        self.app.include_router(hotel.router)
        self.hotel_service = AsyncMock()
        self.room_service = AsyncMock()
        self.client = TestClient(self.app)
        self.app.add_exception_handler(ForbiddenException, handle_forbidden)
        self.app.add_exception_handler(NotFoundException, handle_not_found)
        self.user = {'email': 'temp@gmail.com', 'uid': 1, 'role': 'user'}
        self.app.dependency_overrides[get_current_user] = lambda: self.user
        self.app.dependency_overrides[get_hotel_service] = lambda: self.hotel_service
        self.app.dependency_overrides[get_room_service] = lambda: self.room_service

    def test_add_hotel(self):
        result = Hotel(hid=1, hname='Taj Palace', rating=5)
        self.hotel_service.add_hotel.return_value = result

        response = self.client.post(
            '/hotels',
            json={"hname": "Taj Palace", "rating": 5}
        )

        data = response.json().get('data')
        assert response.status_code == 201
        assert response.json().get('success') == True
        assert response.json().get('message') == 'Hotel Added successfully'
        assert data.get('hid') == 1
        assert data.get('hname') == 'Taj Palace'


    def test_add_hotel_forbidden(self):
        self.hotel_service.add_hotel.side_effect = ForbiddenException('Only admin can add hotels')

        response = self.client.post(
            '/hotels',
            json={
                "hname": "taj",
                "rating": 4
            }
        )

        assert response.status_code == 403
        assert response.json().get('success') == False

    def test_view_all_hotels(self):
        result = [
            Hotel(hid=1, hname='Taj Palace', rating=5),
            Hotel(hid=2, hname='Oberoi', rating=4)
        ]
        self.hotel_service.view_all_hotels.return_value = result

        response = self.client.get('/hotels')

        data = response.json().get('data')
        assert response.status_code == 200
        assert response.json().get('success') == True
        assert response.json().get('message') == 'Hotels fetched successfully'
        assert len(data) == 2
        assert data[0].get('hname') == 'Taj Palace'
        assert data[1].get('rating') == 4

    def test_get_available_rooms(self):
        result = [
            Room(room_id=1, room_type='regular', price=1500, hid=1),
            Room(room_id=2, room_type='premium', price=3000, hid=1)
        ]
        self.hotel_service.get_available_rooms.return_value = result

        response = self.client.get(
            '/hotels/1/rooms',
            params={"check_in_date": "2026-09-18", "check_out_date": "2026-09-19"}
        )

        data = response.json().get('data')
        assert response.status_code == 200
        assert response.json().get('success') == True
        assert response.json().get('message') == 'Room availability fetched successfully'
        assert data[0].get('room_id') == 1

    def test_get_available_rooms_hotel_not_found(self):
        self.hotel_service.get_available_rooms.side_effect = NotFoundException('Hotel not found')

        response = self.client.get('/hotels/1/rooms?check_in_date=2026-09-24&&check_out_date=2026-09-26')

        assert response.status_code == 404


    def test_add_room(self):
        result = Room(room_id=1, room_type='regular', price=1500, hid=1)
        self.room_service.add_room.return_value = result

        response = self.client.post(
            '/hotels/1/rooms',
            json={"room_type": "regular", "price": 1500}
        )

        data = response.json().get('data')
        assert response.status_code == 201
        assert response.json().get('success') == True
        assert response.json().get('message') == 'Room Added Successfully'
        assert data.get('room_type') == 'regular'
        assert data.get('price') == 1500


    def test_add_room_hotel_not_found(self):
        self.room_service.add_room.side_effect = NotFoundException('Hotel not found')

        response = self.client.post(
            '/hotels/1/rooms',
            json={
                "room_type": "regular",
                "price": 1500
            }
        )

        assert response.status_code == 404