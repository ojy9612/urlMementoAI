from typing import Optional

from pydantic import BaseModel, field_validator, Field


class URLCreateRequest(BaseModel):
    url: str = Field(..., examples=["https://www.google.com", "naver.com"], description="원본 URL")
    expires_days: Optional[int] = Field(None, examples=[None, 1, 30], description="1~30사이의 정수 입력, 미 입력시 만료되지 않음")

    @field_validator('expires_days')
    def validate_expires_days(cls, v):
        if v is None:
            return v
        if not (1 <= v <= 30):
            raise ValueError("만료일자는 1~30일 사이로 정해야 합니다.")
        return v

    @field_validator('url')
    def validate_url(cls, v):
        if not v:
            raise ValueError('비어있는 값이 올 수 없습니다.')
        if '.' not in v:
            raise ValueError('URL은 최소 하나의 (.)을 포함해야 합니다.')
        return v


class URLResponse(BaseModel):
    short_key: str = Field(..., examples=["https://www.google.com", "naver.com"])
    expires_at: Optional[str] = Field(None, examples=["2024-08-07 21:07:22"])


class URLStatsResponse(BaseModel):
    original_url: str
    clicks: int
