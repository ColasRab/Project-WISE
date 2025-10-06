# weather_service.py
import os
import sys
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import traceback
import time
from datetime import datetime

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
model_load_error = None


def train_models_if_needed(model_dir: str) -> bool:
    """Train models if they don't exist or are corrupted"""
    import subprocess

    required_models = [
        'wind_u_model.pkl',
        'wind_v_model.pkl',
        'precipitation_model.pkl',
        'temperature_model.pkl',
        'humidity_model.pkl'
    ]

    all_exist = all(os.path.exists(os.path.join(model_dir, m)) for m in required_models)

    if not all_exist:
        print("📚 Models not found. Training now...")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        train_script = os.path.join(script_dir, "train_models.py")

        if not os.path.exists(train_script):
            print(f"❌ Training script not found: {train_script}")
            return False

        result = subprocess.run(
            [sys.executable, train_script],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"❌ Training failed:\n{result.stderr}")
            return False

        print(f"✅ Training output:\n{result.stdout}")
        return True

    return True


@app.on_event("startup")
async def startup_event():
    global api, model_load_error
    port = os.environ.get("PORT", "8000")
    print("=" * 60)
    print("🚀 STARTUP EVENT TRIGGERED")
    print(f"🚀 Server binding to 0.0.0.0:{port}")
    print("=" * 60)

    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        model_dir = os.path.join(script_dir, "models")
        os.makedirs(model_dir, exist_ok=True)

        if not train_models_if_needed(model_dir):
            model_load_error = "Failed to train models"
            print("❌ Could not train models. API will be unavailable.")
            return

        print(f"📁 Loading models from: {model_dir}")

        from weather_module import WeatherAPI

        print("📦 Importing WeatherAPI...")
        api = WeatherAPI(model_dir=model_dir)
        print("✅ Pre-trained Prophet models loaded successfully!")

    except Exception as e:
        model_load_error = str(e)
        print(f"❌ Failed to load models: {e}")
        traceback.print_exc()


@app.get("/")
def root():
    return {
        "status": "Weather API is running",
        "version": "1.0",
        "models_loaded": api is not None,
        "model_load_error": model_load_error,
        "endpoints": {
            "health": "/health",
            "weather": "/api/weather?lat={lat}&lon={lon}&target_date={YYYY-MM-DD}&target_hour={0-23 or 'all'}"
        }
    }


@app.get("/health")
def health():
    return {
        "status": "healthy" if api is not None else "degraded",
        "models_loaded": api is not None,
        "model_load_error": model_load_error,
        "port": os.environ.get("PORT", "8000")
    }


@app.get("/api/weather")
async def get_forecast(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    target_date: str = Query(..., description="Target date (YYYY-MM-DD)"),
    target_hour: str = Query("all", description="Target hour (0-23) or 'all' for full day")
):
    """Get weather forecast for a specific date and hour."""
    start_time = time.time()

    if api is None:
        return JSONResponse(
            status_code=503,
            content={
                "status": "loading",
                "message": f"Models failed to load: {model_load_error or 'Unknown error'}",
                "location": {"latitude": lat, "longitude": lon},
                "forecast": []
            }
        )

    try:
        target_dt = datetime.strptime(target_date, "%Y-%m-%d")
        now = datetime.now()

        if target_hour == "all":
            target_start = target_dt.replace(hour=0, minute=0, second=0, microsecond=0)
            hours_to_target = int((target_start - now).total_seconds() / 3600)
            hours_needed = hours_to_target + 24

            all_forecasts = api.get_forecast(hours=hours_needed, sample_every=3)
            forecasts = [
                f for f in all_forecasts if f['datetime'].startswith(target_date)
            ]
        else:
            target_hour_int = int(target_hour)
            if target_hour_int < 0 or target_hour_int > 23:
                return JSONResponse(
                    status_code=400,
                    content={"status": "error", "message": "Hour must be between 0 and 23"}
                )

            target_datetime = target_dt.replace(hour=target_hour_int, minute=0, second=0, microsecond=0)
            hours_to_target = int((target_datetime - now).total_seconds() / 3600)

            if hours_to_target < 0:
                return JSONResponse(
                    status_code=400,
                    content={"status": "error", "message": "Cannot forecast for past times"}
                )

            all_forecasts = api.get_forecast(hours=hours_to_target + 2, sample_every=1)
            target_datetime_str = target_datetime.strftime("%Y-%m-%d %H:")

            forecasts = [
                f for f in all_forecasts if f['datetime'].startswith(target_datetime_str)
            ]

            if not forecasts:
                forecasts = sorted(
                    all_forecasts,
                    key=lambda x: abs(
                        datetime.fromisoformat(
                            x['datetime'].replace('Z', '+00:00').replace(' ', 'T')
                        ) - target_datetime
                    )
                )[:1]

        elapsed = time.time() - start_time
        print(f"✅ Generated {len(forecasts)} forecast(s) in {elapsed:.2f}s")

        if not forecasts:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "no_data",
                    "message": "No forecast data available for the requested time",
                    "location": {"latitude": lat, "longitude": lon},
                    "forecast": []
                }
            )

        return {
            "status": "success",
            "location": {"latitude": lat, "longitude": lon, "name": f"{lat}, {lon}"},
            "forecast": forecasts,
            "meta": {
                "generation_time_seconds": round(elapsed, 2),
                "forecast_count": len(forecasts),
                "target_date": target_date,
                "target_hour": target_hour
            }
        }

    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": f"Invalid date format. Use YYYY-MM-DD: {str(e)}"
            }
        )
    except Exception as e:
        print(f"❌ ERROR: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error generating forecast: {str(e)}",
                "error_type": type(e).__name__,
                "location": {"latitude": lat, "longitude": lon},
                "forecast": []
            }
        )


print("=" * 60)
print("✅ APP CREATED SUCCESSFULLY")
print("=" * 60)