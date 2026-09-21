from unittest.mock import AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from dependencies import get_current_user, get_room_service
from models.room import Room
from routers import room


class TestRoomRouter:
    def setup_method(self):
        self.app = FastAPI()
        self.app.include_router(room.router)
        self.room_service = AsyncMock()
        self.client = TestClient(self.app)
        self.user = {'email': 'temp@gmail.com', 'uid': 1, 'role': 'admin'}
        self.app.dependency_overrides[get_current_user] = lambda: self.user
        self.app.dependency_overrides[get_room_service] = lambda: self.room_service

    def test_add_room(self):
        result = Room(room_id=1, room_type='regular', price=1500, hid=1)
        self.room_service.add_room.return_value = result

        response = self.client.post(
            '/rooms',
            json={"room_type": "regular", "price": 1500, "hid": 1}
        )

        data = response.json().get('data')
        assert response.status_code == 201
        assert response.json().get('success') == True
        assert response.json().get('message') == 'Room Added Successfully'
        assert data.get('room_type') == 'regular'
        assert data.get('price') == 1500