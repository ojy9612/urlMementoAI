from fastapi.openapi.utils import get_openapi


def custom_openapi(app):
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="URL Memento AI",
        version="0.0.1",
        description="URL 단축 서비스",
        routes=app.routes,
    )
    openapi_schema["components"]["responses"] = {
        "ValidationErrorResponse": {
            "description": "Validation Error",
            "content": {
                "application/json": {
                    "example": {
                        "code": "422_1",
                        "message": "유효성 검사에 실패 했습니다.",
                        "data": {
                            "url": "URL은 최소 하나의 (.)을 포함해야 합니다.",
                            "expires_days": "만료일자는 1~30일 사이로 정해야 합니다."
                        }
                    }
                }
            }
        },
        "ResourceNotFoundResponse": {
            "description": "Resource not found",
            "content": {
                "application/json": {
                    "example": {
                        "code": "404_1",
                        "message": "등록된 단축 URL이 없습니다. URL: AH64t3"
                    }
                }
            }
        },
        "ExpiredResourceResponse": {
            "description": "Expired Resource",
            "content": {
                "application/json": {
                    "example": {
                        "code": "403_1",
                        "message": "만료된 단축 URL입니다. URL: FSeBkP3"
                    }
                }
            }
        },
        "InternalServerErrorResponse": {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {
                        "code": "500_0",
                        "message": "서버측 에러"
                    }
                }
            }
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema
