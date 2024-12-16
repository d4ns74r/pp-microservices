from fastapi import FastAPI
from payment_service_app.db import engine
from payment_service_app.models import Base
from payment_service_app.routers import payments
from payment_service_app.kafka_producer import kafka_producer
from payment_service_app.logger import logger

app = FastAPI()


# Create tables and start Kafka Producer
@app.on_event("startup")
async def startup_event():
    logger.info("Application is starting. Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Tables created successfully.")
    logger.info("Starting Kafka Producer...")
    await kafka_producer.start()
    logger.info("Kafka Producer started successfully.")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application is shutting down. Stopping Kafka Producer...")
    await kafka_producer.stop()
    logger.info("Kafka Producer stopped successfully.")


# Register router
logger.info("Registering router: payments")
app.include_router(payments.router)
logger.info("Router 'payments' registered successfully.")
