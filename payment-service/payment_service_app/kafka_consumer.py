from aiokafka import AIOKafkaConsumer
import asyncio
import json


class KafkaConsumer:
    def __init__(self, topic="client-events", brokers="kafka:9092"):
        self.topic = topic
        self.brokers = brokers
        self.consumer = None

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.brokers,
            group_id="payment-service"
        )
        await self.consumer.start()

    async def stop(self):
        if self.consumer:
            await self.consumer.stop()

    async def consume(self, process_message):
        if not self.consumer:
            raise Exception("Kafka consumer is not started")
        async for message in self.consumer:
            message_data = json.loads(message.value.decode("utf-8"))
            await process_message(message_data)


consumer = KafkaConsumer()
