from aiokafka import AIOKafkaProducer
import asyncio
import json


class KafkaProducer:
    def __init__(self, brokers="kafka:9092"):
        self.brokers = brokers
        self.producer = None

    async def start(self):
        self.producer = AIOKafkaProducer(bootstrap_servers=self.brokers)
        await self.producer.start()

    async def stop(self):
        if self.producer:
            await self.producer.stop()

    async def send(self, topic: str, message: dict):
        if not self.producer:
            raise Exception("Kafka producer is not started")
        message_bytes = json.dumps(message).encode("utf-8")
        await self.producer.send_and_wait(topic, message_bytes)


producer = KafkaProducer()
