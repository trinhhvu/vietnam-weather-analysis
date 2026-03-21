"""
Task 1: Data Collection
WeatherCollector class - Thu thập dữ liệu thời tiết từ Open-Meteo API (free, không cần key).
"""

import requests
import json
import os
from datetime import datetime, timedelta


# Cities configuration
CITIES = {
    "Hà Nội":        {"lat": 21.0285, "lon": 105.8542, "region": "Bắc"},
    "Hải Phòng":     {"lat": 20.8449, "lon": 106.6881, "region": "Bắc"},
    "Đà Nẵng":       {"lat": 16.0544, "lon": 108.2022, "region": "Trung"},
    "Huế":           {"lat": 16.4637, "lon": 107.5909, "region": "Trung"},
    "TP. Hồ Chí Minh": {"lat": 10.8231, "lon": 106.6297, "region": "Nam"},
    "Cần Thơ":       {"lat": 10.0452, "lon": 105.7469, "region": "Nam"},
}

BASE_URL = "https://archive-api.open-meteo.com/v1/archive"


class WeatherCollector:
    """Thu thập dữ liệu thời tiết lịch sử từ Open-Meteo API."""

    def __init__(self):
        """Initialize WeatherCollector."""
        self.cities = CITIES
        self.raw_data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
        os.makedirs(self.raw_data_dir, exist_ok=True)

    def fetch_city_data(self, city_name: str, start_date: str, end_date: str) -> dict:
        """
        Gọi API lấy dữ liệu thời tiết lịch sử cho một thành phố.

        Args:
            city_name: Tên thành phố (phải có trong CITIES).
            start_date: Ngày bắt đầu (YYYY-MM-DD).
            end_date: Ngày kết thúc (YYYY-MM-DD).

        Returns:
            dict chứa dữ liệu thời tiết hoặc empty dict nếu lỗi.
        """
        if city_name not in self.cities:
            print(f"  [ERROR] Thành phố '{city_name}' không có trong danh sách.")
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
            print(f"  Đang tải dữ liệu: {city_name} ({start_date} → {end_date})...")
            response = requests.get(BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Attach metadata
            data["city"] = city_name
            data["region"] = city_info["region"]
            return data

        except requests.exceptions.RequestException as e:
            print(f"  [ERROR] Lỗi kết nối khi tải {city_name}: {e}")
            return {}

    def collect_all(self, start_date: str = "2023-01-01", end_date: str = "2025-01-31") -> list:
        """
        Thu thập dữ liệu cho tất cả các thành phố và lưu vào file JSON.

        Args:
            start_date: Ngày bắt đầu.
            end_date: Ngày kết thúc.

        Returns:
            Danh sách các dict dữ liệu từng thành phố.
        """
        print("\n=== TASK 1: DATA COLLECTION ===")
        all_data = []

        for city_name in self.cities:
            city_data = self.fetch_city_data(city_name, start_date, end_date)
            if city_data:
                all_data.append(city_data)

        if all_data:
            self.save_raw_data(all_data)

        print(f"  Thu thập thành công {len(all_data)}/{len(self.cities)} thành phố.\n")
        return all_data

    def save_raw_data(self, data: list, filename: str = "weather_raw.json"):
        """
        Lưu raw data vào file JSON.

        Args:
            data: List dữ liệu thời tiết.
            filename: Tên file xuất.
        """
        filepath = os.path.join(self.raw_data_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  [OK] Đã lưu raw data: {filepath}")
