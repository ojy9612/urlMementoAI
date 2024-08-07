from datetime import timedelta

import shortuuid

from src.config.database import url_collection
from src.exception.custom_exception import CustomException
from src.exception.response_type import ResponseType
from src.models.url import URLModel
from src.schemas.url_schema import URLCreateRequest, URLStatsResponse, URLResponse
from src.utils.utils import datetime_to_str, datetime_now_timezone, default_timezone


async def _create_key() -> str:
    while True:
        short_key = shortuuid.uuid()[:7]
        existing_url = await url_collection.find_one({"short_key": short_key})
        if not existing_url:
            return short_key


async def create_shorten_url(url_create: URLCreateRequest, db_session) -> URLResponse:
    short_key = await _create_key()

    expires_at = None
    if url_create.expires_days:
        expires_at = ((datetime_now_timezone() + timedelta(days=url_create.expires_days))
                      .replace(tzinfo=default_timezone()))
    url = URLModel(original_url=url_create.url, short_key=short_key, expires_at=expires_at)
    await url_collection.insert_one(url.to_mongo(), session=db_session)

    return URLResponse(short_key=short_key, expires_at=datetime_to_str(expires_at) if expires_at else None)


async def get_original_url(short_key: str, db_session) -> str:
    url = await url_collection.find_one({"short_key": short_key}, session=db_session)
    if url is None:
        raise CustomException(ResponseType.RESOURCE_NOT_FOUND, message=f"등록된 단축 URL이 없습니다. URL: {short_key}")

    expires_at = url.get("expires_at")
    if expires_at:
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=default_timezone())
        if expires_at < datetime_now_timezone():
            raise CustomException(ResponseType.EXPIRED_RESOURCE, message=f"만료된 단축 URL입니다. URL: {short_key}")

    await url_collection.update_one({"short_key": short_key}, {"$inc": {"clicks": 1}}, session=db_session)
    original_url = url["original_url"]
    if not original_url.startswith(("http://", "https://")):
        original_url = "http://" + original_url
    return original_url


async def get_url_stats(short_key: str, db_session) -> URLStatsResponse:
    url = await url_collection.find_one({"short_key": short_key}, session=db_session)
    if url is None:
        raise CustomException(ResponseType.RESOURCE_NOT_FOUND, f"단축 URL을 찾을 수 없습니다. short_key: {short_key}")
    url = URLModel.from_mongo(url)
    return URLStatsResponse(original_url=url.original_url, clicks=url.clicks)


async def delete_expired_urls():
    now = datetime_now_timezone()
    await url_collection.delete_many({"expires_at": {"$lt": now}})
