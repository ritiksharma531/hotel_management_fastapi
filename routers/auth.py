from typing import Annotated
from fastapi import APIRouter, Depends
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm
from dependencies import get_auth_service
from logs.logger import logger
from schemas.api_response import APIResponse
from schemas.user import RegisterUserRequest, UserResponse
from services.auth_service import AuthService

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=APIResponse)
async def register_user(new_user: RegisterUserRequest, auth_service: AuthService = Depends(get_auth_service)):
    result = await auth_service.register_user(new_user)
    logger.info('Register endpoint hit')
    return APIResponse(
        success=True,
        message='User registered successfully',
        data=UserResponse.model_validate(result).model_dump()
    )


@router.post('/login', status_code=status.HTTP_200_OK, response_model=APIResponse)
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], auth_service: AuthService = Depends(get_auth_service)):
    logger.info('Login endpoint hit')
    return await auth_service.login_user(form_data)