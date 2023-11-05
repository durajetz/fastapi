import httpx

from app.schemas.torchserve import TorchServeResponse
from app.core.config import Config


class Client:
    """
    This is the client to TorchServe APIs service.
    """

    @property
    def client(self):
        return httpx.AsyncClient(base_url=Config.TORCH_SERVE_URL, timeout=10.0)

    async def make_prediction(self, prediction_model: str) -> TorchServeResponse:
        async with self.client as client:
            response = await client.post(prediction_model)
            return TorchServeResponse.model_validate_json(response.read())
