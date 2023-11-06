from loguru import logger
import pika
from pika.exceptions import AMQPError
from ..core.config import settings


class MessageQueue:
    def __init__(self):
        self.url = settings.RABBITMQ_HOST
        self.params = pika.URLParameters(self.url)
        self.connection = None
        self.channel = None

    def connect(self):
        try:
            self.connection = pika.BlockingConnection(self.params)
            self.channel = self.connection.channel()
            # Declare the queue, in case it doesn't exist
            self.channel.queue_declare(queue='prediction_queue', durable=True)
            logger.info("Connected to RabbitMQ and declared the queue.")
        except AMQPError as err:
            print(f"An error occurred connecting to RabbitMQ: {err}")
            raise

    def disconnect(self):
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from RabbitMQ.")

    def publish(self, body, routing_key='prediction_queue'):
        try:
            if not self.connection or self.connection.is_closed:
                self.connect()
            if self.channel and self.channel.is_open:
                self.channel.basic_publish(
                    exchange='',
                    routing_key=routing_key,
                    body=body,
                    properties=pika.BasicProperties(delivery_mode=2)
                )
                logger.info(
                    f"Published message to {routing_key}. Message: {body}")
            else:
                logger.warning("Channel is not open. Message not sent.")
        except AMQPError as err:
            logger.error(f"An error occurred publishing a message: {err}")
            # Handle reconnection, etc.
            self.connect()
            raise

    def consume(self, callback, queue='prediction_queue'):
        try:
            if not self.connection or self.connection.is_closed:
                self.connect()
            if self.channel and self.channel.is_open:
                self.channel.basic_consume(
                    queue=queue,
                    on_message_callback=callback,
                    auto_ack=True
                )
                self.channel.start_consuming()
            else:
                logger.warning("Channel is not open. Message not sent.")
        except AMQPError as err:
            logger.error(f"An error occurred publishing a message: {err}")
            raise
