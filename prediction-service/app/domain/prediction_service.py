import base64
import json
import pickle
import uuid
import magic
import mimetypes
from fastapi.responses import StreamingResponse

from loguru import logger
from ..core.message_queue import MessageQueue
from ..infrastructure.torchserve_client import TorchServeClient
from ..infrastructure.redis_client import RedisClient
from ..schemas.prediction import PredictionRequest, PredictionResponse
from ..domain.exceptions.domain_exceptions import EntityNotFoundException, ServerException


class PredictionService:
    def __init__(self, mq: MessageQueue, torchserve_client: TorchServeClient, redis_client: RedisClient):
        self.mq = mq
        self.torchserve_client = torchserve_client
        self.redis_client = redis_client

    async def publish_prediction(self, request: PredictionRequest) -> str:
        inference_id = str(uuid.uuid4())
        logger.info(
            f"Publishing prediction with request {request} and inference_id: {inference_id}")
        self.publish_to_queue(request, inference_id)
        self.redis_client.set(inference_id, json.dumps({"status": "pending"}))
        return inference_id

    async def make_prediction(self, request: PredictionRequest) -> PredictionResponse | StreamingResponse:
        response = await self.torchserve_client.make_prediction(request.prediction_model_name, request.image_path)
        return self.process_response(response, request.prediction_model_name)

    async def store_response(self, inference_id: str, result):
        logger.info(
            f"Storing prediction results with inference_id: {inference_id}")
        stored_data = {}

        if isinstance(result, PredictionResponse):
            stored_data = {
                "type": "PredictionResponse",
                "content": result.dict()
            }
        elif isinstance(result, StreamingResponse):
            base64_content = await self.encode_streaming_response_to_base64(result)
            stored_data = {
                "type": "StreamingResponse",
                "content": base64_content,
                "content_type": result.media_type
            }
        else:
            logger.error(
                f"Unsupported result type for inference_id: {inference_id}")

        if stored_data:
            self.redis_client.set(inference_id, json.dumps(stored_data))

    async def encode_streaming_response_to_base64(self, streaming_response: StreamingResponse):
        full_body_bytes = b''

        async for data in streaming_response.body_iterator:
            if isinstance(data, str):
                data = data.encode('utf-8')
            full_body_bytes += data

        return base64.b64encode(full_body_bytes).decode('utf-8')

    def get_response_from_inference_id(self, inference_id: str):
        logger.info(
            f"Retrieving prediction results with inference_id: {inference_id}")

        raw_result = self.redis_client.get(inference_id)
        if not raw_result:
            raise EntityNotFoundException(
                f"No result found for inference_id {inference_id}")

        logger.info(
            f"Value {raw_result} of redis with key: {inference_id}")

        decoded_result = None

        if isinstance(raw_result, bytes):
            decoded_result = raw_result.decode('utf-8')

        if decoded_result is None:
            raise ServerException(
                detail=f"Failed to decode result for inference_id {inference_id}")

        result_data = json.loads(decoded_result)

        if result_data['type'] == "StreamingResponse":
            content_type = result_data["content_type"]
            data = result_data["data"].encode()
            return StreamingResponse(content=data, media_type=content_type)
        elif result_data['type'] == "PredictionResponse":
            return PredictionResponse(**result_data['content'])
        else:
            raise ServerException(detail="Unsupported response type")

    def publish_to_queue(self, request: PredictionRequest, inference_id: str):
        request_dict = request.dict()
        self.mq.publish(json.dumps(request_dict), inference_id)
        logger.info(
            f"Published to queue: {request_dict} with inference id {inference_id}")

    def process_response(self, response, model_name) -> PredictionResponse | StreamingResponse:
        try:
            response_text = response.content.decode('utf-8')
            if response_text and (response_text.strip()[0] in '{['):
                return self.handle_json_response(response_text, model_name)
        except UnicodeDecodeError:
            return self.handle_binary_response(response.content, model_name)

        return PredictionResponse(prediction_model_name=model_name, results="Unsupported response type")

    def handle_json_response(self, response_text, model_name) -> PredictionResponse:
        response_data = json.loads(response_text)
        logger.info(
            f"JSON Prediction output for model {model_name}: {response_data}")
        return PredictionResponse(prediction_model_name=model_name,
                                  results=response_data)

    def handle_binary_response(self, response_content, model_name) -> StreamingResponse:
        logger.info("Handling binary response data.")
        content_type = magic.from_buffer(response_content, mime=True)
        file_extension = mimetypes.guess_extension(content_type) or ''
        logger.info(f"Binary content type: {content_type}")
        return StreamingResponse(
            iter([response_content]),
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename={model_name}_output{file_extension}"
            }
        )
