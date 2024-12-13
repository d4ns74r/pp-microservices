from fastapi import FastAPI
from payment_service_app.db import engine
from payment_service_app.models import Base
from payment_service_app.routers import payments

app = FastAPI()


# Создание таблиц при запуске сервера
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(payments.router)
