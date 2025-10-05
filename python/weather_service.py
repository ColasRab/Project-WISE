# weather_service.py

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from weather_module import WeatherAPI  # your code should be in a separate module like weather_module.py
import json

app = FastAPI()

# Allow CORS if calling from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # update this in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize API on startup
@app.on_event("startup")
def load_weather_model():
    global api
    api = WeatherAPI(
        "data/processed/wind_u.csv",
        "data/processed/wind_v.csv",
        "data/processed/precipitation.csv",
        "data/processed/temperature.csv",
        "data/processed/humidity.csv"
    )



@app.get("/api/weather")
def get_forecast(lat: float = Query(...), lon: float = Query(...)):
    result = api.get_forecast(lat, lon)
    return result
