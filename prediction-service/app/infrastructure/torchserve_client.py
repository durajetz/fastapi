import asyncio
import httpx
from httpx import Response
from loguru import logger
from aiolimiter import AsyncLimiter
from app.domain.exceptions.domain_exceptions import EntityNotFoundException, ServerException
from app.core.config import settings


class TorchServeClient:
    rate_limiter = AsyncLimiter(
        settings.RATE_LIMITER_MAX_TOKENS,
        settings.RATE_LIMITER_REFILL_TIME
    )

    def __init__(self, host):
        self.host = host
        self._client = httpx.AsyncClient(base_url=self.host, timeout=30.0)

    async def close(self):
        await self._client.aclose()

    async def make_prediction(self, prediction_model: str, data) -> Response:
        try:
            await asyncio.wait_for(self.rate_limiter.acquire(), timeout=1.0)
        except asyncio.TimeoutError:
            logger.error("Rate limit exceeded. Please try again later.")
            raise ServerException(
                detail="Rate limit exceeded, please try again later.")

        logger.info(f"Prediction start for model {prediction_model}.")

        async def post_request():
            with open("/data/cat.jpg", 'rb') as f:
                image_data = f.read()

            return await self._client.post(
                f"predictions/{prediction_model}",
                content=image_data,
                headers={'Content-Type': 'application/octet-stream'}
            )

        prediction_task = asyncio.create_task(post_request())

        try:
            response = await asyncio.wait_for(prediction_task, timeout=settings.PREDICTION_TIMEOUT)
            response.raise_for_status()
            logger.info(
                f"Prediction made successfully for model {prediction_model}.")
            return response

        except asyncio.TimeoutError:
            prediction_task.cancel()
            logger.error("Prediction request timed out.")
            raise ServerException(
                status_code=504,
                detail="Prediction request timed out, please try again later."
            )
        except httpx.HTTPStatusError as e:
            prediction_task.cancel()
            logger.error(
                f"HTTP error occurred while making a prediction: {str(e)}")
            if e.response.status_code == 404:
                raise EntityNotFoundException(
                    detail="Model not found for prediction."
                )
            else:
                raise ServerException(
                    status_code=e.response.status_code,
                    detail="Server error occurred while making a prediction."
                )
        except httpx.RequestError as e:
            prediction_task.cancel()
            logger.error(
                f"Request error occurred while making a prediction: {str(e)}")
            raise ServerException(
                detail="Internal server error occurred while making a prediction."
            )
