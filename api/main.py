from fastapi import FastAPI

from api.routes import price, recommend

app = FastAPI(title="Rental Pricing API")

app.include_router(price.router, prefix="/predict")
app.include_router(recommend.router, prefix="/recommend")
