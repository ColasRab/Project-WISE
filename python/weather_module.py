"""
Weather Predictor - 5 Year Forecast with Prophet + Fuzzy Logic
"""

import pandas as pd
import json
from prophet import Prophet
from datetime import timedelta
from prophet import Prophet

# ============================================
# FUZZY LOGIC (same as before)
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
    def overall_assessment(wind_speed, precip_mm_day, humidity, temp_c=None):
        wind_result = SimpleFuzzyLogic.assess_wind(wind_speed)
        precip_result = SimpleFuzzyLogic.assess_precipitation(precip_mm_day)
        humidity_result = SimpleFuzzyLogic.assess_humidity(humidity)

        # Combine severity as average
        risk = (wind_result['severity'] + precip_result['severity'] + humidity_result['severity']) / 3
        safe = wind_result['safe'] and precip_result['safe'] and humidity_result['safe']

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
            'overall_risk': risk,
            'safe_for_outdoors': safe,
            'recommendation': recommendation
        }

# ============================================
# PROPHET FORECASTER
# ============================================

class ProphetForecaster:
    def __init__(self, df, value_col="value", day_col="day", hour_col="hour"):
        # Combine day + hour into a single datetime column for Prophet
        if day_col in df.columns and hour_col in df.columns and value_col in df.columns:
            df["ds"] = pd.to_datetime(df[day_col].astype(str) + " " + df[hour_col].astype(str) + ":00:00")
            df = df.rename(columns={value_col: "y"})
        elif "ds" not in df.columns or "y" not in df.columns:
            raise ValueError(f"Expected columns ({day_col},{hour_col},{value_col}) or (ds,y), but got {df.columns.tolist()}")

        self.df = df[["ds", "y"]].copy()
        self.model = Prophet()
        self.model.fit(self.df)

        
        self.model = Prophet()
        self.model.fit(self.df)

    def forecast(self, years=5, freq="D"):
        periods = int(years) * 365
        future = self.model.make_future_dataframe(periods=periods, freq=freq)

        forecast = self.model.predict(future)
        return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]

# ============================================
# WEATHER API WITH 5-YEAR FORECAST
# ============================================

import pandas as pd

class WeatherAPI:
    def __init__(self, wind_u_file, wind_v_file, precip_file, temp_file, humidity_file):
        self.wind_u = pd.read_csv(wind_u_file)
        self.wind_v = pd.read_csv(wind_v_file)
        self.precip = pd.read_csv(precip_file)
        self.temp = pd.read_csv(temp_file)
        self.humidity = pd.read_csv(humidity_file)

        # Forecasters for each dataset
        self.wind_u_forecaster = ProphetForecaster(self.wind_u, value_col="value", day_col="day", hour_col="hour")
        self.wind_v_forecaster = ProphetForecaster(self.wind_v, value_col="value", day_col="day", hour_col="hour")
        self.precip_forecaster = ProphetForecaster(self.precip, value_col="value", day_col="day", hour_col="hour")
        self.temp_forecaster = ProphetForecaster(self.temp, value_col="value", day_col="day", hour_col="hour")
        self.humidity_forecaster = ProphetForecaster(self.humidity, value_col="value", day_col="day", hour_col="hour")


    def get_forecast(self, years=5, sample_every=30):
        wind_u_future = self.wind_u_forecaster.forecast(years)
        wind_v_future = self.wind_v_forecaster.forecast(years)
        precip_future = self.precip_forecaster.forecast(years)
        temp_future = self.temp_forecaster.forecast(years)
        humidity_future = self.humidity_forecaster.forecast(years)

        # Merge all forecasts by date
        merged = (
            wind_u_future
            .merge(wind_v_future, on="ds", suffixes=("_wind_u", "_wind_v"))
            .merge(precip_future, on="ds")
            .merge(temp_future, on="ds", suffixes=("_precip", "_temp"))
            .merge(humidity_future, on="ds", suffixes=("", "_humidity"))
        )

        merged = merged.iloc[::sample_every, :]

        forecasts = []
        for _, row in merged.iterrows():
            wind_u_val = row["yhat_wind_u"]
            wind_v_val = row["yhat_wind_v"]
            precip_val = row["yhat"]
            temp_val = row["yhat_temp"]
            humidity_val = row["yhat_humidity"]

            assessment = SimpleFuzzyLogic.overall_assessment(
                wind_u_val, precip_val, humidity_val, temp_val
            )

            forecasts.append({
                "date": str(row["ds"].date()),
                "predicted_wind_u": round(wind_u_val, 2),
                "predicted_wind_v": round(wind_v_val, 2),
                "predicted_precip_mm": round(precip_val, 2),
                "predicted_temp_c": round(temp_val, 2),
                "predicted_humidity": round(humidity_val, 2),
                "assessment": assessment
            })

        return forecasts



# ============================================
# MAIN
# ============================================

def main():
    api = WeatherAPI(
        "python/data/processed/wind_u.csv",
        "python/data/processed/wind_v.csv",
        "python/data/processed/precipitation.csv",
        "python/data/processed/temperature.csv",
        "python/data/processed/humidity.csv"
    )

    print("Generating 5-year forecast...")
    future = api.forecast_trend(years=5, sample_every=30)

    with open("five_year_forecast.json", "w") as f:
        json.dump(future, f, indent=2)

    print("\nForecast saved to five_year_forecast.json")


if __name__ == "__main__":
    main()
