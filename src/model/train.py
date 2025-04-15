import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

df = pd.read_csv("data/processed/clean_rentals.csv")
X = df[["bedrooms", "area_m2", "has_furniture"]]
y = df["price"]

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

preds = model.predict(X)
mae = mean_absolute_error(y, preds)

with mlflow.start_run():
    mlflow.log_param("model_type", "RandomForest")
    mlflow.log_metric("mae", mae)
    mlflow.sklearn.log_model(model, "model")

    # Save locally for FastAPI
    joblib.dump(model, "src/model/rent_model.pkl")
