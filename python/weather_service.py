# weather_service.py

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from weather_module import WeatherAPI
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize API on startup
api = None

@app.on_event("startup")
async def load_weather_model():
    global api
    print("Loading weather model...")
    try:
        api = WeatherAPI(
            "data/processed/wind_u.csv",
            "data/processed/wind_v.csv",
            "data/processed/precipitation.csv",
            "data/processed/temperature.csv",
            "data/processed/humidity.csv"
        )
        print("Weather model loaded successfully!")
    except Exception as e:
        print(f"Error loading weather model: {e}")

@app.get("/")
def root():
    return {"status": "Weather API is running", "version": "1.0"}

@app.get("/health")
def health():
    return {"status": "healthy", "api_loaded": api is not None}

@app.get("/api/weather")
def get_forecast(lat: float = Query(...), lon: float = Query(...)):
    if api is None:
        return {"error": "API not initialized"}
    
    try:
        # Get 5-year forecast
        forecasts = api.get_forecast(years=5, sample_every=30)
        
        # For demo, return first forecast entry with location info
        if forecasts:
            first_forecast = forecasts[0]
            return {
                "location": {
                    "latitude": lat,
                    "longitude": lon,
                    "name": f"{lat}, {lon}"
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
    except Exception as e:
        return {"error": f"Error generating forecast: {str(e)}"}

# This is critical for Render deployment
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)