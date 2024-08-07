from __future__ import annotations

from typing import Optional, Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.exception.response_type import ResponseType


class CommonResponse(JSONResponse):
    def __init__(self, code: str, status_code: int, message: str, data: Optional[Any] = None):
        self.code = code
        self.message = message
        self.data = data

        content = {
            "code": self.code,
            "message": self.message
        }
        if data is not None:
            content["data"] = jsonable_encoder(self.data)
        super().__init__(status_code=status_code, content=content)

    @classmethod
    def success(cls, data) -> CommonResponse:
        return cls(code=ResponseType.OK.code,
                   status_code=ResponseType.OK.status_code,
                   message=ResponseType.OK.message,
                   data=data)

    @classmethod
    def fail(cls, response_type: ResponseType, message=None, data=None) -> CommonResponse:
        return cls(code=response_type.code,
                   status_code=response_type.status_code,
                   message=message if message is not None else response_type.message,
                   data=data)
