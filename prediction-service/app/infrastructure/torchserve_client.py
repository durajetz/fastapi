import httpx
from httpx import Response
from loguru import logger
from app.domain.exceptions.domain_exceptions import EntityNotFoundException, ServerException


class TorchServeClient:
    """
    This is the client to TorchServe APIs service.
    """

    def __init__(self, host):
        self.host = host

    @property
    def client(self):
        return httpx.AsyncClient(base_url=self.host, timeout=30.0)

    async def make_prediction(self, prediction_model: str, data) -> Response:
        logger.info(
            f"Prediction start for model {prediction_model}.")
        async with self.client as client:
            try:
                with open("/data/cat.jpg", 'rb') as f:
                    image_data = f.read()

                response = await client.post(
                    f"predictions/{prediction_model}",
                    content=image_data,
                    headers={'Content-Type': 'application/octet-stream'}
                )
                response.raise_for_status()
                logger.info(
                    f"Prediction made successfully for model {prediction_model}.")
                return response
            except httpx.HTTPStatusError as e:
                logger.error(
                    f"HTTP error occurred while making a prediction: {str(e)}")
                if e.response.status_code == 404:
                    raise EntityNotFoundException(
                        detail="Model not found for prediction.")
                else:
                    raise ServerException(status_code=e.response.status_code,
                                          detail="Server error occurred while making a prediction.")
            except httpx.RequestError as e:
                logger.error(
                    f"Request error occurred while making a prediction: {str(e)}")
                raise ServerException(
                    detail="Internal server error occurred while making a prediction.")
