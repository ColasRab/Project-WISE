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
    """Train a Prophet model from CSV and save to models/ (with unit normalization)."""
    path = os.path.join(DATA_DIR, csv_file)
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Training data missing: {path}")

    df = pd.read_csv(path)
    print(f"📂 Loaded {csv_file}: {len(df)} rows")

    # Drop duplicate timestamps (common in reanalysis data)
    if {"day", "hour"}.issubset(df.columns):
        df = df.drop_duplicates(subset=["day", "hour"])
        print(f"🧹 After deduplication: {len(df)} rows")

    # =========================
    # UNIT NORMALIZATION
    # =========================
    if "temperature" in csv_file.lower():
        df[value_col] = df[value_col] - 273.15  # Kelvin → Celsius
        print("🌡️ Converted temperature from K → °C")

    if "humidity" in csv_file.lower() and df[value_col].max() <= 1:
        df[value_col] = df[value_col] * 100  # fraction → percent
        print("💧 Converted humidity from fraction → %")

    if "precip" in csv_file.lower():
        df[value_col] = df[value_col] * 3600  # kg/m²/s → mm/hour
        print("🌧️ Converted precipitation from kg/m²/s → mm/hour")

    # =========================
    # TIMESTAMP HANDLING
    # =========================
    if {day_col, hour_col, value_col}.issubset(df.columns):
        df["ds"] = pd.to_datetime(df[day_col].astype(str) + " " + df[hour_col].astype(str) + ":00:00")
        df = df.rename(columns={value_col: "y"})
    elif {"ds", "y"}.issubset(df.columns):
        pass  # already formatted
    else:
        raise ValueError(f"CSV {csv_file} must have either (day,hour,value) or (ds,y) columns")

    df = df[["ds", "y"]].dropna()
    if df["y"].nunique() < 3:
        raise ValueError(f"⚠️ Not enough variation in {csv_file} for Prophet training")

    # =========================
    # TRAIN PROPHET MODEL
    # =========================
    print(f"📊 Training Prophet model for {model_name} ({len(df)} hourly records)...")
    model = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=True
    )
    model.fit(df)

    # =========================
    # SAVE MODEL
    # =========================
    out_path = os.path.join(MODEL_DIR, f"{model_name}.pkl")
    joblib.dump(model, out_path)
    print(f"✅ Saved trained model → {out_path}\n")
if __name__ == "__main__":
    train_and_save("wind_u.csv", model_name="wind_u")
    train_and_save("wind_v.csv", model_name="wind_v")
    train_and_save("precipitation.csv", model_name="precip")
    train_and_save("temperature.csv", model_name="temp")
    train_and_save("humidity.csv", model_name="humidity")

    print("🎉 All models trained and saved in:", MODEL_DIR)
