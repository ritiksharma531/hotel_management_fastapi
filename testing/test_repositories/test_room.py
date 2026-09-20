import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock, Mock
from models.room import Room
from schemas.room import BookRoomRequest
from repositories.room_repository import RoomRepository


class TestRoomRepository:
    def setup_method(self):
        self.db = AsyncMock()
        self.repo = RoomRepository(self.db)

    @pytest.mark.asyncio
    async def test_add_room(self):
        room = Room(room_type="regular", price=1500, hid=1)

        response = await self.repo.add_room(room)

        self.db.add.assert_called_once_with(room)
        self.db.commit.assert_awaited_once()
        self.db.refresh.assert_awaited_once_with(room)
        assert response == room

    @pytest.mark.asyncio
    async def test_is_room_available_true(self):
        book_room_request = BookRoomRequest(
            room_id=1, check_in_date=date.today() + timedelta(days=1), check_out_date=date.today() + timedelta(days=2)
        )
        room = Room(room_id=1, room_type="regular", price=1500, hid=1)
        result = Mock()
        result.scalar.return_value = room
        self.db.execute.return_value = result

        response = await self.repo.is_room_available(book_room_request)

        assert response == room
        self.db.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_is_room_available_false(self):
        book_room_request = BookRoomRequest(
            room_id=1, check_in_date=date.today() + timedelta(days=1), check_out_date=date.today() + timedelta(days=2)
        )
        result = Mock()
        result.scalar.return_value = None
        self.db.execute.return_value = result

        response = await self.repo.is_room_available(book_room_request)

        assert response is None
        self.db.execute.assert_awaited_once()