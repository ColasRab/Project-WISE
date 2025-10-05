# weather_service.py

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from weather_module import WeatherAPI  # your code should be in a separate module like weather_module.py
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ This allows Vercel to call your API
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
    # Get 5-year forecast
    forecasts = api.get_forecast(years=5, sample_every=30)
    
    # For demo, return first forecast entry with location info
    if forecasts:
        first_forecast = forecasts[0]
        return {
            "location": {
                "latitude": lat,
                "longitude": lon,
                "name": f"{lat}, {lon}"  # You could add reverse geocoding here
            },
            "predictions": {
                "wind_speed_ms": first_forecast["predicted_wind_u"],
                "precipitation_mm": first_forecast["predicted_precip_mm"],
                "temperature_c": first_forecast["predicted_temp_c"],
                "humidity_percent": first_forecast["predicted_humidity"]
            },
            "assessment": first_forecast["assessment"],
            "fuzzy_probabilities": {
                "wind": {
                    "calm_percent": 0,
                    "breezy_percent": 0,
                    "windy_percent": 0,
                    "very_windy_percent": 0,
                    "most_likely": first_forecast["assessment"]["wind"]["category"]
                },
                "precipitation": {
                    "dry_percent": 0,
                    "light_rain_percent": 0,
                    "moderate_rain_percent": 0,
                    "heavy_rain_percent": 0,
                    "most_likely": first_forecast["assessment"]["precipitation"]["category"]
                }
            },
            "statistics": {
                "wind": {
                    "mean": first_forecast["predicted_wind_u"],
                    "std": 0,
                    "min": 0,
                    "max": 0,
                    "p25": 0,
                    "p75": 0,
                    "p90": 0
                },
                "precipitation": {
                    "mean": first_forecast["predicted_precip_mm"],
                    "std": 0,
                    "min": 0,
                    "max": 0,
                    "p25": 0,
                    "p75": 0,
                    "p90": 0
                }
            }
        }
    
    return {"error": "No forecast available"}