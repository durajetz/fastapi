import json
import magic
import mimetypes
from fastapi.responses import StreamingResponse

from loguru import logger
from ..core.message_queue import MessageQueue
from ..infrastructure.torchserve_client import TorchServeClient
from ..schemas.prediction import PredictionRequest, PredictionResponse


class PredictionService:
    def __init__(self, mq: MessageQueue, torchserve_client: TorchServeClient):
        self.mq = mq
        self.torchserve_client = torchserve_client

    async def make_prediction(self, request: PredictionRequest) -> PredictionResponse | StreamingResponse:
        self.publish_to_queue(request)

        response = await self.torchserve_client.make_prediction(request.prediction_model_name, request.image_path)
        return self.process_response(response, request.prediction_model_name)

    def publish_to_queue(self, request: PredictionRequest):
        self.mq.publish(json.dumps(request.dict()))
        logger.info(f"Published to queue: {request.dict()}")

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
        return PredictionResponse(prediction_model_name=model_name, results=response_data)

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
