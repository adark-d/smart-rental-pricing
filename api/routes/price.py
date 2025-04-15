import mlflow.pyfunc
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

model_uri = "models:/rental_price_model/Production"
model = mlflow.pyfunc.load_model(model_uri)


class PriceInput(BaseModel):
    bedrooms: int
    area_m2: float
    has_furniture: bool


@router.post("/")
def predict_price(input_data: PriceInput):
    features = {
        "bedrooms": [input_data.bedrooms],
        "area_m2": [input_data.area_m2],
        "has_furniture": [int(input_data.has_furniture)],
    }
    prediction = model.predict(features)
    return {"predicted_price": float(prediction[0])}
