from unittest.mock import AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from dependencies import get_current_user, get_hotel_service
from models.hotel import Hotel
from routers import hotel


class TestHotelRouter:
    def setup_method(self):
        self.app = FastAPI()
        self.app.include_router(hotel.router)
        self.hotel_service = AsyncMock()
        self.client = TestClient(self.app)
        self.user = {'email': 'temp@gmail.com', 'uid': 1, 'role': 'admin'}
        self.app.dependency_overrides[get_current_user] = lambda: self.user
        self.app.dependency_overrides[get_hotel_service] = lambda: self.hotel_service

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
        assert data.get('rating') == 5

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