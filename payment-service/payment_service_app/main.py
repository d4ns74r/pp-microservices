from fastapi import FastAPI
from payment_service_app.db import engine
from payment_service_app.models import Base
from payment_service_app.routers import payments
from payment_service_app.kafka_consumer import consumer  # Импорт Kafka Consumer
import asyncio

app = FastAPI()


# Создание таблиц при запуске сервера
@app.on_event("startup")
async def startup_event():
    # Запуск создания таблиц
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Запуск Kafka Consumer
    await consumer.start()
    asyncio.create_task(consumer.consume(process_kafka_message))


@app.on_event("shutdown")
async def shutdown_event():
    # Остановка Kafka Consumer
    await consumer.stop()


# Обработчик сообщений из Kafka
async def process_kafka_message(message):
    print(f"Получено сообщение из Kafka: {message}")
    # Логика обработки сообщения здесь


# Регистрация роутера
app.include_router(payments.router)
