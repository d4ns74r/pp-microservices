from aiokafka import AIOKafkaProducer
import json

class KafkaProducerService:
    def __init__(self, kafka_broker: str):
        self.kafka_broker = kafka_broker
        self.producer = None

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.kafka_broker,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await self.producer.start()

    async def stop(self):
        if self.producer:
            await self.producer.stop()

    async def send_message(self, topic: str, message: dict):
        if not self.producer:
            raise RuntimeError("Producer is not initialized. Call start() first.")
        await self.producer.send_and_wait(topic, message)
        print(f"Message sent to topic: payment_notifications -> {message}")

# Инициализация глобального Kafka Producer
kafka_producer = KafkaProducerService(kafka_broker="kafka:9092")
