from fastapi import FastAPI
from app.routers import clients
from app.db import engine
from app.models import Base

app = FastAPI()


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
