import json
import asyncio
from .api.dependencies import get_message_queue, get_prediction_service
from .schemas.prediction import PredictionRequest
from pika import BasicProperties

mq = get_message_queue()
prediction_service = get_prediction_service()


async def async_process_message(body, inference_id):
    data = json.loads(body)
    prediction_request = PredictionRequest(**data)
    result = await prediction_service.make_prediction(prediction_request)
    await prediction_service.store_response(inference_id, result)


def process_message(ch, method, properties: BasicProperties, body):
    inference_id = properties.headers['inference_id']
    loop = asyncio.get_event_loop()
    loop.create_task(async_process_message(body, inference_id))

    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    mq.connect()
    mq.consume(process_message)


if __name__ == "__main__":
    main()
