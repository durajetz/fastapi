import json
import asyncio
from loguru import logger
from app.api.dependencies import (
    get_message_queue,
    get_prediction_service,
    get_redis_client,
    get_torchserve_client,
)
from app.schemas.prediction import PredictionRequest

mq = get_message_queue()
redis_client = get_redis_client()
torchserve_client = get_torchserve_client()
prediction_service = get_prediction_service(mq, torchserve_client, redis_client)


async def process_message(message):
    body = message.body.decode()
    inference_id = message.headers.get("inference_id")

    logger.info(f"Received message for inference ID: {inference_id}. Message: {body}")

    try:
        data = json.loads(body)
        prediction_request = PredictionRequest(**data)
        logger.info(f"Processing request: {prediction_request}")

        try:
            result = await prediction_service.make_prediction(prediction_request)
        except Exception:
            result = json.dumps(
                {
                    "prediction_model_name": prediction_request.prediction_model_name,
                    "results": "Error while making the prediction.",
                }
            )
        await prediction_service.store_response(inference_id, result)

        logger.info(f"Processed message for inference ID: {inference_id}")
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
    except Exception as e:
        logger.error(f"Failed to process message: {e}")


async def main():
    await asyncio.sleep(10)
    await mq.connect()
    await mq.consume(process_message)


if __name__ == "__main__":
    asyncio.run(main())
