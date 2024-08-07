import logging

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError

from src.exception.custom_exception import ResponseType, CustomException
from src.schemas.common_response import CommonResponse


async def custom_exception_handler(request: Request, exc: CustomException) -> CommonResponse:
    return CommonResponse.fail(response_type=exc.error_type, message=exc.detail)


async def http_exception_handler(request: Request, exc: HTTPException) -> CommonResponse:
    logging.error(f"HTTPException: {exc.detail}")
    return CommonResponse(code=f"{exc.status_code}_0", status_code=exc.status_code, message=exc.detail)


async def request_validation_error_handler(request: Request, exc: RequestValidationError) -> CommonResponse:
    data = {}
    for error in exc.errors():
        field = error['loc'][-1]  # 필드 이름 추출
        message = error['msg']
        data[field] = message

    error_type = ResponseType.BINDING_FAILED
    return CommonResponse.fail(response_type=error_type, data=data)


async def generic_exception_handler(request: Request, exc: Exception) -> CommonResponse:
    logging.error(f"Exception: {str(exc)}")
    error_type = ResponseType.INTERNAL_SERVER_ERROR
    return CommonResponse(code=error_type.code, status_code=error_type.status_code, message=error_type.message)
