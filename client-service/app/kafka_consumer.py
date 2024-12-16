import asyncio
import json
from aiokafka import AIOKafkaConsumer
from confluent_kafka.admin import AdminClient, NewTopic
from app.logger import logger
from sqlalchemy.future import select
from app.models import Client
from app.db import get_db
from decimal import Decimal


class KafkaConsumerService:
    def __init__(self, kafka_broker: str, topic: str):
        self.kafka_broker = kafka_broker
        self.topic = topic
        self.consumer = None
        self.task = None

    async def create_topic_if_not_exists(self):
        try:
            logger.info(f"Checking if topic '{self.topic}' exists...")
            admin_client = AdminClient({'bootstrap.servers': self.kafka_broker})
            metadata = admin_client.list_topics(timeout=10)

            if self.topic not in metadata.topics:
                logger.info(f"Topic '{self.topic}' not found. Creating topic...")
                new_topic = NewTopic(self.topic, num_partitions=1, replication_factor=1)
                fs = admin_client.create_topics([new_topic])
                for topic, f in fs.items():
                    try:
                        f.result()  # Блокирует до завершения
                        logger.info(f"Topic '{self.topic}' created successfully.")
                    except Exception as e:
                        logger.info(f"Failed to create topic {topic}: {e}")

            else:
                logger.info(f"Topic '{self.topic}' already exists.")
        except Exception as e:
            logger.error(f"Error creating or checking topic: {e}")

    async def start(self):
        try:
            logger.info("Waiting for Kafka to be ready...")
            await self.wait_for_kafka()

            logger.info(f"Starting Kafka consumer for topic '{self.topic}'...")

            # Создание топика, если его нет
            await self.create_topic_if_not_exists()

            # Настройка и запуск потребителя
            self.consumer = AIOKafkaConsumer(
                self.topic,
                bootstrap_servers=self.kafka_broker,
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                auto_offset_reset="earliest",
                group_id="my_consumer_group"
            )

            logger.info(f"Connecting to Kafka...")
            await self.consumer.start()
            self.task = asyncio.create_task(self.consume_messages())
            logger.info("Kafka consumer started")
        except Exception as e:
            logger.error(f"Error starting Kafka consumer: {e}")

    async def stop(self):
        if self.consumer:
            logger.info("Stopping Kafka consumer...")
            await self.consumer.stop()
            if self.task:
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:
                    logger.info("Consumer task cancelled")
            logger.info("Kafka consumer stopped")

    async def consume_messages(self):
        while True:
            try:
                async for message in self.consumer:
                    logger.info(f"Received message: {message.value}")
                    msg = message.value

                    # Извлекаем данные из сообщения
                    event = msg.get("event")
                    user_id = msg.get("user_id")
                    amount = msg.get("amount")

                    # Проверяем корректность данных
                    if not all([event, user_id is not None, amount]):
                        logger.warning(f"Incomplete message: {msg}")
                        continue

                    # Обновляем баланс клиента через сессию БД
                    async with get_db() as db_session:
                        await self.update_client_balance(event, user_id, amount, db_session)
            except Exception as e:
                logger.error(f"Error in Kafka consumer loop: {e}")
                await asyncio.sleep(5)

    @staticmethod
    async def update_client_balance(event, user_id, amount, db_session):
        logger.info(f"Updating balance for user_id={user_id}, event={event}, amount={amount}")
        try:
            result = await db_session.execute(select(Client).where(Client.id == user_id))
            client = result.scalar_one_or_none()

            if not client:
                logger.warning(f"Client with ID {user_id} not found.")
                return

            amount = Decimal(amount)

            if event == 'deposit':
                client.balance += amount
            elif event == 'withdraw':
                if client.balance < amount:
                    logger.warning(f"Insufficient balance for user_id={user_id}. Transaction skipped.")
                    return
                client.balance -= amount
            else:
                logger.warning(f"Unknown event type: {event}. Skipping message.")
                return

            await db_session.commit()
            logger.info(f"Updated balance for user_id={user_id}: new balance = {client.balance}")
        except Exception as e:
            logger.error(f"Error updating balance for user_id={user_id}: {e}")
            await db_session.rollback()

    async def wait_for_kafka(self):
        retries = 12
        for _ in range(retries):
            try:
                # Пробуем получить метаданные от Kafka
                AdminClient({'bootstrap.servers': self.kafka_broker})
                logger.info("Kafka is ready!")
                return
            except Exception as e:
                logger.warning(f"Kafka is not ready yet, retrying: {e}")
                await asyncio.sleep(5)  # Ждем 5 секунд перед следующей попыткой
        raise Exception("Kafka is not available after multiple retries")


# Инициализация глобального Kafka Consumer
kafka_consumer = KafkaConsumerService(kafka_broker="kafka:9092", topic="payment_notifications")


# Пример старта
async def run():
    await kafka_consumer.start()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
