# weather_service.py
import os
import sys
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import traceback
import time
from datetime import datetime, timedelta

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

        print(f"📁 Looking for models in: {model_dir}")
        if os.path.exists(model_dir):
            print(f"📂 Found models: {os.listdir(model_dir)}")
        else:
            print("⚠️ No models folder found!")
            model_load_error = "Models directory not found"
            return

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
        # Parse target date
        target_dt = datetime.strptime(target_date, "%Y-%m-%d")
        now = datetime.now()
        
        # Calculate hours from now to target
        if target_hour == "all":
            # For all day, we need forecasts at 0, 3, 6, 9, 12, 15, 18, 21 hours
            # Calculate hours to the start of target day
            target_start = target_dt.replace(hour=0, minute=0, second=0, microsecond=0)
            hours_to_target = int((target_start - now).total_seconds() / 3600)
            
            # We need to forecast up to 21:00 on target day
            hours_needed = hours_to_target + 24
            
            print(f"🔮 Request: lat={lat}, lon={lon}, date={target_date}, time=ALL DAY")
            print(f"   Hours from now to target date start: {hours_to_target}")
            print(f"   Total hours needed: {hours_needed}")
            
            # Generate forecast with 3-hour intervals
            all_forecasts = api.get_forecast(hours=hours_needed, sample_every=3)
            
            # Filter for only the target date
            target_date_str = target_date
            forecasts = [
                f for f in all_forecasts 
                if f['datetime'].startswith(target_date_str)
            ]
            
        else:
            # For specific hour, just get that one forecast
            target_hour_int = int(target_hour)
            if target_hour_int < 0 or target_hour_int > 23:
                return JSONResponse(
                    status_code=400,
                    content={"status": "error", "message": "Hour must be between 0 and 23"}
                )
            
            target_datetime = target_dt.replace(hour=target_hour_int, minute=0, second=0, microsecond=0)
            hours_to_target = int((target_datetime - now).total_seconds() / 3600)
            
            print(f"🔮 Request: lat={lat}, lon={lon}, date={target_date}, time={target_hour}:00")
            print(f"   Hours from now to target: {hours_to_target}")
            
            if hours_to_target < 0:
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": "error",
                        "message": "Cannot forecast for past times"
                    }
                )
            
            # Generate just enough hours to reach the target (+1 for safety)
            all_forecasts = api.get_forecast(hours=hours_to_target + 2, sample_every=1)
            
            # Find the forecast closest to target time
            target_datetime_str = target_datetime.strftime("%Y-%m-%d %H:")
            forecasts = [
                f for f in all_forecasts 
                if f['datetime'].startswith(target_datetime_str)
            ]
            
            if not forecasts:
                # If exact match not found, take the closest
                forecasts = sorted(
                    all_forecasts,
                    key=lambda x: abs(
                        datetime.fromisoformat(x['datetime'].replace('Z', '+00:00').replace(' ', 'T')) - target_datetime
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

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 10000))
    print("=" * 60)
    print(f"🚀 Binding to 0.0.0.0:{port} (Render requires this)")
    print("=" * 60)

    uvicorn.run(
        "weather_service:app", 
        host="0.0.0.0", 
        port=port, 
        reload=False,
        timeout_keep_alive=120
    )