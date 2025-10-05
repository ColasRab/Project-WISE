# weather_service.py
import os
import random
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Weather API", version="1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    port = os.environ.get("PORT", "8000")
    print(f"=" * 50)
    print(f"🚀 Server starting on 0.0.0.0:{port}")
    print(f"=" * 50)

@app.get("/")
def root():
    return {
        "status": "Weather API is running",
        "version": "1.0",
        "endpoints": {
            "health": "/health",
            "weather": "/api/weather?lat={latitude}&lon={longitude}"
        }
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "port": os.environ.get("PORT", "8000")
    }

@app.get("/api/weather")
def get_forecast(lat: float = Query(..., description="Latitude"), 
                 lon: float = Query(..., description="Longitude")):
    """
    Get weather forecast for a specific location.
    
    Example: /api/weather?lat=14.5995&lon=120.9842
    """
    
    # Generate mock weather data based on location
    # In production, this would come from your Prophet models
    wind_speed = round(5 + random.uniform(-2, 5), 2)
    precip = round(max(0, 2 + random.uniform(-1, 8)), 2)
    temp = round(25 + random.uniform(-5, 10), 2)
    humidity = round(max(30, min(90, 65 + random.uniform(-15, 20))), 2)
    
    # Assessment functions
    def assess_wind(speed):
        if speed < 3:
            return {"category": "Calm", "severity": 0.2, "safe": True}
        elif speed < 8:
            return {"category": "Breezy", "severity": 0.4, "safe": True}
        elif speed < 15:
            return {"category": "Windy", "severity": 0.6, "safe": True}
        else:
            return {"category": "Very Windy", "severity": 0.9, "safe": False}
    
    def assess_precip(p):
        if p < 1:
            return {"category": "Dry", "severity": 0.1, "safe": True}
        elif p < 5:
            return {"category": "Light Rain", "severity": 0.3, "safe": True}
        elif p < 15:
            return {"category": "Moderate Rain", "severity": 0.6, "safe": True}
        else:
            return {"category": "Heavy Rain", "severity": 0.9, "safe": False}
    
    def assess_humidity(h):
        if h < 30:
            return {"category": "Very Dry", "severity": 0.5, "safe": False}
        elif h < 60:
            return {"category": "Comfortable", "severity": 0.2, "safe": True}
        elif h < 80:
            return {"category": "Humid", "severity": 0.5, "safe": True}
        else:
            return {"category": "Very Humid", "severity": 0.8, "safe": False}
    
    def assess_temp(t):
        if t < 15:
            return {"category": "Cold", "severity": 0.5, "safe": True}
        elif t < 25:
            return {"category": "Cool", "severity": 0.2, "safe": True}
        elif t < 30:
            return {"category": "Warm", "severity": 0.3, "safe": True}
        else:
            return {"category": "Hot", "severity": 0.7, "safe": True}
    
    # Calculate assessments
    wind_assessment = assess_wind(wind_speed)
    precip_assessment = assess_precip(precip)
    humidity_assessment = assess_humidity(humidity)
    temp_assessment = assess_temp(temp)
    
    overall_risk = (wind_assessment['severity'] + precip_assessment['severity'] + 
                   humidity_assessment['severity'] + temp_assessment['severity']) / 4
    
    safe = (wind_assessment['safe'] and precip_assessment['safe'] and 
            humidity_assessment['safe'] and temp_assessment['safe'])
    
    if not safe:
        recommendation = "Not recommended for outdoor activities"
    elif overall_risk > 0.5:
        recommendation = "Use caution for outdoor activities"
    else:
        recommendation = "Good conditions for outdoor activities"
    
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
        "assessment": {
            "wind": wind_assessment,
            "precipitation": precip_assessment,
            "humidity": humidity_assessment,
            "temperature": temp_assessment,
            "overall_risk": round(overall_risk, 2),
            "safe_for_outdoors": safe,
            "recommendation": recommendation
        },
        "fuzzy_probabilities": {
            "wind": {
                "calm_percent": 20.0,
                "breezy_percent": 40.0,
                "windy_percent": 30.0,
                "very_windy_percent": 10.0,
                "most_likely": wind_assessment["category"]
            },
            "precipitation": {
                "dry_percent": 30.0,
                "light_rain_percent": 35.0,
                "moderate_rain_percent": 25.0,
                "heavy_rain_percent": 10.0,
                "most_likely": precip_assessment["category"]
            }
        },
        "statistics": {
            "wind": {
                "mean": round(wind_speed, 2),
                "std": 2.5,
                "min": round(max(0, wind_speed - 3), 2),
                "max": round(wind_speed + 3, 2),
                "p25": round(wind_speed - 1, 2),
                "p75": round(wind_speed + 1, 2),
                "p90": round(wind_speed + 2, 2)
            },
            "precipitation": {
                "mean": round(precip, 2),
                "std": 1.5,
                "min": round(max(0, precip - 2), 2),
                "max": round(precip + 2, 2),
                "p25": round(max(0, precip - 1), 2),
                "p75": round(precip + 1, 2),
                "p90": round(precip + 1.5, 2)
            },
            "temperature": {
                "mean": round(temp, 2),
                "std": 3.0,
                "min": round(temp - 4, 2),
                "max": round(temp + 4, 2),
                "p25": round(temp - 2, 2),
                "p75": round(temp + 2, 2),
                "p90": round(temp + 3, 2)
            },
            "humidity": {
                "mean": round(humidity, 2),
                "std": 10.0,
                "min": round(max(0, humidity - 15), 2),
                "max": round(min(100, humidity + 15), 2),
                "p25": round(humidity - 5, 2),
                "p75": round(humidity + 5, 2),
                "p90": round(humidity + 10, 2)
            }
        }
    }

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