import asyncio
import httpx
from loguru import logger
from aiolimiter import AsyncLimiter
from ..domain.exceptions.domain_exceptions import EntityNotFoundException, ServerException
from ..core.config import settings


class TorchServeClient:
    rate_limiter = AsyncLimiter(
        settings.RATE_LIMITER_MAX_TOKENS,
        settings.RATE_LIMITER_REFILL_TIME
    )

    def __init__(self, host: str):
        self.host = host
        self._client = httpx.AsyncClient(base_url=self.host, timeout=30.0)

    async def close(self):
        await self._client.aclose()

    @staticmethod
    async def read_image_data(image_path: str) -> bytes:
        return await asyncio.to_thread(TorchServeClient._read_image_file, image_path)

    @staticmethod
    def _read_image_file(image_path: str) -> bytes:
        with open(image_path, 'rb') as f:
            return f.read()

    async def _handle_http_exception(self, e: httpx.HTTPStatusError):
        if e.response.status_code == 404:
            logger.error("Model not found for prediction.")
            raise EntityNotFoundException(
                detail="Model not found for prediction.")
        else:
            logger.error(
                f"Server error occurred while making a prediction: {str(e)}")
            raise ServerException(
                status_code=e.response.status_code, detail=str(e))

    async def make_prediction(self, prediction_model: str, image_path: str) -> httpx.Response:
        try:
            await asyncio.wait_for(self.rate_limiter.acquire(), timeout=1.0)
        except asyncio.TimeoutError as e:
            logger.error("Rate limit exceeded. Please try again later.")
            raise ServerException(detail=str(e))

        logger.info(f"Prediction start for model {prediction_model}.")

        image_data = await self.read_image_data(image_path)

        async def prediction_task():
            if prediction_model == 'nst':
                return await self._client.post(
                    f"predictions/{prediction_model}",
                    files={
                        'file1': ('image1.jpg', image_data, 'image/jpeg'),
                        'file2': ('image2.jpg', image_data, 'image/jpeg')
                    }
                )
            else:
                return await self._client.post(
                    f"predictions/{prediction_model}",
                    content=image_data,
                    headers={'Content-Type': 'application/octet-stream'}
                )

        try:
            response = await asyncio.wait_for(prediction_task(), timeout=settings.PREDICTION_TIMEOUT)
            response.raise_for_status()
        except asyncio.TimeoutError:
            logger.error("Prediction request timed out.")
            raise ServerException(
                status_code=504, detail="Prediction request timed out, please try again later.")
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            logger.error(
                f"HTTP error occurred while making a prediction: {str(e)}")
            raise ServerException(detail=str(e))

        logger.info(
            f"Prediction made successfully for model {prediction_model}.")
        return response
