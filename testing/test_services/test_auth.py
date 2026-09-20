from datetime import timedelta
from unittest.mock import AsyncMock

import pytest
from fastapi.security import OAuth2PasswordRequestForm

from exceptions.exceptions import ConflictException, UnauthenticatedException
from models import User
from schemas.user import RegisterUserRequest
from services.auth_service import AuthService


class TestAuth:
    def setup_method(self):
        self.auth_repository = AsyncMock()
        self.auth_service = AuthService(self.auth_repository)

    @pytest.mark.asyncio
    async def test_register_user(self):
        register_request = RegisterUserRequest(
            fullname='Ritik Sharma', email='temp@gmail.com', password='Passw0rd!'
        )
        result = User(uid=1, fullname='Ritik Sharma', email='temp@gmail.com',
                       hashed_password='hashed', role='user')
        self.auth_repository.is_user_exists.return_value = False
        self.auth_repository.register.return_value = result

        response = await self.auth_service.register_user(register_request)

        assert response.uid == 1
        assert response.fullname == 'Ritik Sharma'
        assert response.email == 'temp@gmail.com'

    @pytest.mark.asyncio
    async def test_register_admin_when_no_admin_exists(self):
        register_request = RegisterUserRequest(
            fullname='Ritik Sharma', email='temp@gmail.com', password='Passw0rd!', role='admin'
        )
        result = User(uid=1, fullname='Ritik Sharma', email='temp@gmail.com',
                       hashed_password='hashed', role='admin')
        self.auth_repository.check_admin.return_value = None
        self.auth_repository.is_user_exists.return_value = False
        self.auth_repository.register.return_value = result

        response = await self.auth_service.register_user(register_request)

        assert response.uid == 1
        assert response.role == 'admin'

    @pytest.mark.asyncio
    async def test_register_admin_conflict_when_admin_exists(self):
        register_request = RegisterUserRequest(
            fullname='Ritik Sharma', email='temp@gmail.com', password='Passw0rd!', role='admin'
        )
        existing_admin = User(uid=2, fullname='Existing Admin', email='admin@gmail.com',
                               hashed_password='hashed', role='admin')
        self.auth_repository.check_admin.return_value = existing_admin

        with pytest.raises(ConflictException):
            await self.auth_service.register_user(register_request)

    @pytest.mark.asyncio
    async def test_register_user_already_exists(self):
        register_request = RegisterUserRequest(
            fullname='Ritik Sharma', email='temp@gmail.com', password='Passw0rd!'
        )
        self.auth_repository.is_user_exists.return_value = True

        with pytest.raises(ConflictException):
            await self.auth_service.register_user(register_request)

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self):
        password = 'FDsa#21Ee3'
        hashed = self.auth_service.hash_password(password)
        cur_user = User(uid=1, fullname='Ritik Sharma', email='temp@gmail.com',
                         hashed_password=hashed, role='user')
        self.auth_repository.authenticate_user.return_value = cur_user

        response = await self.auth_service.authenticate_user('temp@gmail.com', password)

        assert response.uid == 1
        assert response.email == 'temp@gmail.com'

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self):
        self.auth_repository.authenticate_user.return_value = None

        response = await self.auth_service.authenticate_user('temp@gmail.com', 'Passw0rd!')

        assert response is False

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self):
        hashed = self.auth_service.hash_password('Passw0rd!')
        cur_user = User(uid=1, fullname='Ritik Sharma', email='temp@gmail.com',
                         hashed_password=hashed, role='user')
        self.auth_repository.authenticate_user.return_value = cur_user

        response = await self.auth_service.authenticate_user('temp@gmail.com', 'WrongPass1!')

        assert response is False

    @pytest.mark.asyncio
    async def test_create_token(self):
        token = await self.auth_service.create_token('temp@gmail.com', 1, 'user', timedelta(minutes=20))

        assert isinstance(token, str)
        assert token != ''

    @pytest.mark.asyncio
    async def test_login_user_success(self):
        password = '@34dwwkDW1'
        hashed = self.auth_service.hash_password(password)
        cur_user = User(uid=1, fullname='Ritik Sharma', email='temp@gmail.com',
                         hashed_password=hashed, role='user')
        self.auth_repository.authenticate_user.return_value = cur_user
        form_data = OAuth2PasswordRequestForm(username='temp@gmail.com', password=password)

        response = await self.auth_service.login_user(form_data)

        assert response['token_type'] == 'bearer'
        assert 'access_token' in response

    @pytest.mark.asyncio
    async def test_login_user_wrong_credentials(self):
        self.auth_repository.authenticate_user.return_value = None
        form_data = OAuth2PasswordRequestForm(username='temp@gmail.com', password='WrongPass1!')

        with pytest.raises(UnauthenticatedException):
            await self.auth_service.login_user(form_data)