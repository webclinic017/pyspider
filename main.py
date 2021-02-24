from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from app import api

app = FastAPI()
app.include_router(api.router)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)


@app.exception_handler(HTTPException)
async def http_error_handler(request, exc: HTTPException):
    return JSONResponse({"errors": [exc.detail]}, status_code=exc.status_code)
