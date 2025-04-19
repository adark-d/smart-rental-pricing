from fastapi import FastAPI

from app.api.v1.endpoints import listings, meta
from app.api.v1.endpoints.health import health_check
from app.core.tags import tags_metadata
from src.utils.settings import settings

app = FastAPI(
    title="Smart Rental Pricing API",
    description="Backend API for inserting and retrieving real estate listings in Ghana.",
    version="1.0.0",
    contact={"name": "David Adarkwah", "email": f"{settings.API_EMAIL}"},
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata,
)

app.include_router(listings.router, prefix="", tags=["Listings"])
app.include_router(meta.router, prefix="", tags=["Meta"])
app.add_api_route("/", endpoint=health_check, methods=["GET"], tags=["Health"])
