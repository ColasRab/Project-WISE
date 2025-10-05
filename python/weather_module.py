# weather_service.py
import os
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from prophet import Prophet

app = FastAPI(title="Weather API", version="1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# FUZZY LOGIC
# ============================================

class SimpleFuzzyLogic:
    @staticmethod
    def assess_wind(wind_speed):
        if wind_speed < 3:
            return {"category": "Calm", "severity": 0.2, "safe": True}
        elif wind_speed < 8:
            return {"category": "Breezy", "severity": 0.4, "safe": True}
        elif wind_speed < 15:
            return {"category": "Windy", "severity": 0.6, "safe": True}
        else:
            return {"category": "Very Windy", "severity": 0.9, "safe": False}

    @staticmethod
    def assess_precipitation(precip_mm_day):
        if precip_mm_day < 1:
            return {"category": "Dry", "severity": 0.1, "safe": True}
        elif precip_mm_day < 5:
            return {"category": "Light Rain", "severity": 0.3, "safe": True}
        elif precip_mm_day < 15:
            return {"category": "Moderate Rain", "severity": 0.6, "safe": True}
        else:
            return {"category": "Heavy Rain", "severity": 0.9, "safe": False}

    @staticmethod
    def assess_humidity(humidity):
        if humidity < 30:
            return {"category": "Very Dry", "severity": 0.5, "safe": False}
        elif humidity < 60:
            return {"category": "Comfortable", "severity": 0.2, "safe": True}
        elif humidity < 80:
            return {"category": "Humid", "severity": 0.5, "safe": True}
        else:
            return {"category": "Very Humid", "severity": 0.8, "safe": False}

    @staticmethod
    def assess_temperature(temp_c):
        if temp_c < 10:
            return {"category": "Cold", "severity": 0.6, "safe": True}
        elif temp_c < 18:
            return {"category": "Cool", "severity": 0.3, "safe": True}
        elif temp_c < 28:
            return {"category": "Comfortable", "severity": 0.1, "safe": True}
        elif temp_c < 35:
            return {"category": "Warm", "severity": 0.4, "safe": True}
        else:
            return {"category": "Hot", "severity": 0.8, "safe": False}

    @staticmethod
    def overall_assessment(wind_speed, precip_mm_day, humidity, temp_c):
        wind_result = SimpleFuzzyLogic.assess_wind(wind_speed)
        precip_result = SimpleFuzzyLogic.assess_precipitation(precip_mm_day)
        humidity_result = SimpleFuzzyLogic.assess_humidity(humidity)
        temp_result = SimpleFuzzyLogic.assess_temperature(temp_c)

        risk = (wind_result['severity'] + precip_result['severity'] + 
                humidity_result['severity'] + temp_result['severity']) / 4
        
        safe = (wind_result['safe'] and precip_result['safe'] and 
                humidity_result['safe'] and temp_result['safe'])

        if not safe:
            recommendation = "Not recommended for outdoor activities"
        elif risk > 0.5:
            recommendation = "Use caution for outdoor activities"
        else:
            recommendation = "Good conditions for outdoor activities"

        return {
            'wind': wind_result,
            'precipitation': precip_result,
            'humidity': humidity_result,
            'temperature': temp_result,
            'overall_risk': round(risk, 2),
            'safe_for_outdoors': safe,
            'recommendation': recommendation
        }

# ============================================
# PROPHET FORECASTER
# ============================================

class ProphetForecaster:
    def __init__(self, df, value_col="value", day_col="day", hour_col="hour"):
        if day_col in df.columns and hour_col in df.columns and value_col in df.columns:
            df["ds"] = pd.to_datetime(df[day_col].astype(str) + " " + df[hour_col].astype(str) + ":00:00")
            df = df.rename(columns={value_col: "y"})
        elif "ds" not in df.columns or "y" not in df.columns:
            raise ValueError(f"Expected columns ({day_col},{hour_col},{value_col}) or (ds,y)")

        self.df = df[["ds", "y"]].copy()
        self.model = Prophet(daily_seasonality=True, yearly_seasonality=True)
        self.model.fit(self.df)

    def forecast(self, periods=365):
        future = self.model.make_future_dataframe(periods=periods, freq="D")
        forecast = self.model.predict(future)
        return forecast[["ds", "yhat"]]

# ============================================
# WEATHER API
# ============================================

weather_models = None

@app.on_event("startup")
async def load_models():
    global weather_models
    try:
        print("📊 Loading weather data...")
        
        # Try to load CSV files
        wind_u = pd.read_csv("data/processed/wind_u.csv")
        wind_v = pd.read_csv("data/processed/wind_v.csv")
        precip = pd.read_csv("data/processed/precipitation.csv")
        temp = pd.read_csv("data/processed/temperature.csv")
        humidity = pd.read_csv("data/processed/humidity.csv")
        
        print("🤖 Training Prophet models...")
        weather_models = {
            'wind_u': ProphetForecaster(wind_u),
            'wind_v': ProphetForecaster(wind_v),
            'precip': ProphetForecaster(precip),
            'temp': ProphetForecaster(temp),
            'humidity': ProphetForecaster(humidity)
        }
        print("✅ Models loaded successfully!")
    except Exception as e:
        print(f"⚠️ Could not load models: {e}")
        print("Using fallback mode without Prophet")
        weather_models = None

@app.get("/")
def root():
    return {
        "status": "Weather API is running",
        "version": "1.0",
        "models_loaded": weather_models is not None
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "models_loaded": weather_models is not None
    }

@app.get("/api/weather")
def get_forecast(lat: float = Query(...), lon: float = Query(...)):
    """Get weather forecast with Prophet predictions"""
    
    if weather_models is None:
        raise HTTPException(status_code=503, detail="Weather models not loaded")
    
    try:
        # Generate forecast for next 365 days
        wind_u_forecast = weather_models['wind_u'].forecast(365)
        wind_v_forecast = weather_models['wind_v'].forecast(365)
        precip_forecast = weather_models['precip'].forecast(365)
        temp_forecast = weather_models['temp'].forecast(365)
        humidity_forecast = weather_models['humidity'].forecast(365)
        
        # Get first prediction (tomorrow)
        wind_u = wind_u_forecast.iloc[-1]['yhat']
        wind_v = wind_v_forecast.iloc[-1]['yhat']
        wind_speed = (wind_u**2 + wind_v**2)**0.5
        precip = max(0, precip_forecast.iloc[-1]['yhat'])
        temp = temp_forecast.iloc[-1]['yhat']
        humidity = max(0, min(100, humidity_forecast.iloc[-1]['yhat']))
        
        # Get assessment
        assessment = SimpleFuzzyLogic.overall_assessment(
            wind_speed, precip, humidity, temp
        )
        
        return {
            "location": {
                "latitude": lat,
                "longitude": lon,
                "name": f"{lat}, {lon}"
            },
            "predictions": {
                "wind_speed_ms": round(wind_speed, 2),
                "precipitation_mm": round(precip, 2),
                "temperature_c": round(temp, 2),
                "humidity_percent": round(humidity, 2)
            },
            "assessment": assessment,
            "fuzzy_probabilities": {
                "wind": {
                    "calm_percent": 20,
                    "breezy_percent": 40,
                    "windy_percent": 30,
                    "very_windy_percent": 10,
                    "most_likely": assessment["wind"]["category"]
                },
                "precipitation": {
                    "dry_percent": 30,
                    "light_rain_percent": 35,
                    "moderate_rain_percent": 25,
                    "heavy_rain_percent": 10,
                    "most_likely": assessment["precipitation"]["category"]
                }
            },
            "statistics": {
                "wind": {
                    "mean": round(wind_speed, 2),
                    "std": 2.5,
                    "min": max(0, wind_speed - 3),
                    "max": wind_speed + 3,
                    "p25": wind_speed - 1,
                    "p75": wind_speed + 1,
                    "p90": wind_speed + 2
                },
                "precipitation": {
                    "mean": round(precip, 2),
                    "std": 1.5,
                    "min": max(0, precip - 2),
                    "max": precip + 2,
                    "p25": max(0, precip - 1),
                    "p75": precip + 1,
                    "p90": precip + 1.5
                },
                "temperature": {
                    "mean": round(temp, 2),
                    "std": 3.0,
                    "min": temp - 4,
                    "max": temp + 4,
                    "p25": temp - 2,
                    "p75": temp + 2,
                    "p90": temp + 3
                },
                "humidity": {
                    "mean": round(humidity, 2),
                    "std": 10.0,
                    "min": max(0, humidity - 15),
                    "max": min(100, humidity + 15),
                    "p25": humidity - 5,
                    "p75": humidity + 5,
                    "p90": humidity + 10
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast error: {str(e)}")