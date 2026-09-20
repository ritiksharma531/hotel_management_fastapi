from fastapi import APIRouter, Depends
from starlette import status

from dependencies import get_booking_service, get_current_user
from logs.logger import logger
from schemas.api_response import APIResponse
from schemas.booking import BookingResponse, BookingStatus
from schemas.room import BookRoomRequest, BookRoomResponse, BaseBookingResponse, UpdateStatusResponse
from services.booking_service import BookingService

router = APIRouter(
    prefix='/bookings',
    tags=['bookings']
)

@router.post('', status_code=status.HTTP_200_OK, response_model=APIResponse)
async def book_room(book_room_request: BookRoomRequest, user: dict = Depends(get_current_user), booking_service:BookingService = Depends(get_booking_service)):
    logger.info(f'book room endpoint hit by {user.get('uid')}')
    result, price = await booking_service.book_room(book_room_request, user)
    return APIResponse(
        success=True,
        message='Room booked successfully',
        data=BookRoomResponse(**BaseBookingResponse.model_validate(result).model_dump(), price=price)
    )

@router.patch('', status_code=status.HTTP_200_OK, response_model=APIResponse)
async def update_booking_status(booking_id: int, status: BookingStatus, user: dict = Depends(get_current_user), booking_service: BookingService = Depends(get_booking_service)):
    logger.info(f'update status endpoint hit by {user.get('uid')}')
    result = await booking_service.update_booking_status(booking_id, user, status.status)

    return APIResponse(
        success=True,
        message='Updated status successfully',
        data=UpdateStatusResponse.model_validate(result).model_dump()
    )


@router.get('', status_code=status.HTTP_200_OK, response_model=APIResponse)
async def get_all_bookings(user: dict = Depends(get_current_user), booking_service: BookingService = Depends(get_booking_service)):
    logger.info(f'get all bookings endpoint hit by {user.get('uid')}')
    result =  await booking_service.get_all_bookings(user)
    data = []
    for booking in result:
        data.append(BookingResponse.model_validate(booking).model_dump())
    return APIResponse(
        success=True,
        message='Bookings fetched successfully',
        data=data
    )

@router.get('/my_bookings', status_code=status.HTTP_200_OK, response_model=APIResponse)
async def get_my_bookings(user: dict = Depends(get_current_user), booking_service: BookingService = Depends(get_booking_service)):
    logger.info(f'get my bookings endpoint hit by {user.get('uid')}')
    result = await booking_service.get_my_bookings(user)
    data = []
    for booking in result:
        data.append(BookingResponse.model_validate(booking).model_dump())
    return APIResponse(
        success=True,
        message='Bookings fetched successfully',
        data=data
    )