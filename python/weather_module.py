"""
Weather Module - Loads pre-trained Prophet models and generates forecasts
"""
import os
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Any
import numpy as np


class WeatherAPI:
    """API for weather forecasting using pre-trained Prophet models"""
    
    def __init__(self, model_dir: str):
        """
        Initialize the Weather API with pre-trained models
        
        Args:
            model_dir: Directory containing the pickled Prophet models
        """
        self.models = {}
        self.model_dir = model_dir
        
        # Load all pre-trained models
        model_files = {
            'wind_u': 'wind_u.pkl',
            'wind_v': 'wind_v.pkl',
            'precipitation': 'precipitation.pkl',
            'temperature': 'temperature.pkl',
            'humidity': 'humidity.pkl'
        }
        
        for key, filename in model_files.items():
            filepath = os.path.join(model_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    self.models[key] = pickle.load(f)
                    print(f"✅ Loaded model: {key}")
            else:
                print(f"⚠️  Model not found: {filepath}")
                raise FileNotFoundError(f"Model file not found: {filepath}")
    
    def get_forecast(self, hours: int = 24, sample_every: int = 3) -> List[Dict[str, Any]]:
        """
        Generate weather forecast for the next N hours
        
        Args:
            hours: Number of hours to forecast
            sample_every: Sample interval in hours (e.g., 3 = every 3 hours)
            
        Returns:
            List of forecast dictionaries with weather data and assessments
        """
        if not self.models:
            raise Exception("No models loaded")
        
        # Generate future dates
        now = datetime.now()
        future_dates = []
        
        for i in range(0, hours + 1, sample_every):
            future_dates.append(now + timedelta(hours=i))
        
        # Create DataFrame for Prophet
        import pandas as pd
        future_df = pd.DataFrame({'ds': future_dates})
        
        # Get predictions from all models
        predictions = {}
        
        for key, model in self.models.items():
            forecast = model.predict(future_df)
            predictions[key] = forecast['yhat'].values
        
        # Build forecast results
        forecasts = []
        
        for i, dt in enumerate(future_dates):
            wind_u = predictions['wind_u'][i]
            wind_v = predictions['wind_v'][i]
            wind_speed = np.sqrt(wind_u**2 + wind_v**2)
            precip = max(0, predictions['precipitation'][i])  # Can't be negative
            temp = predictions['temperature'][i]
            humidity = max(0, min(100, predictions['humidity'][i]))  # Clamp 0-100
            
            # Assess conditions
            assessment = self._assess_conditions(wind_speed, precip, temp, humidity)
            
            forecast_item = {
                'datetime': dt.strftime('%Y-%m-%d %H:%M:%S'),
                'timestamp': int(dt.timestamp()),
                'predicted_wind_u': round(float(wind_u), 2),
                'predicted_wind_v': round(float(wind_v), 2),
                'predicted_wind_speed': round(float(wind_speed), 2),
                'predicted_precip_mm': round(float(precip), 2),
                'predicted_temp_c': round(float(temp), 2),
                'predicted_humidity': round(float(humidity), 2),
                'assessment': assessment
            }
            
            forecasts.append(forecast_item)
        
        return forecasts
    
    def _assess_conditions(self, wind_speed: float, precip: float, 
                          temp: float, humidity: float) -> Dict[str, Any]:
        """
        Assess weather conditions and generate risk assessment
        
        Args:
            wind_speed: Wind speed in m/s
            precip: Precipitation in mm
            temp: Temperature in Celsius
            humidity: Humidity percentage
            
        Returns:
            Assessment dictionary with categories and safety info
        """
        # Wind assessment
        if wind_speed < 3:
            wind_cat = "Calm"
            wind_severity = 0.0
        elif wind_speed < 7:
            wind_cat = "Breezy"
            wind_severity = 0.3
        elif wind_speed < 12:
            wind_cat = "Windy"
            wind_severity = 0.6
        else:
            wind_cat = "Very Windy"
            wind_severity = 0.9
        
        # Precipitation assessment
        if precip < 2.5:
            precip_cat = "Dry"
            precip_severity = 0.0
        elif precip < 7.6:
            precip_cat = "Light Rain"
            precip_severity = 0.3
        elif precip < 50:
            precip_cat = "Moderate Rain"
            precip_severity = 0.6
        else:
            precip_cat = "Heavy Rain"
            precip_severity = 0.9
        
        # Temperature assessment
        if temp < 15:
            temp_cat = "Cool"
            temp_severity = 0.3
        elif temp < 25:
            temp_cat = "Comfortable"
            temp_severity = 0.0
        elif temp < 32:
            temp_cat = "Warm"
            temp_severity = 0.3
        else:
            temp_cat = "Hot"
            temp_severity = 0.6
        
        # Humidity assessment
        if humidity < 40:
            humid_cat = "Dry"
            humid_severity = 0.2
        elif humidity < 70:
            humid_cat = "Comfortable"
            humid_severity = 0.0
        else:
            humid_cat = "Humid"
            humid_severity = 0.4
        
        # Overall risk calculation
        overall_risk = (wind_severity + precip_severity + temp_severity + humid_severity) / 4
        
        # Safety assessment
        safe_for_outdoors = overall_risk < 0.5
        
        if safe_for_outdoors:
            recommendation = "Conditions are favorable for outdoor activities."
        elif overall_risk < 0.7:
            recommendation = "Proceed with caution. Some outdoor activities may be affected."
        else:
            recommendation = "Not recommended for outdoor activities. Stay indoors if possible."
        
        return {
            'wind': {
                'category': wind_cat,
                'severity': wind_severity,
                'safe': wind_severity < 0.6
            },
            'precipitation': {
                'category': precip_cat,
                'severity': precip_severity,
                'safe': precip_severity < 0.6
            },
            'temperature': {
                'category': temp_cat,
                'severity': temp_severity,
                'safe': temp_severity < 0.6
            },
            'humidity': {
                'category': humid_cat,
                'severity': humid_severity,
                'safe': humid_severity < 0.6
            },
            'overall_risk': round(overall_risk, 2),
            'safe_for_outdoors': safe_for_outdoors,
            'recommendation': recommendation
        }