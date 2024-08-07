from enum import Enum


class ResponseType(Enum):
    # 200
    OK = ("200_0", 200, "정상 처리 되었습니다.")

    # 400
    BAD_REQUEST = ("400_0", 400, "잘못된 요청입니다.")

    # 403
    EXPIRED_RESOURCE = ("403_1", 403, "요청한 리소스가 만료되었습니다.")

    # 404
    RESOURCE_NOT_FOUND = ("404_1", 404, "요청한 리소스를 찾을 수 없습니다.")

    # 422
    BINDING_FAILED = ("422_1", 422, "유효성 검사에 실패 했습니다.")
    # 500
    INTERNAL_SERVER_ERROR = ("500_0", 500, "서버측 에러")

    def __init__(self, code, status_code, message):
        self.code = code
        self.status_code = status_code
        self.message = message
