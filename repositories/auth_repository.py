from sqlalchemy import select
from models import User
class AuthRepository:
    def __init__(self, db):
        self.db = db

    async def check_admin(self):
        result = await self.db.execute(select(User).where(User.role == 'admin'))
        return result.scalar_one_or_none()

    async def is_user_exists(self, email: str):
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if user:
            return True
        return False


    async def authenticate_user(self, email: str):
        result = await self.db.execute(select(User).where(User.email == email))
        cur_user = result.scalar_one_or_none()
        return cur_user

    async def register(self, new_user_model: User):
        self.db.add(new_user_model)
        await self.db.commit()
        return new_user_model