# weather_service.py
import os
import sys
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from weather_module import WeatherAPI

print("=" * 60)
print("STARTING WEATHER SERVICE")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"PORT environment variable: {os.environ.get('PORT', 'NOT SET')}")
print("=" * 60)

app = FastAPI(title="Weather API", version="1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global API instance
api = None


@app.on_event("startup")
async def startup_event():
    global api
    port = os.environ.get("PORT", "8000")
    print("=" * 60)
    print("🚀 STARTUP EVENT TRIGGERED")
    print(f"🚀 Server binding to 0.0.0.0:{port}")
    print("=" * 60)

    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        model_dir = os.path.join(script_dir, "models")

        print(f"📁 Looking for models in: {model_dir}")
        if os.path.exists(model_dir):
            print(f"📂 Found models: {os.listdir(model_dir)}")
        else:
            print("⚠️ No models folder found!")

        api = WeatherAPI(model_dir=model_dir)
        print("✅ Pre-trained Prophet models loaded successfully!")
    except Exception as e:
        print(f"❌ Failed to load models: {e}")
        import traceback
        traceback.print_exc()


@app.get("/")
def root():
    return {
        "status": "Weather API is running",
        "version": "1.0",
        "models_loaded": api is not None,
        "endpoints": {
            "health": "/health",
            "weather": "/api/weather?lat={latitude}&lon={longitude}&hours={hours}"
        }
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "models_loaded": api is not None,
        "port": os.environ.get("PORT", "8000")
    }


@app.get("/api/weather")
def get_forecast(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    hours: int = Query(24, description="Forecast horizon in hours (default: 24)")
):
    """Get weather forecast for a specific location (hourly resolution)."""

    if api is None:
        return {
            "status": "loading",
            "message": "Models are still warming up or failed to load.",
            "location": {"latitude": lat, "longitude": lon},
            "forecast": []
        }

    try:
        print(f"🔮 Generating forecast for lat={lat}, lon={lon}, hours={hours}")
        # Changed sample_every=1 for hourly forecasts
        forecasts = api.get_forecast(hours=hours, sample_every=1)

        if not forecasts:
            return {
                "status": "no_data",
                "message": "No forecast data available",
                "location": {"latitude": lat, "longitude": lon},
                "forecast": []
            }

        return {
            "status": "success",
            "location": {"latitude": lat, "longitude": lon, "name": f"{lat}, {lon}"},
            "forecast": forecasts
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"Error generating forecast: {str(e)}",
            "location": {"latitude": lat, "longitude": lon},
            "forecast": []
        }

print("=" * 60)
print("✅ APP CREATED SUCCESSFULLY")
print("=" * 60)

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 10000))  # Render defaults to 10000
    print("=" * 60)
    print(f"🚀 Binding to 0.0.0.0:{port} (Render requires this)")
    print("=" * 60)

    uvicorn.run("weather_service:app", host="0.0.0.0", port=port, reload=False)