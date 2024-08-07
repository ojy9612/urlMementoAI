from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.utils.utils import datetime_now_timezone


class URLModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    original_url: str
    short_key: str
    created_at: datetime = Field(default_factory=lambda: datetime_now_timezone())
    expires_at: Optional[datetime] = None
    clicks: int = Field(default=0)

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        from_attributes = True

    def to_mongo(self) -> dict:
        return self.model_dump(by_alias=True, exclude={"id"})

    @classmethod
    def from_mongo(cls, data: dict) -> Optional[URLModel]:
        if data is None or data["_id"] is None:
            return None
        return cls(
            id=data["_id"].__str__(),
            original_url=data["original_url"],
            short_key=data["short_key"],
            created_at=data["created_at"],
            expires_at=data["expires_at"],
            clicks=data["clicks"]
        )
