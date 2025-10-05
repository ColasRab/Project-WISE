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

class WeatherAPI:
    def __init__(self, wind_u_path, wind_v_path, precip_path, temp_path, humidity_path):
        """Initialize Weather API with Prophet models"""
        self.models = {}
        
        # Load and train models
        wind_u = pd.read_csv(wind_u_path)
        wind_v = pd.read_csv(wind_v_path)
        precip = pd.read_csv(precip_path)
        temp = pd.read_csv(temp_path)
        humidity = pd.read_csv(humidity_path)
        
        self.models['wind_u'] = ProphetForecaster(wind_u)
        self.models['wind_v'] = ProphetForecaster(wind_v)
        self.models['precip'] = ProphetForecaster(precip)
        self.models['temp'] = ProphetForecaster(temp)
        self.models['humidity'] = ProphetForecaster(humidity)
    
    def get_forecast(self, years=5, sample_every=30):
        """Generate weather forecast for specified years"""
        days = years * 365
        
        # Get forecasts from all models
        wind_u_forecast = self.models['wind_u'].forecast(days)
        wind_v_forecast = self.models['wind_v'].forecast(days)
        precip_forecast = self.models['precip'].forecast(days)
        temp_forecast = self.models['temp'].forecast(days)
        humidity_forecast = self.models['humidity'].forecast(days)
        
        # Sample every N days
        forecasts = []
        for i in range(0, len(wind_u_forecast), sample_every):
            wind_u = wind_u_forecast.iloc[i]['yhat']
            wind_v = wind_v_forecast.iloc[i]['yhat']
            wind_speed = (wind_u**2 + wind_v**2)**0.5
            precip = max(0, precip_forecast.iloc[i]['yhat'])
            temp = temp_forecast.iloc[i]['yhat']
            humidity = max(0, min(100, humidity_forecast.iloc[i]['yhat']))
            
            # Get fuzzy logic assessment
            assessment = SimpleFuzzyLogic.overall_assessment(
                wind_speed, precip, humidity, temp
            )
            
            forecasts.append({
                "date": str(wind_u_forecast.iloc[i]['ds']),
                "predicted_wind_u": round(wind_u, 2),
                "predicted_wind_v": round(wind_v, 2),
                "predicted_precip_mm": round(precip, 2),
                "predicted_temp_c": round(temp, 2),
                "predicted_humidity": round(humidity, 2),
                "assessment": assessment
            })
        
        return forecasts