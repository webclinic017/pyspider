from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import ORJSONResponse


async def validation_error_handler(request, exc: RequestValidationError):
    return ORJSONResponse({"errors": [exc.errors]}, status_code=400)


async def http_error_handler(request, exc: HTTPException):
    return ORJSONResponse({"errors": [exc.detail]}, status_code=exc.status_code)
