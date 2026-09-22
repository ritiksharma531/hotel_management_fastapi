import pytest
from unittest.mock import AsyncMock, Mock
from models import User
from repositories.auth_repository import AuthRepository


class TestAuthRepository:
    def setup_method(self):
        self.db = AsyncMock()
        self.repo = AuthRepository(self.db)

    @pytest.mark.asyncio
    async def test_check_admin(self):
        admin = User(uid=1, fullname="Ritik Sharma", email="ritik@gmail.com", hashed_password="hashed", role="admin")
        result = Mock()
        result.scalar_one_or_none.return_value = admin
        self.db.execute.return_value = result

        response = await self.repo.check_admin()

        assert response == admin
        self.db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_is_user_exists_true(self):
        user = User(uid=1, fullname="Ritik Sharma", email="ritik@gmail.com", hashed_password="hashed", role="user")
        result = Mock()
        result.scalar_one_or_none.return_value = user
        self.db.execute.return_value = result

        response = await self.repo.is_user_exists("ritik@gmail.com")

        assert response is True
        self.db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_is_user_exists_false(self):
        result = Mock()
        result.scalar_one_or_none.return_value = None
        self.db.execute.return_value = result

        response = await self.repo.is_user_exists("ritik@gmail.com")

        assert response is False
        self.db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_authenticate_user(self):
        user = User(uid=1, fullname="Ritik Sharma", email="ritik@gmail.com", hashed_password="hashed", role="user")
        result = Mock()
        result.scalar_one_or_none.return_value = user
        self.db.execute.return_value = result

        response = await self.repo.authenticate_user("ritik@gmail.com")

        assert response == user
        self.db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_register(self):
        user = User(fullname="Ritik Sharma", email="ritik@gmail.com", hashed_password="hashed", role="user")

        response = await self.repo.register(user)

        self.db.add.assert_called_once_with(user)
        self.db.commit.assert_awaited_once()
        assert response == user