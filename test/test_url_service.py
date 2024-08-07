import asyncio
from datetime import datetime, timezone, timedelta

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from main import app
from src.batch.scheduler import delete_expired_urls
from src.exception.response_type import ResponseType
from src.models.url import URLModel
from src.schemas.common_response import CommonResponse
from src.schemas.url_schema import URLResponse, URLStatsResponse
from src.utils.utils import datetime_now_timezone
from test.conftest import url_collection


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client():
    return TestClient(app)


@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac


test_data = [
    pytest.param("https://www.google.com", None,
                 id="구글 URL, None"),
    pytest.param("https://www.google.com", 10,
                 id="구글 URL, 10"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("url_input, expires_days_input", test_data)
async def test_create_shorten_url(async_client, url_input, expires_days_input):
    """URL 단축 생성"""
    response = await async_client.post("/shorten",
                                       json={"url": url_input, "expires_days": expires_days_input})
    assert response.status_code == 200
    response_json = response.json()
    response = CommonResponse(**response_json, status_code=response.status_code)
    url_response = URLResponse(**response.data)

    assert url_response.short_key
    if expires_days_input is not None:
        assert url_response.expires_at
    else:
        assert url_response.expires_at is None

    url_data = await url_collection.find_one({"short_key": url_response.short_key})
    url_data: URLModel = URLModel.from_mongo(url_data)
    assert url_data is not None
    assert url_data.original_url == url_input


test_data = [
    pytest.param("",
                 id="빈 URL"),
    pytest.param("google",
                 id="잘못된 URL"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("url_input", test_data)
async def test_create_shorten_url_empty_wrong(async_client, url_input):
    """URL 단축 생성 - 빈 URL, 잘못된 URL"""
    response = await async_client.post("/shorten", json={"url": url_input})
    response_json = response.json()
    response = CommonResponse(**response_json, status_code=response.status_code)
    assert response.code == ResponseType.BINDING_FAILED.code


test_data = [
    pytest.param("https://www.google.com", -1,
                 id="구글 URL, -1"),
    pytest.param("https://www.google.com", 0,
                 id="구글 URL, 0"),
    pytest.param("https://www.google.com", 31,
                 id="구글 URL, 31"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("url_input, expires_days_input", test_data)
async def test_create_shorten_url_invalid_days(async_client, url_input, expires_days_input):
    """URL 단축 생성 - 잘못된 만료일"""
    response = await async_client.post("/shorten",
                                       json={"url": url_input, "expires_days": expires_days_input})
    response_json = response.json()
    response = CommonResponse(**response_json, status_code=response.status_code)
    assert response.code == ResponseType.BINDING_FAILED.code


test_data = [
    pytest.param("https://www.google.com", None,
                 id="구글 URL, None"),
    pytest.param("https://www.google.com", 10,
                 id="구글 URL, 10"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("url_input, expires_days_input", test_data)
async def test_redirect_original_url(async_client, url_input, expires_days_input):
    """원본 URL 리다이렉션"""
    response = await async_client.post("/shorten",
                                       json={"url": url_input, "expires_days": expires_days_input})
    assert response.status_code == 200
    response_json = response.json()
    response = CommonResponse(**response_json, status_code=response.status_code)
    url_response = URLResponse(**response.data)

    response = await async_client.get(f"/{url_response.short_key}")
    assert response.status_code == 301
    assert response.headers["Location"] == url_input


test_data = [
    pytest.param("https://www.google.com", "SHORT",
                 id="구글 URL, 단축 URL"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("url_input, short_key_input", test_data)
async def test_redirect_expired_url(async_client, url_input, short_key_input):
    """원본 URL 리다이렉션 - 만료된 단축 URL"""
    url_model = URLModel(original_url=url_input,
                         short_key=short_key_input,
                         expires_at=datetime.now(timezone.utc) - timedelta(days=1),
                         clicks=0)
    url_collection.insert_one(url_model.model_dump())

    response = await async_client.get(f"/{short_key_input}")
    response_json = response.json()
    response = CommonResponse(**response_json, status_code=response.status_code)
    assert response.code == ResponseType.EXPIRED_RESOURCE.code


test_data = [
    pytest.param("https://www.google.com", "",
                 id="구글 URL, 빈 단축 URL"),
    pytest.param("https://www.google.com", "SHORT",
                 id="구글 URL, 단축 URL"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("url_input, short_key_input", test_data)
async def test_redirect_expired_url(async_client, url_input, short_key_input):
    """원본 URL 리다이렉션 - 잘못된 단축 URL"""
    url_model = URLModel(original_url=url_input,
                         short_key=short_key_input,
                         expires_at=datetime.now(timezone.utc) + timedelta(days=1),
                         clicks=0)
    url_collection.insert_one(url_model.model_dump())

    wrong_url = "wrong_url"
    response = await async_client.get(f"/{wrong_url}")
    assert response.status_code == 404
    response_json = response.json()
    response = CommonResponse(**response_json, status_code=response.status_code)
    assert response.code == ResponseType.RESOURCE_NOT_FOUND.code


test_data = [
    pytest.param("https://www.google.com", None,
                 id="구글 URL, None"),
    pytest.param("https://www.google.com", 10,
                 id="구글 URL, 10"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("url_input, expires_days_input", test_data)
async def test_get_url_stats(async_client, url_input, expires_days_input):
    """URL 통계 정보"""
    response = await async_client.post("/shorten", json={"url": url_input, "expires_days": expires_days_input})
    assert response.status_code == 200
    response_json = response.json()
    response = CommonResponse(**response_json, status_code=response.status_code)
    url_response = URLResponse(**response.data)

    response = await async_client.get(f"/stats/{url_response.short_key}")
    assert response.status_code == 200
    response_json = response.json()
    response = CommonResponse(**response_json, status_code=response.status_code)
    url_stats_response = URLStatsResponse(**response.data)

    assert url_stats_response.original_url == url_input
    assert url_stats_response.clicks == 0

    await async_client.get(f"/{url_response.short_key}")
    response = await async_client.get(f"/stats/{url_response.short_key}")

    assert response.status_code == 200
    response_json = response.json()
    response = CommonResponse(**response_json, status_code=response.status_code)
    url_stats_response = URLStatsResponse(**response.data)
    assert url_stats_response.clicks == 1


test_data = [
    pytest.param("https://www.google.com", None,
                 id="구글 URL, None"),
    pytest.param("https://www.google.com", 10,
                 id="구글 URL, 10"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("url_input, expires_days_input", test_data)
async def test_get_url_stats_not_found(async_client, url_input, expires_days_input):
    """URL 통계 정보 - 잘못된 단축 URL"""
    wrong_url = "wrong_url"
    response = await async_client.get(f"/stats/{wrong_url}")
    response_json = response.json()
    response = CommonResponse(**response_json, status_code=response.status_code)
    assert response.code == ResponseType.RESOURCE_NOT_FOUND.code


test_data = [
    pytest.param("https://www.google.com", "SHORT",
                 id="구글 URL, 단축 URL"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("url_input, short_key", test_data)
async def test_delete_expired_urls(async_client, url_input, short_key):
    """만료된 URL 일괄 삭제"""
    expires_at = datetime_now_timezone() + timedelta(days=-3)
    url_models = [
        URLModel(original_url=url_input, short_key=short_key, expires_at=expires_at).to_mongo(),
        URLModel(original_url=url_input, short_key=short_key, expires_at=expires_at + timedelta(days=1)).to_mongo(),
        URLModel(original_url=url_input, short_key=short_key, expires_at=expires_at + timedelta(days=2)).to_mongo(),
    ]

    url_collection.insert_many(url_models)

    cursor = await url_collection.count_documents({})
    assert cursor == 3
    await delete_expired_urls()

    cursor = await url_collection.count_documents({})
    assert cursor == 0
