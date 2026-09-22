from fastapi import APIRouter, Depends, Path, Query
from starlette import status
from dependencies import get_hotel_service, get_current_user, get_room_service
from logs.logger import logger
from schemas.api_response import APIResponse
from schemas.hotel import AddHotelRequest, HotelResponse, GetAvailabilityRequest
from schemas.room import RoomResponse, AddRoomRequest, AddRoomResponse
from services.hotel_service import HotelService

router = APIRouter(
    prefix='/hotels',
    tags=['hotels']
)

@router.post('', status_code=status.HTTP_201_CREATED, response_model=APIResponse)
async def add_hotel(add_hotel_request: AddHotelRequest, user: dict = Depends(get_current_user), hotel_service: HotelService = Depends(get_hotel_service)):
    logger.info(f'add hotel endpoint hit by {user.get('uid')}')
    result = await hotel_service.add_hotel(user, add_hotel_request)
    return APIResponse(
        success=True,
        message='Hotel Added successfully',
        data=HotelResponse.model_validate(result).model_dump()
    )

@router.get('', status_code=status.HTTP_200_OK, response_model=APIResponse)
async def view_all_hotels(user: dict = Depends(get_current_user), hotel_service: HotelService = Depends(get_hotel_service)):
    logger.info(f'view all hotels endpoint hit by {user.get('uid')}')
    result = await hotel_service.view_all_hotels(user)
    data = []
    for hotel in result:
        data.append(HotelResponse.model_validate(hotel).model_dump())
    return APIResponse(
        success=True,
        message='Hotels fetched successfully',
        data=data
    )

@router.post('/{hid}/rooms', status_code=status.HTTP_201_CREATED, response_model=APIResponse)
async def add_room(hid, new_room: AddRoomRequest, user: dict = Depends(get_current_user), room_service: RoomService = Depends(get_room_service)):
    logger.info(f'add room endpoint hit by {user.get('uid')}')
    result = await room_service.add_room(hid, new_room, user)
    return APIResponse(
        success=True,
        message='Room Added Successfully',
        data=AddRoomResponse.model_validate(result).model_dump()
    )

@router.get('/{hid}/rooms', status_code=status.HTTP_200_OK, response_model=APIResponse)
async def get_available_rooms(hid: int, get_availability_request: GetAvailabilityRequest = Query(), hotel_service: HotelService = Depends(get_hotel_service), user: dict = Depends(get_current_user)):
    logger.info(f'get available rooms endpoint hit by {user.get('uid')}')
    result = await hotel_service.get_available_rooms(hid, get_availability_request, user)
    data = []
    for room in result:
        data.append(RoomResponse.model_validate(room).model_dump())
    return APIResponse(
        success=True,
        message='Room availability fetched successfully',
        data=data
    )