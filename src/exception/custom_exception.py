from src.exception.response_type import ResponseType


class CustomException(Exception):
    def __init__(self, error_type: ResponseType, message: str = None):
        self.error_type = error_type
        self.status_code = error_type.status_code
        self.detail = message if message else error_type.message
        super().__init__(self.detail)
