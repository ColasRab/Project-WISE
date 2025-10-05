# weather_service.py
import os
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from weather_module import WeatherAPI

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
    print(f"=" * 60)
    print(f"🚀 Server starting on 0.0.0.0:{port}")
    print(f"=" * 60)
    
    # Load Prophet models
    try:
        print("📊 Loading weather data and training Prophet models...")
        api = WeatherAPI(
            "data/processed/wind_u.csv",
            "data/processed/wind_v.csv",
            "data/processed/precipitation.csv",
            "data/processed/temperature.csv",
            "data/processed/humidity.csv"
        )
        print("✅ Prophet models loaded successfully!")
    except Exception as e:
        print(f"⚠️  Warning: Could not load Prophet models: {e}")
        print("📝 API will return mock data instead")

@app.get("/")
def root():
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
    return {
        "status": "healthy",
        "models_loaded": api is not None,
        "port": os.environ.get("PORT", "8000")
    }

@app.get("/api/weather")
def get_forecast(lat: float = Query(..., description="Latitude"), 
                 lon: float = Query(..., description="Longitude")):
    """
    Get weather forecast for a specific location.
    
    Example: /api/weather?lat=14.5995&lon=120.9842
    """
    
    # Try to use real Prophet forecasts
    if api is not None:
        try:
            print(f"🔮 Generating forecast for lat={lat}, lon={lon}")
            
            # Get 5-year forecast
            forecasts = api.get_forecast(years=5, sample_every=30)
            
            if not forecasts or len(forecasts) == 0:
                raise Exception("No forecast data available")
            
            # Use first forecast point
            first = forecasts[0]
            
            # Calculate wind speed from components
            wind_u = first["predicted_wind_u"]
            wind_v = first["predicted_wind_v"]
            wind_speed = round((wind_u**2 + wind_v**2)**0.5, 2)
            precip = first["predicted_precip_mm"]
            temp = first["predicted_temp_c"]
            humidity = first["predicted_humidity"]
            
            # Get assessment from forecast
            assessment = first["assessment"]
            
            # Calculate statistics from all forecasts
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
            
            # Extract values for statistics
            wind_speeds = [(f["predicted_wind_u"]**2 + f["predicted_wind_v"]**2)**0.5 for f in forecasts]
            precip_vals = [f["predicted_precip_mm"] for f in forecasts]
            temp_vals = [f["predicted_temp_c"] for f in forecasts]
            humidity_vals = [f["predicted_humidity"] for f in forecasts]
            
            print(f"✅ Forecast generated successfully")
            
            return {
                "location": {
                    "latitude": lat,
                    "longitude": lon,
                    "name": f"{lat}, {lon}"
                },
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
    
    else:
        # Fallback: Models not loaded, return error
        raise HTTPException(
            status_code=503,
            detail="Prophet models not loaded. Check server logs for data file errors."
        )

# This is CRITICAL for Render
if __name__ == "__main__":
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get("PORT", 8000))
    
    print(f"\n{'='*60}")
    print(f"🌤️  Weather API Server")
    print(f"{'='*60}")
    print(f"Port: {port}")
    print(f"Host: 0.0.0.0")
    print(f"{'='*60}\n")
    
    # MUST bind to 0.0.0.0 for Render
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )