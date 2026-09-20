from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from database.database import engine, Base
from exceptions.exception_handlers import handle_not_found, handle_forbidden, handle_unauthenticated, \
    handle_conflict_error, handle_validation_error
from exceptions.exceptions import  NotFoundException, ForbiddenException, UnauthenticatedException, ConflictException
from routers import auth, hotel, room, booking


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

app.add_exception_handler(NotFoundException, handle_not_found)
app.add_exception_handler(ForbiddenException, handle_forbidden)
app.add_exception_handler(UnauthenticatedException, handle_unauthenticated)
app.add_exception_handler(ConflictException, handle_conflict_error)
app.add_exception_handler(RequestValidationError, handle_validation_error)


app.include_router(auth.router)
app.include_router(hotel.router)
app.include_router(room.router)
app.include_router(booking.router)