from unittest.mock import AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from dependencies import get_auth_service
from models.user import User
from routers import auth


class TestAuthRouter:
    def setup_method(self):
        self.app = FastAPI()
        self.app.include_router(auth.router)
        self.auth_service = AsyncMock()
        self.client = TestClient(self.app)
        self.app.dependency_overrides[get_auth_service] = lambda: self.auth_service

    def test_register_user(self):
        result = User(uid=1, fullname='Ritik Kumar', email='ritik@gmail.com', hashed_password='hashed', role='user')
        self.auth_service.register_user.return_value = result

        response = self.client.post(
            '/auth/register',
            json={"fullname": "Ritik Kumar", "email": "ritik@gmail.com", "password": "djs27GH@#", "role": "user"}
        )

        data = response.json().get('data')
        assert response.status_code == 201
        assert response.json().get('success') == True
        assert response.json().get('message') == 'User registered successfully'
        assert data.get('email') == 'ritik@gmail.com'

    def test_login_user(self):
        result = {'access_token': 'sometoken', 'token_type': 'bearer'}
        self.auth_service.login_user.return_value = result

        response = self.client.post(
            '/auth/login',
            data={"username": "ritik@gmail.com", "password": "Passw0rd!"}
        )

        assert response.status_code == 200
        assert response.json().get('access_token') == 'sometoken'
        assert response.json().get('token_type') == 'bearer'