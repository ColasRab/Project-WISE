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
    
    # Generate mock forecast data
    wind_speed = round(random.uniform(2, 12), 2)
    precip = round(random.uniform(0, 10), 2)
    temp = round(random.uniform(20, 35), 2)
    humidity = round(random.uniform(40, 90), 2)
    
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
                "calm_percent": 20,
                "breezy_percent": 40,
                "windy_percent": 30,
                "very_windy_percent": 10,
                "most_likely": wind_assessment["category"]
            },
            "precipitation": {
                "dry_percent": 30,
                "light_rain_percent": 35,
                "moderate_rain_percent": 25,
                "heavy_rain_percent": 10,
                "most_likely": precip_assessment["category"]
            }
        },
        "statistics": {
            "wind": {
                "mean": wind_speed,
                "std": 2.5,
                "min": max(0, wind_speed - 3),
                "max": wind_speed + 3,
                "p25": wind_speed - 1,
                "p75": wind_speed + 1,
                "p90": wind_speed + 2
            },
            "precipitation": {
                "mean": precip,
                "std": 1.5,
                "min": max(0, precip - 2),
                "max": precip + 2,
                "p25": max(0, precip - 1),
                "p75": precip + 1,
                "p90": precip + 1.5
            },
            "temperature": {
                "mean": temp,
                "std": 3.0,
                "min": temp - 4,
                "max": temp + 4,
                "p25": temp - 2,
                "p75": temp + 2,
                "p90": temp + 3
            },
            "humidity": {
                "mean": humidity,
                "std": 10.0,
                "min": max(0, humidity - 15),
                "max": min(100, humidity + 15),
                "p25": humidity - 5,
                "p75": humidity + 5,
                "p90": humidity + 10
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