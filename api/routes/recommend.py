import pandas as pd
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

df = pd.read_csv("data/processed/clean_rentals.csv")


class RecommenderInput(BaseModel):
    bedrooms: int
    area_m2: float
    price: float


@router.post("/")
def recommend(input_data: RecommenderInput):
    candidates = df.copy()
    candidates["distance"] = (
        (candidates["bedrooms"] - input_data.bedrooms).abs()
        + (candidates["area_m2"] - input_data.area_m2).abs() / 10
        + (candidates["price"] - input_data.price).abs() / 100
    )
    top = candidates.sort_values("distance").head(5)
    return top[["title", "price", "location"]].to_dict(orient="records")
