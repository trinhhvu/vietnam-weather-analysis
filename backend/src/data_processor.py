"""
Task 2 & 3: Data Processing
Cleans and transforms raw weather JSON data into structured pandas DataFrames.
"""

import json
import os
import numpy as np
import pandas as pd

class DataProcessor:
    """Class to manage data cleaning and transformation."""

    def __init__(self):
        """Initializes raw and processed data directories."""
        base_dir = os.path.dirname(__file__)
        self.raw_dir = os.path.join(base_dir, "..", "data", "raw")
        self.processed_dir = os.path.join(base_dir, "..", "data", "processed")
        os.makedirs(self.processed_dir, exist_ok=True)
        self.df = None

    def load_data(self, filename: str = "weather_raw.json") -> list:
        """Loads entries from the raw JSON file."""
        filepath = os.path.join(self.raw_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    def clean_data(self, raw_data: list) -> pd.DataFrame:
        """Parses, cleans, and generates features from raw weather JSON data."""
        records = []
        for city_data in raw_data:
            city_name = city_data.get("city", "Unknown")
            region = city_data.get("region", "Unknown")
            daily = city_data.get("daily", {})
            dates = daily.get("time", [])

            for i, date in enumerate(dates):
                records.append({
                    "date":        date,
                    "city":        city_name,
                    "region":      region,
                    "temp_max":    daily.get("temperature_2m_max", [None])[i],
                    "temp_min":    daily.get("temperature_2m_min", [None])[i],
                    "temp_mean":   daily.get("temperature_2m_mean", [None])[i],
                    "precipitation": daily.get("precipitation_sum", [None])[i],
                    "wind_speed":  daily.get("windspeed_10m_max", [None])[i],
                    "humidity":    daily.get("relative_humidity_2m_mean", [None])[i],
                })

        df = pd.DataFrame(records)
        df["date"] = pd.to_datetime(df["date"])

        # Convert to numeric and fill NaN values with each city's average
        num_cols = ["temp_max", "temp_min", "temp_mean", "precipitation", "wind_speed", "humidity"]
        for col in num_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df[num_cols] = df.groupby("city")[num_cols].transform(lambda x: x.fillna(x.mean()))

        # Extract basic date components
        df["year"]  = df["date"].dt.year
        df["month"] = df["date"].dt.month
        df["day"]   = df["date"].dt.day

        # Define seasons based on the Vietnamese calendar
        def get_season(month):
            if month in [12, 1, 2]: return "Winter"
            elif month in [3, 4, 5]: return "Spring"
            elif month in [6, 7, 8]: return "Summer"
            else: return "Autumn"

        df["season"] = df["month"].apply(get_season)

        # Flag weather extremes: Nắng nóng (>35°C) and Mưa lớn (>50mm)
        df["is_hot_day"]   = df["temp_max"] > 35
        df["is_rainy_day"] = df["precipitation"] > 50

        self.df = df
        return df

    def export_results(self, filename: str = "weather_cleaned.csv"):
        """Exports the processed DataFrame to a CSV file."""
        if self.df is None:
            print("  [ERROR] No data to export. Run clean_data() first.")
            return

        filepath = os.path.join(self.processed_dir, filename)
        self.df.to_csv(filepath, index=False, encoding="utf-8-sig")
        print(f"  [OK] Exported cleaned data to: {filepath}")
