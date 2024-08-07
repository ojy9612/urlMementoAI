import logging

from fastapi import FastAPI

from src.batch.scheduler import start_scheduler
from src.config.swagger_config import custom_openapi
from src.exception import exception_setup
from src.routes.url_route import router as url_router

app = FastAPI()

app.include_router(url_router)
exception_setup.setup_exception_handlers(app)
custom_openapi(app)
start_scheduler()
logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
