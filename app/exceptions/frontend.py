from fastapi import HTTPException


class FrontendHttpException(HTTPException):
    pass


class FrontendNotAuthException(FrontendHttpException):
    pass
