import asyncio
import json
from aiokafka import AIOKafkaConsumer
from confluent_kafka.admin import AdminClient, NewTopic
import logging

logging.basicConfig(level=logging.INFO)

class KafkaConsumerService:
    def __init__(self, kafka_broker: str, topic: str):
        self.kafka_broker = kafka_broker
        self.topic = topic
        self.consumer = None
        self.task = None

    async def create_topic_if_not_exists(self):
        try:
            logging.info(f"Checking if topic '{self.topic}' exists...")
            admin_client = AdminClient({'bootstrap.servers': self.kafka_broker})
            metadata = admin_client.list_topics(timeout=10)

            if self.topic not in metadata.topics:
                logging.info(f"Topic '{self.topic}' not found. Creating topic...")
                new_topic = NewTopic(self.topic, num_partitions=1, replication_factor=1)
                fs = admin_client.create_topics([new_topic])
                for topic, f in fs.items():
                    try:
                        f.result()  # Блокирует до завершения
                        logging.info(f"Topic '{self.topic}' created successfully.")
                    except Exception as e:
                        logging.error(f"Failed to create topic {topic}: {e}")
            else:
                logging.info(f"Topic '{self.topic}' already exists.")
        except Exception as e:
            logging.error(f"Error creating or checking topic: {e}")

    async def start(self):
        try:
            logging.info("Waiting for Kafka to be ready...")
            await self.wait_for_kafka()

            logging.info(f"Starting Kafka consumer for topic '{self.topic}'...")

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

            logging.info(f"Connecting to Kafka...")
            await self.consumer.start()
            self.task = asyncio.create_task(self.consume_messages())
            logging.info("Kafka consumer started")
        except Exception as e:
            logging.error(f"Error starting Kafka consumer: {e}")

    async def stop(self):
        if self.consumer:
            logging.info("Stopping Kafka consumer...")
            await self.consumer.stop()
            if self.task:
                self.task.cancel()
                try:
                    await self.task
                except asyncio.CancelledError:
                    logging.info("Consumer task cancelled")
            logging.info("Kafka consumer stopped")

    async def consume_messages(self):
        while True:
            try:
                async for message in self.consumer:
                    logging.info(f"Received message: {message.value}")
            except Exception as e:
                logging.error(f"Error in Kafka consumer loop: {e}")
                await asyncio.sleep(5)  # Задержка перед повторной попыткой

    async def wait_for_kafka(self):
        retries = 12
        for _ in range(retries):
            try:
                # Пробуем получить метаданные от Kafka
                admin_client = AdminClient({'bootstrap.servers': self.kafka_broker})
                metadata = admin_client.list_topics(timeout=5)
                logging.info("Kafka is ready!")
                return
            except Exception as e:
                logging.warning(f"Kafka is not ready yet, retrying: {e}")
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
