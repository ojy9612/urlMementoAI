from typing import Optional, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class CommonResponseModel(BaseModel, Generic[T]):
    """Swagger에 표현하기 위한 모델"""
    code: str = Field(..., examples=["200_0"], description="상태코드")
    message: str = Field(..., examples=["정상 처리 되었습니다."], description="상태코드에 따른 메세지")
    data: Optional[T] = None

    class Config:
        arbitrary_types_allowed = True
