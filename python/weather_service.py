# weather_service.py
import os
import sys
from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from weather_module import WeatherAPI
import threading


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
    print(f"🚀 Server should start on 0.0.0.0:{port}")
    print("=" * 60)

    def load_models():
        global api
        try:
            print("📊 Loading weather data and training Prophet models (in background)...")
            script_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(script_dir, "data", "processed")

            print(f"📁 Data directory: {data_dir}, exists={os.path.exists(data_dir)}")
            if os.path.exists(data_dir):
                print(f"📁 Files in data dir: {os.listdir(data_dir)}")

            api = WeatherAPI(
                os.path.join(data_dir, "wind_u.csv"),
                os.path.join(data_dir, "wind_v.csv"),
                os.path.join(data_dir, "precipitation.csv"),
                os.path.join(data_dir, "temperature.csv"),
                os.path.join(data_dir, "humidity.csv"),
            )
            print("✅ Prophet models loaded successfully!")
        except Exception as e:
            print(f"⚠️  Warning: Could not load Prophet models: {e}")
            import traceback
            traceback.print_exc()


    threading.Thread(target=load_models, daemon=True).start()

@app.get("/")
def root():
    print("✅ ROOT ENDPOINT HIT")
    return {
        "status": "Weather API is running",
        "version": "1.0",
        "models_loaded": api is not None,
        "endpoints": {
            "health": "/health",
            "weather": "/api/weather?lat={latitude}&lon={longitude}"
        }
    }

@app.get("/health")
def health():
    print("✅ HEALTH ENDPOINT HIT")
    return {
        "status": "healthy",
        "models_loaded": api is not None,
        "port": os.environ.get("PORT", "8000")
    }

@app.get("/api/weather")
def get_forecast(lat: float = Query(..., description="Latitude"), 
                 lon: float = Query(..., description="Longitude")):
    """Get weather forecast for a specific location"""
    
    if api is None:
        raise HTTPException(
            status_code=503,
            detail="Prophet models not loaded. Check server logs for data file errors."
        )
    
    try:
        print(f"🔮 Generating forecast for lat={lat}, lon={lon}")
        forecasts = api.get_forecast(years=5, sample_every=30)
        
        if not forecasts or len(forecasts) == 0:
            raise Exception("No forecast data available")
        
        first = forecasts[0]
        wind_u = first["predicted_wind_u"]
        wind_v = first["predicted_wind_v"]
        wind_speed = round((wind_u**2 + wind_v**2)**0.5, 2)
        precip = first["predicted_precip_mm"]
        temp = first["predicted_temp_c"]
        humidity = first["predicted_humidity"]
        assessment = first["assessment"]
        
        def calc_stats(values):
            if not values:
                return {"mean": 0, "std": 0, "min": 0, "max": 0, "p25": 0, "p75": 0, "p90": 0}
            import statistics
            sorted_vals = sorted(values)
            n = len(sorted_vals)
            return {
                "mean": round(statistics.mean(values), 2),
                "std": round(statistics.stdev(values) if n > 1 else 0, 2),
                "min": round(min(values), 2),
                "max": round(max(values), 2),
                "p25": round(sorted_vals[n//4], 2),
                "p75": round(sorted_vals[3*n//4], 2),
                "p90": round(sorted_vals[int(n*0.9)] if n > 10 else sorted_vals[-1], 2),
            }
        
        wind_speeds = [(f["predicted_wind_u"]**2 + f["predicted_wind_v"]**2)**0.5 for f in forecasts]
        precip_vals = [f["predicted_precip_mm"] for f in forecasts]
        temp_vals = [f["predicted_temp_c"] for f in forecasts]
        humidity_vals = [f["predicted_humidity"] for f in forecasts]
        
        print(f"✅ Forecast generated successfully")
        
        return {
            "location": {"latitude": lat, "longitude": lon, "name": f"{lat}, {lon}"},
            "predictions": {
                "wind_speed_ms": wind_speed,
                "precipitation_mm": precip,
                "temperature_c": temp,
                "humidity_percent": humidity
            },
            "assessment": assessment,
            "fuzzy_probabilities": {
                "wind": {
                    "calm_percent": 20.0,
                    "breezy_percent": 40.0,
                    "windy_percent": 30.0,
                    "very_windy_percent": 10.0,
                    "most_likely": assessment["wind"]["category"]
                },
                "precipitation": {
                    "dry_percent": 30.0,
                    "light_rain_percent": 35.0,
                    "moderate_rain_percent": 25.0,
                    "heavy_rain_percent": 10.0,
                    "most_likely": assessment["precipitation"]["category"]
                }
            },
            "statistics": {
                "wind": calc_stats(wind_speeds),
                "precipitation": calc_stats(precip_vals),
                "temperature": calc_stats(temp_vals),
                "humidity": calc_stats(humidity_vals)
            }
        }
        
    except Exception as e:
        print(f"❌ Error generating forecast: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating forecast: {str(e)}")

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
