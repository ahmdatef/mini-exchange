from eventsourcing.application import AggregateNotFound
from fastapi import FastAPI

from common.models.errors import BadRequest
from web.models.responses import Response


def register_error_handlers(app: FastAPI):
    def aggregate_not_found_handler(request, exception):
        return Response(status_code=404, content="Not found")

    def bad_request_handler(request, exception):
        return Response(status_code=400, content=str(exception))

    app.add_exception_handler(AggregateNotFound, aggregate_not_found_handler)
    app.add_exception_handler(BadRequest, bad_request_handler)