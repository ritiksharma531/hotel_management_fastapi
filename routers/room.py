from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from starlette import status

from dependencies import get_room_service, get_current_user
from logs.logger import logger
from schemas.api_response import APIResponse
from schemas.hotel import GetAvailabilityRequest
from services.room_service import RoomService
from schemas.room import AddRoomRequest, AddRoomResponse, RoomResponse

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

@router.get('', status_code=status.HTTP_200_OK, response_model=APIResponse)
async def get_available_rooms(hid: int, check_in_date: date = Query(default=date.today()), check_out_date: date = Query(default=date.today() + timedelta(days=1)), room_service: RoomService = Depends(get_room_service), user: dict = Depends(get_current_user)):
    logger.info(f'get available rooms endpoint hit by {user.get('uid')}')
    get_availability_request = GetAvailabilityRequest(hid=hid, check_in_date=check_in_date, check_out_date=check_out_date)
    result = await room_service.get_available_rooms(get_availability_request, user)
    data = []
    for room in result:
        data.append(RoomResponse.model_validate(room).model_dump())
    return APIResponse(
        success=True,
        message='Room availability fetched successfully',
        data=data
    )