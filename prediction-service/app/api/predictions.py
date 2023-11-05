from fastapi import APIRouter, HTTPException
from app.schemas.prediction import PredictionRequest, PredictionResponse

predictions = APIRouter(prefix="/api/v1/predictions", tags=["Predictions"])


@predictions.post('/', response_model=PredictionResponse)
async def make_prediction(payload: PredictionRequest):
    """
    Make incoming prediction requests to the requested model.
    """
    # cast_id = await db_manager.add_cast(payload)

    response = {
        'id': 12313,
        **payload.dict()
    }

    return response
