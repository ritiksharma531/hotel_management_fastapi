from fastapi.security import OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from datetime import timedelta, datetime, timezone
from jose import jwt
from config import settings
from exceptions.exceptions import ConflictException, UnauthenticatedException
from logs.logger import logger
from models.user import User
from repositories.auth_repository import AuthRepository
from schemas.user import RegisterUserRequest


class AuthService:
    def __init__(self, auth_repository: AuthRepository):
        self.password_hash = PasswordHash.recommended()
        self.auth_repository = auth_repository

    def hash_password(self, normal_password: str):
        return self.password_hash.hash(normal_password)

    def verify_password(self, entered_password: str, hashed_password: str):
        return self.password_hash.verify(entered_password, hashed_password)

    async def authenticate_user(self, email: str, password: str):
        cur_user = await self.auth_repository.authenticate_user(email)

        if not cur_user:
            return False
        if self.verify_password(password, cur_user.hashed_password):
            return cur_user
        return False

    async def create_token(self, email: str, user_id: int, role: str, expires_delta: timedelta):
        encode = {'sub': email, 'id': user_id, 'role': role}
        expires = datetime.now(timezone.utc) + expires_delta
        encode.update({'exp': expires})
        return jwt.encode(encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


    async def register_user(self, new_user: RegisterUserRequest):
        if new_user.role == 'admin' and await self.auth_repository.check_admin():
            logger.error(f'Someone tried to register as admin')
            raise ConflictException("Can't register as admin")

        if await self.auth_repository.is_user_exists(new_user.email):
            logger.error(f'Already registered user tries to register again')
            raise ConflictException('User already exists')

        new_user_model = User(
            fullname=new_user.fullname,
            email=new_user.email,
            hashed_password=self.hash_password(new_user.password),
            role=new_user.role
        )
        result = await self.auth_repository.register(new_user_model)
        logger.info(f'User {new_user.fullname} registered')
        return result


    async def login_user(self, form_data:OAuth2PasswordRequestForm):
        cur_user = await self.authenticate_user(form_data.username, form_data.password)
        if not cur_user:
            logger.error(f'User not authenticated')
            raise UnauthenticatedException('Wrong credentials')
        token = await self.create_token(cur_user.email, cur_user.uid, cur_user.role, timedelta(minutes=20))
        return {'access_token': token, 'token_type': 'bearer'}