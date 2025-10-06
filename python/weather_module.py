# weather_module.py
import os
import joblib
import pandas as pd

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
    def assess_precipitation(precip_mm_hr):
        if precip_mm_hr < 0.1:
            return {"category": "Dry", "severity": 0.1, "safe": True}
        elif precip_mm_hr < 1:
            return {"category": "Light Rain", "severity": 0.3, "safe": True}
        elif precip_mm_hr < 5:
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
    def overall_assessment(wind_speed, precip_mm_hr, humidity, temp_c):
        wind_result = SimpleFuzzyLogic.assess_wind(wind_speed)
        precip_result = SimpleFuzzyLogic.assess_precipitation(precip_mm_hr)
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
# WEATHER API (loads pretrained Prophet models)
# ============================================

class WeatherAPI:
    def __init__(self, model_dir="models"):
        self.models = {}
        for name in ["wind_u", "wind_v", "precip", "temp", "humidity"]:
            path = os.path.join(model_dir, f"{name}.pkl")
            if os.path.exists(path):
                print(f"📂 Loading model: {path}")
                self.models[name] = joblib.load(path)
            else:
                print(f"⚠️ Model {name}.pkl not found!")

    def get_forecast(self, hours=168, sample_every=1):
        """
        Generate hourly forecasts.
        hours = number of hours into the future (default: 168 = 7 days)
        sample_every = take every Nth hour (default: 1 = every hour)
        """
        if not self.models:
            raise RuntimeError("No models loaded")

        wind_u_forecast = self.models['wind_u'].predict(
            self.models['wind_u'].make_future_dataframe(periods=hours, freq="H")
        )
        wind_v_forecast = self.models['wind_v'].predict(
            self.models['wind_v'].make_future_dataframe(periods=hours, freq="H")
        )
        precip_forecast = self.models['precip'].predict(
            self.models['precip'].make_future_dataframe(periods=hours, freq="H")
        )
        temp_forecast = self.models['temp'].predict(
            self.models['temp'].make_future_dataframe(periods=hours, freq="H")
        )
        humidity_forecast = self.models['humidity'].predict(
            self.models['humidity'].make_future_dataframe(periods=hours, freq="H")
        )

        forecasts = []
        for i in range(0, len(wind_u_forecast), sample_every):
            wind_u = wind_u_forecast.iloc[i]['yhat']
            wind_v = wind_v_forecast.iloc[i]['yhat']
            wind_speed = (wind_u**2 + wind_v**2)**0.5
            precip = max(0, precip_forecast.iloc[i]['yhat'])
            temp = temp_forecast.iloc[i]['yhat']
            humidity = max(0, min(100, humidity_forecast.iloc[i]['yhat']))

            assessment = SimpleFuzzyLogic.overall_assessment(
                wind_speed, precip, humidity, temp
            )

            forecasts.append({
                "datetime": str(wind_u_forecast.iloc[i]['ds']),
                "predicted_wind_u": round(wind_u, 2),
                "predicted_wind_v": round(wind_v, 2),
                "predicted_precip_mm": round(precip, 2),
                "predicted_temp_c": round(temp, 2),
                "predicted_humidity": round(humidity, 2),
                "assessment": assessment
            })
        return forecasts
