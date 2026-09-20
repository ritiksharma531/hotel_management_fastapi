from fastapi import APIRouter, Depends, Path
from starlette import status

from dependencies import get_hotel_service, get_current_user
from logs.logger import logger
from schemas.api_response import APIResponse
from schemas.hotel import AddHotelRequest, HotelResponse
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