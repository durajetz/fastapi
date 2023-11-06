from fastapi import HTTPException
import httpx
from loguru import logger

from app.schemas.torchserve import TorchServeResponse


class TorchServeClient:
    """
    This is the client to TorchServe APIs service.
    """

    def __init__(self, host):
        self.host = host

    @property
    def client(self):
        return httpx.AsyncClient(base_url=self.host, timeout=30.0)

    async def make_prediction(self, prediction_model: str, data):
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
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                logger.error(
                    f"An error occurred while making a prediction: {str(e)}")
                # logger.exception(e)
                raise HTTPException(
                    status_code=500, detail="Internal server error occurred while making a prediction.")
