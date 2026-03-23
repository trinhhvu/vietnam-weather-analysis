"""
Task 1: Data Collection
Collects historical weather data from the Open-Meteo Archive API.
"""

import requests
import json
import os
from datetime import datetime, timedelta

# Major cities across North, Central, and South regions
CITIES = {
    "Hanoi":         {"lat": 21.0285, "lon": 105.8542, "region": "North"},
    "Hai Phong":     {"lat": 20.8449, "lon": 106.6881, "region": "North"},
    "Da Nang":       {"lat": 16.0544, "lon": 108.2022, "region": "Central"},
    "Hue":           {"lat": 16.4637, "lon": 107.5909, "region": "Central"},
    "Ho Chi Minh":   {"lat": 10.8231, "lon": 106.6297, "region": "South"},
    "Can Tho":       {"lat": 10.0452, "lon": 105.7469, "region": "South"},
}

BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

class WeatherCollector:
    """Class to manage weather data gathering."""

    def __init__(self):
        """Initializes raw data directories."""
        self.cities = CITIES
        self.raw_data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
        os.makedirs(self.raw_data_dir, exist_ok=True)

    def fetch_city_data(self, city_name: str, start_date: str, end_date: str) -> dict:
        """Fetches historical daily weather data for a single city."""
        if city_name not in self.cities:
            print(f"  [ERROR] {city_name} not found in configuration.")
            return {}

        city_info = self.cities[city_name]
        params = {
            "latitude": city_info["lat"],
            "longitude": city_info["lon"],
            "start_date": start_date,
            "end_date": end_date,
            "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,windspeed_10m_max,relative_humidity_2m_mean",
            "timezone": "Asia/Ho_Chi_Minh",
        }

        try:
            print(f"  Fetching: {city_name} ({start_date} -> {end_date})...")
            response = requests.get(BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Attach metadata for downstream processing
            data["city"] = city_name
            data["region"] = city_info["region"]
            return data
        except Exception as e:
            print(f"  [ERROR] Connection error for {city_name}: {e}")
            return {}

    def collect_all(self, start_date: str = "2023-01-01", end_date: str = "2025-01-31") -> list:
        """Aggregates weather data for all configured cities."""
        all_data = []
        
        for city_name in self.cities:
            city_data = self.fetch_city_data(city_name, start_date, end_date)
            if city_data:
                all_data.append(city_data)

        if all_data:
            self._save_raw_data(all_data)

        return all_data

    def _save_raw_data(self, data: list, filename: str = "weather_raw.json"):
        """Saves list of dicts to a JSON file."""
        filepath = os.path.join(self.raw_data_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  [OK] Saved raw data to: {filepath}")
