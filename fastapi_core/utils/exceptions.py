from http import HTTPStatus

from fastapi import HTTPException
from pydantic import BaseModel

REGISTER_NOT_FOUND_MESSAGE = "Item do not exist!"


class EntityNotFoundException(HTTPException):
    def __init__(self, message=REGISTER_NOT_FOUND_MESSAGE):
        super().__init__(status_code=HTTPStatus.NOT_FOUND, detail=message)


class InternalErrorSchema(BaseModel):
    detail: str = "Internal error."


#
# class EntityNotFoundExceptionSchema(BaseModel):
#     detail: str = REGISTER_NOT_FOUND_MESSAGE
#
#
# class NoContentException(HTTPException):
#     def __init__(self):
#         super().__init__(status_code=HTTPStatus.NO_CONTENT)
#
#
# class EntityAlreadyExistsException(HTTPException):
#     def __init__(self, message: str = REGISTER_ALREADY_EXISTS_MESSAGE):
#         super().__init__(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=message)
#
#
# class EntityAlreadyExistsExceptionSchema(BaseModel):
#     detail: str = REGISTER_ALREADY_EXISTS_MESSAGE
#
#
# class ErrorInProcessRequest(HTTPException):
#     def __init__(self, message: str = ERROR_IN_PROCESS_REQUEST_MESSAGE):
#         super().__init__(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=message)
#
#
# class ErrorInValidation(HTTPException):
#     def __init__(self, message: str = ERROR_IN_PROCESS_REQUEST_MESSAGE):
#         super().__init__(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=message)
#
#
# class ErrorInValidationSchema(BaseModel):
#     detail: str = ERROR_IN_PROCESS_REQUEST_MESSAGE
#
#
# class ModeInvalid(HTTPException):
#     def __init__(self, modes_valid: list):
#         super().__init__(status_code=HTTPStatus.BAD_REQUEST, detail=f"mode only accept {modes_valid}")
