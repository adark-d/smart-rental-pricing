from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Health check endpoint")
def health_check():
    return {
        "status": "ok",
        "message": "Smart Rental Pricing API is running",
        "version": "1.0.0",
    }
