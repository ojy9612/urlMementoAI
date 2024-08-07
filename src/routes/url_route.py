from fastapi import APIRouter, Path
from starlette.responses import RedirectResponse

from src.config.transactional import transactional
from src.models.common_response_model import CommonResponseModel
from src.schemas.common_response import CommonResponse
from src.schemas.url_schema import URLCreateRequest, URLStatsResponse, URLResponse
from src.service.url_service import get_original_url, get_url_stats, create_shorten_url

router = APIRouter()


@router.post("/shorten",
             response_model=CommonResponseModel[URLResponse],
             summary="단축 URL 생성",
             description="URL을 Redirect시키는 단축키와 만료일자를 생성합니다.  \n  \n"
                         " - url : **required** (.)을 포함하는 문자열 입력  \n"
                         " - expires_days : 1~30 사이의 정수 입력 (미입력시 만료기한이 없습니다.)  \n \n"
                         "expries_at이 제공되지 않았다면 만료되지 않는 URL입니다.  \n"
                         "매일 자정에 만료된 URL이 삭제됩니다.",
             responses={
                 "422": {"$ref": "#/components/responses/ValidationErrorResponse"},
                 "500": {"$ref": "#/components/responses/InternalServerErrorResponse"},
             })
async def shorten_url(url_create: URLCreateRequest) -> CommonResponse:
    data = await create_shorten_url(url_create)
    return CommonResponse.success(data=data)


@router.get("/{short_key}",
            summary="원본 URL로 리다이렉션",
            description="단축 URL을 원본 URL로 Redirect시킵니다.  \n  \n"
                        " - short_key : **required** 단축 URL",
            responses={
                "403": {"$ref": "#/components/responses/ExpiredResourceResponse"},
                "404": {"$ref": "#/components/responses/ResourceNotFoundResponse"},
                "500": {"$ref": "#/components/responses/InternalServerErrorResponse"},
                "422": {},
            })
@transactional
async def redirect_url(short_key: str = Path(..., example="AH64t3", description="단축 URL")) -> RedirectResponse:
    original_url = await get_original_url(short_key)
    return RedirectResponse(url=original_url, status_code=301)


@router.get("/stats/{short_key}",
            response_model=CommonResponseModel[URLStatsResponse],
            summary="URL 통계 조회",
            description="단축 URL의 리다이렉션 횟수를 조회합니다.  \n  \n"
                        " - short_key : **required** 단축 URL",
            responses={
                "404": {"$ref": "#/components/responses/ResourceNotFoundResponse"},
                "500": {"$ref": "#/components/responses/InternalServerErrorResponse"},
                "422": {},
            })
@transactional
async def url_stats(short_key: str = Path(..., example="AH64t3", description="단축 URL")) -> CommonResponse:
    data = await get_url_stats(short_key)
    return CommonResponse.success(data=data)
