from aiokafka import AIOKafkaProducer
import json
from payment_service_app.logger import logger


class KafkaProducerService:
    def __init__(self, kafka_broker: str):
        self.kafka_broker = kafka_broker
        self.producer = None

    async def start(self):
        logger.info(f"Starting kafka producer")
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.kafka_broker,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await self.producer.start()

    async def stop(self):
        logger.info(f"Kafka producer stopping")
        if self.producer:
            await self.producer.stop()

    async def send_message(self, topic: str, message: dict):
        if not self.producer:
            logger.info(f"Producer is not initialized. Call start() first.")
            raise RuntimeError("Producer is not initialized. Call start() first.")
        await self.producer.send_and_wait(topic, message)
        logger.info(f"Message sent to topic: payment_notifications -> {message}")


# Инициализация глобального Kafka Producer
kafka_producer = KafkaProducerService(kafka_broker="kafka:9092")
