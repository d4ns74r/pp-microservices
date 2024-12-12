from fastapi import FastAPI, Request
from app.routers import clients
from app.db import engine
from app.models import Base
from app.logger import logger
import time

app = FastAPI()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"Completed response: {response.status_code} in {process_time: .2f}s"
    )
    return response


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(clients.router)


# Подключаем роуты
app.include_router(clients.router)


# Эндпоинт для проверки работы сервиса
@app.get("/")
def read_root():
    return {"message": "Client service running"}
