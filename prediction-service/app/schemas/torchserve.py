from pydantic import BaseModel


class TorchServeResponse(BaseModel):
    id: int
