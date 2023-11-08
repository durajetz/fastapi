from loguru import logger
import pika
from pika.exceptions import AMQPError, ChannelClosedByBroker
from ..core.config import settings
from time import sleep
import backoff


class MessageQueue:
    def __init__(self):
        self.url = settings.RABBITMQ_HOST
        self.queue_name = settings.INCOMING_QUEUE
        self.params = pika.URLParameters(self.url)
        self.connection = None
        self.channel = None

    @backoff.on_exception(backoff.expo, AMQPError, max_tries=8)
    def connect(self):
        self.connection = pika.BlockingConnection(self.params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)
        self.channel.basic_qos(prefetch_count=1)
        logger.info("Connected to RabbitMQ and declared the queue.")

    def disconnect(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Disconnected from RabbitMQ.")

    @backoff.on_exception(backoff.expo, AMQPError, max_tries=8)
    def publish(self, body, inference_id: str, routing_key=None):
        routing_key = routing_key or self.queue_name
        if not self.connection or self.connection.is_closed:
            self.connect()
        if self.channel and self.channel.is_open:
            self.channel.basic_publish(
                exchange='',
                routing_key=routing_key,
                body=body,
                properties=pika.BasicProperties(
                    headers={'inference_id': inference_id},
                    delivery_mode=2,
                )
            )
            logger.info(f"Published message to {routing_key}. Message: {body}")
        else:
            logger.warning("Channel is not open. Message not sent.")

    def consume(self, callback, queue=None):
        queue = queue or self.queue_name
        if not self.connection or self.connection.is_closed:
            self.connect()
        if self.channel and self.channel.is_open:
            def wrapped_callback(ch, method, properties, body):
                try:
                    callback(ch, method, properties, body)
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag)

            self.channel.basic_consume(
                queue=queue,
                on_message_callback=wrapped_callback,
                auto_ack=False
            )
            try:
                self.channel.start_consuming()
            except ChannelClosedByBroker:
                logger.error(
                    "Channel was closed by broker, attempting to reconnect.")
                self.connect()
                self.consume(callback, queue)
            except KeyboardInterrupt:
                logger.info("Consumer was stopped by user.")
        else:
            logger.warning("Channel is not open. Cannot consume messages.")
