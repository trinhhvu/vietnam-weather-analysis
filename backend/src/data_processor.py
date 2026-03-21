"""
Task 2 & Task 3 (OOP): Data Processing
DataProcessor class - Xử lý và làm sạch dữ liệu thời tiết.
"""

import json
import os
import numpy as np
import pandas as pd


class DataProcessor:
    """Xử lý và làm sạch dữ liệu thời tiết từ raw JSON sang DataFrame."""

    def __init__(self):
        """Initialize DataProcessor."""
        base_dir = os.path.dirname(__file__)
        self.raw_dir = os.path.join(base_dir, "..", "data", "raw")
        self.processed_dir = os.path.join(base_dir, "..", "data", "processed")
        os.makedirs(self.processed_dir, exist_ok=True)
        self.df = None

    def load_data(self, filename: str = "weather_raw.json") -> list:
        """
        Load raw data từ file JSON.

        Args:
            filename: Tên file JSON trong thư mục data/raw/.

        Returns:
            List các dict dữ liệu thô.
        """
        filepath = os.path.join(self.raw_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"  [OK] Loaded raw data: {filepath}")
        return data

    def clean_data(self, raw_data: list) -> pd.DataFrame:
        """
        Parse JSON, làm phẳng dữ liệu, xử lý missing values và tạo cột dẫn xuất.

        Args:
            raw_data: List các dict raw data từng thành phố.

        Returns:
            DataFrame đã được làm sạch.
        """
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

        # Convert data types
        df["date"] = pd.to_datetime(df["date"])

        # Convert numeric columns using numpy
        num_cols = ["temp_max", "temp_min", "temp_mean", "precipitation", "wind_speed", "humidity"]
        for col in num_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Handle missing values - fill with column mean per city
        df[num_cols] = df.groupby("city")[num_cols].transform(lambda x: x.fillna(x.mean()))

        # Derived columns
        df["year"]  = df["date"].dt.year
        df["month"] = df["date"].dt.month
        df["day"]   = df["date"].dt.day

        # Season (Mùa theo lịch Việt Nam)
        def get_season(month):
            if month in [12, 1, 2]:
                return "Đông"
            elif month in [3, 4, 5]:
                return "Xuân"
            elif month in [6, 7, 8]:
                return "Hè"
            else:
                return "Thu"

        df["season"] = df["month"].apply(get_season)

        # Flag extreme days
        df["is_hot_day"]   = df["temp_max"] > 35
        df["is_rainy_day"] = df["precipitation"] > 50

        self.df = df
        return df

    def export_results(self, filename: str = "weather_cleaned.csv"):
        """
        Xuất DataFrame đã xử lý ra file CSV.

        Args:
            filename: Tên file CSV đầu ra.
        """
        if self.df is None:
            print("  [ERROR] Chưa có dữ liệu để xuất. Hãy chạy clean_data() trước.")
            return

        filepath = os.path.join(self.processed_dir, filename)
        self.df.to_csv(filepath, index=False, encoding="utf-8-sig")
        print(f"  [OK] Đã xuất cleaned data: {filepath}")
