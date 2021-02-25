from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from app import api
from app.events import setup_db, shutdown_db


def create_app(env="test"):
    app = FastAPI()
    app.add_event_handler("startup", setup_db(app, env=env))
    app.add_event_handler("shutdown", shutdown_db(env=env))
    app.include_router(api.router)
    return app


app = create_app(env="test")


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse({"errors": [exc.errors]}, status_code=400)


@app.exception_handler(HTTPException)
async def http_error_handler(request, exc: HTTPException):
    return JSONResponse({"errors": [exc.detail]}, status_code=exc.status_code)
