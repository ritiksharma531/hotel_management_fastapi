from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from exceptions.exceptions import UnauthenticatedException, NotFoundException, ForbiddenException, ConflictException
from schemas.api_response import APIResponse
from schemas.error_response import ErrorResponse


def response(status_code: int, message: str, errors: list):
    return JSONResponse(
        status_code=status_code,
        content=APIResponse(
            success=False,
            message=message,
            data=None,
            errors=ErrorResponse(code=status_code, details=errors)
        ).model_dump()
    )


def handle_validation_error(request: Request, exc: RequestValidationError):
    error_list = []
    for error in exc.errors():
        error_list.append({"error": str(error["loc"][-1]), "message": error["msg"]})

    return response(status_code=422, message='Validation error', errors = error_list)


def handle_forbidden(request: Request, exc: ForbiddenException):
    return response(status_code=403, message="Permission Error", errors=[str(exc)])


def handle_unauthenticated(request: Request, exc: UnauthenticatedException):
    return response(status_code=401, message='Authentication Error', errors = [str(exc)])


def handle_not_found(request: Request, exc: NotFoundException):
    return response(status_code=404, message='Not found Error', errors = [str(exc)])


def handle_conflict_error(request: Request, exc: ConflictException):
    return response(status_code=409, message="Conflict Error", errors=[str(exc)])