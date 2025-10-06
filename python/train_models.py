import os
import pandas as pd
import joblib
from prophet import Prophet

# Base directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data and models directories relative to this script
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
MODEL_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(MODEL_DIR, exist_ok=True)

def train_and_save(csv_file, value_col="value", day_col="day", hour_col="hour", model_name="model"):
    """Train a Prophet model from CSV and save to models/"""
    path = os.path.join(DATA_DIR, csv_file)
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Training data missing: {path}")

    df = pd.read_csv(path)

    if "temperature" in csv_file:
        df[value_col] = df[value_col] - 273.15   # Kelvin → Celsius
    if "humidity" in csv_file and df[value_col].max() <= 1:
        df[value_col] = df[value_col] * 100      # fraction → percent


    # Build hourly timestamp if day/hour/value exist
    if day_col in df.columns and hour_col in df.columns and value_col in df.columns:
        df["ds"] = pd.to_datetime(
            df[day_col].astype(str) + " " + df[hour_col].astype(str) + ":00:00"
        )
        df = df.rename(columns={value_col: "y"})
    elif "ds" not in df.columns or "y" not in df.columns:
        raise ValueError(f"CSV {csv_file} must have (day,hour,value) or (ds,y) columns")

    # Train Prophet
    print(f"📊 Training model for {csv_file} ...")
    model = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=True
    )
    model.fit(df[["ds", "y"]])

    # Save model
    out_path = os.path.join(MODEL_DIR, f"{model_name}.pkl")
    joblib.dump(model, out_path)
    print(f"✅ Saved model: {out_path}")

if __name__ == "__main__":
    train_and_save("wind_u.csv", model_name="wind_u")
    train_and_save("wind_v.csv", model_name="wind_v")
    train_and_save("precipitation.csv", model_name="precip")
    train_and_save("temperature.csv", model_name="temp")
    train_and_save("humidity.csv", model_name="humidity")

    print("🎉 All models trained and saved in:", MODEL_DIR)
