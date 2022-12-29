import enum
import typing

from pydantic.generics import GenericModel
from starlette.background import BackgroundTask
from starlette.responses import JSONResponse


class Status(str, enum.Enum):
    OK = "OK"
    ERROR = "ERROR"


T = typing.TypeVar('T')


class Content(GenericModel, typing.Generic[T]):
    status: Status = Status.OK
    details: T = None


class Response(JSONResponse):

    def __init__(self, content: typing.Any, status_code: int = 200,
                 headers: typing.Optional[typing.Dict[str, str]] = None, media_type: typing.Optional[str] = None,
                 background: typing.Optional[BackgroundTask] = None) -> None:
        if status_code >= 400:
            content = {
                'status': 'ERROR',
                'details': content
            }
        else:
            content = {
                'status': 'OK',
                'details': content
            }
        super().__init__(content, status_code, headers, media_type, background)
