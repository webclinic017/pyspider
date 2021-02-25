from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException


async def validation_error_handler(request, exc: RequestValidationError):
    return JSONResponse({"errors": [exc.errors]}, status_code=400)


async def http_error_handler(request, exc: HTTPException):
    return JSONResponse({"errors": [exc.detail]}, status_code=exc.status_code)
