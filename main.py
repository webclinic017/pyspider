from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError

from app import api
from app.errors import http_error_handler, validation_error_handler
from app.events import setup_db, shutdown_db


def create_app(env="test"):
    if env == "test":
        debug = True
    else:
        debug = False
    app = FastAPI(debug=debug)
    app.add_event_handler("startup", setup_db(app, env=env))
    app.add_event_handler("shutdown", shutdown_db(app))

    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(HTTPException, http_error_handler)

    app.include_router(api.router)

    return app


app = create_app(env="test")


@app.get("/")
async def read_root():
    return {"Hello": "World"}
