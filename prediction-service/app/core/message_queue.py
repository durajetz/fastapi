import asyncio
from aio_pika import connect, Message, DeliveryMode
from loguru import logger
from ..core.config import settings
import backoff


class AsyncMessageQueue:
    def __init__(self):
        self.url = settings.RABBITMQ_HOST
        self.queue_name = settings.INCOMING_QUEUE
        self.connection = None
        self.channel = None

    @backoff.on_exception(backoff.expo, ConnectionRefusedError, max_time=60)
    async def connect(self):
        try:
            self.connection = await connect(self.url)
            self.channel = await self.connection.channel()
            queue = await self.channel.declare_queue(self.queue_name, durable=True)
            await self.channel.set_qos(prefetch_count=1)
            logger.info("Connected to RabbitMQ and declared the queue.")
            return queue
        except ConnectionRefusedError as e:
            logger.error(f"Connection to RabbitMQ failed. {str(e)}")

    async def disconnect(self):
        if self.connection:
            await self.connection.close()
            logger.info("Disconnected from RabbitMQ.")

    async def publish(
        self, body: str, inference_id: str, routing_key: str | None = None
    ):
        logger.info(
            f"Publishing message with inference_id {inference_id}. Message: {body}"
        )
        routing_key = routing_key or self.queue_name
        if not self.channel or not self.connection:
            await self.connect()

        message = Message(
            body=body.encode(),
            headers={"inference_id": inference_id},
            delivery_mode=DeliveryMode.PERSISTENT,
        )

        await self.channel.default_exchange.publish(
            message,
            routing_key=routing_key,
        )
        logger.info(f"Published message to {routing_key}. Message: {body}")

    async def consume(self, callback, queue=None):
        logger.info("Starting consuming the message...")
        queue = await self.connect() if not queue else queue

        async for message in queue:
            async with message.process():
                logger.info(
                    f"Consuming message with inference_id {message.headers['inference_id']}. Message: {message.body.decode()}"
                )
                await callback(message)
