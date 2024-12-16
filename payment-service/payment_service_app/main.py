from fastapi import FastAPI
from payment_service_app.db import engine
from payment_service_app.models import Base
from payment_service_app.routers import payments
from payment_service_app.kafka_producer import kafka_producer
import asyncio

app = FastAPI()

# Создание таблиц и запуск Kafka Producer
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await kafka_producer.start()

@app.on_event("shutdown")
async def shutdown_event():
    await kafka_producer.stop()

# Регистрация роутера
app.include_router(payments.router)
