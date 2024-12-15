from aiokafka import AIOKafkaConsumer
import asyncio
import json

class KafkaConsumerService:
    def __init__(self, kafka_broker: str, topic: str):
        self.kafka_broker = kafka_broker
        self.topic = topic
        self.consumer = None
        self.task = None  # Храним задачу consumer-а

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.kafka_broker,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            auto_offset_reset="earliest",
            group_id="my_consumer_group"  # Добавляем group_id для группового чтения
        )
        await self.consumer.start()
        self.task = asyncio.create_task(self.consume_messages())
        print(f"Kafka consumer started")

    async def stop(self):
        if self.consumer:
            print("Stopping Kafka consumer...")
            await self.consumer.stop()
            if self.task:
                self.task.cancel()  # Отменяем задачу
                try:
                    await self.task
                except asyncio.CancelledError:
                    print("Consumer task cancelled")
            print("Kafka consumer stopped")

    async def consume_messages(self):
        while True:  # Цикл для перезапуска в случае ошибок
            try:
                async for message in self.consumer:
                    try:
                        # Обработка сообщения
                        print(f"Received message: {message.value}")
                    except Exception as e:
                        print(f"Error processing message: {e}")
            except Exception as e:
                print(f"Error in Kafka consumer loop: {e}")
                await asyncio.sleep(5)  # Задержка перед повторной попыткой

# Инициализация глобального Kafka Consumer
kafka_consumer = KafkaConsumerService(kafka_broker="kafka:9092", topic="payment_notifications")
