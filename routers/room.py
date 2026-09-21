from fastapi import APIRouter, Depends
from starlette import status
from dependencies import get_room_service, get_current_user
from logs.logger import logger
from schemas.api_response import APIResponse
from services.room_service import RoomService
from schemas.room import AddRoomRequest, AddRoomResponse

router = APIRouter(
    prefix='/rooms',
    tags=['rooms']
)


@router.post('', status_code=status.HTTP_201_CREATED, response_model=APIResponse)
async def add_room(new_room: AddRoomRequest, user: dict = Depends(get_current_user), room_service: RoomService = Depends(get_room_service)):
    logger.info(f'add room endpoint hit by {user.get('uid')}')
    result = await room_service.add_room(new_room, user)
    return APIResponse(
        success=True,
        message='Room Added Successfully',
        data=AddRoomResponse.model_validate(result).model_dump()
    )