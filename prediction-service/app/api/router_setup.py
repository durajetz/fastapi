from fastapi import APIRouter
from .routes.predictions import predictions

router = APIRouter()
router.include_router(predictions, prefix="/predictions", tags=["predictions"])