"""
Task 3 (OOP) + Task 4: Weather Analysis
WeatherAnalyzer class - Phân tích thống kê dữ liệu thời tiết.
"""

import os
import numpy as np
import pandas as pd


class WeatherAnalyzer:
    """Phân tích thống kê và so sánh thời tiết giữa các thành phố."""

    def __init__(self, df: pd.DataFrame):
        """
        Initialize WeatherAnalyzer với DataFrame đã được làm sạch.

        Args:
            df: DataFrame từ DataProcessor.clean_data().
        """
        self.df = df
        base_dir = os.path.dirname(__file__)
        self.reports_dir = os.path.join(base_dir, "..", "outputs", "reports")
        os.makedirs(self.reports_dir, exist_ok=True)

    def get_summary_stats(self) -> pd.DataFrame:
        """
        Tính thống kê mô tả (mean, max, min, std) theo từng thành phố.

        Returns:
            DataFrame thống kê tổng hợp.
        """
        stats = self.df.groupby("city").agg(
            temp_mean_avg=("temp_mean", "mean"),
            temp_max_peak=("temp_max", "max"),
            temp_min_lowest=("temp_min", "min"),
            temp_range=("temp_max", lambda x: x.max() - self.df.loc[x.index, "temp_min"].min()),
            precipitation_avg=("precipitation", "mean"),
            precipitation_total=("precipitation", "sum"),
            wind_speed_avg=("wind_speed", "mean"),
            humidity_avg=("humidity", "mean"),
            hot_days=("is_hot_day", "sum"),
            rainy_days=("is_rainy_day", "sum"),
        ).round(2)

        filepath = os.path.join(self.reports_dir, "summary_stats.csv")
        stats.to_csv(filepath, encoding="utf-8-sig")
        print(f"  [OK] Đã xuất summary stats: {filepath}")
        return stats

    def get_monthly_average(self) -> pd.DataFrame:
        """
        Tính nhiệt độ trung bình theo từng tháng và từng thành phố.

        Returns:
            DataFrame nhiệt độ trung bình theo tháng.
        """
        monthly = self.df.groupby(["city", "month"]).agg(
            temp_mean=("temp_mean", "mean"),
            precipitation=("precipitation", "mean"),
            humidity=("humidity", "mean"),
        ).round(2)

        filepath = os.path.join(self.reports_dir, "monthly_average.csv")
        monthly.to_csv(filepath, encoding="utf-8-sig")
        print(f"  [OK] Đã xuất monthly average: {filepath}")
        return monthly

    def find_extreme_days(self) -> pd.DataFrame:
        """
        Tìm các ngày thời tiết cực đoan (nhiệt độ > 35°C hoặc mưa > 50mm).

        Returns:
            DataFrame các ngày cực đoan.
        """
        extreme = self.df[(self.df["is_hot_day"]) | (self.df["is_rainy_day"])].copy()
        extreme = extreme[["date", "city", "region", "temp_max", "precipitation"]].sort_values("date")

        filepath = os.path.join(self.reports_dir, "extreme_days.csv")
        extreme.to_csv(filepath, index=False, encoding="utf-8-sig")
        print(f"  [OK] Đã xuất extreme days: {filepath}")
        return extreme

    def compare_cities(self) -> pd.DataFrame:
        """
        So sánh khí hậu giữa các vùng miền (Bắc - Trung - Nam).

        Returns:
            DataFrame so sánh theo vùng miền.
        """
        region_stats = self.df.groupby("region").agg(
            temp_mean_avg=("temp_mean", "mean"),
            temp_max_avg=("temp_max", "mean"),
            temp_min_avg=("temp_min", "mean"),
            precipitation_avg=("precipitation", "mean"),
            humidity_avg=("humidity", "mean"),
            hot_days_total=("is_hot_day", "sum"),
        ).round(2)

        filepath = os.path.join(self.reports_dir, "city_comparison.csv")
        region_stats.to_csv(filepath, encoding="utf-8-sig")
        print(f"  [OK] Đã xuất city comparison: {filepath}")
        return region_stats

    def get_insights(self) -> dict:
        """
        Tạo nhận xét/insights chính từ dữ liệu và trả về dưới dạng dict.

        Returns:
            dict chứa các insights key-value.
        """
        insights = {}

        # City with largest temperature range
        city_range = self.df.groupby("city").apply(
            lambda g: g["temp_max"].max() - g["temp_min"].min()
        )
        insights["largest_temp_range_city"] = city_range.idxmax()
        insights["largest_temp_range_value"] = round(float(city_range.max()), 1)

        # Hot days per city
        hot = self.df.groupby("city")["is_hot_day"].sum().sort_values(ascending=False)
        insights["hot_days_by_city"] = hot.to_dict()

        # Rainy days per city
        rainy = self.df.groupby("city")["is_rainy_day"].sum().sort_values(ascending=False)
        insights["rainy_days_by_city"] = rainy.to_dict()

        # Wettest month per region
        monthly_rain = self.df.groupby(["region", "month"])["precipitation"].mean()
        wettest_months = {}
        for region in ["Bắc", "Trung", "Nam"]:
            if region in monthly_rain.index.get_level_values(0):
                wettest_months[region] = int(monthly_rain[region].idxmax())
        insights["wettest_month_by_region"] = wettest_months

        # Overall stats
        insights["total_records"] = len(self.df)
        insights["avg_temp_nationwide"] = round(float(self.df["temp_mean"].mean()), 1)
        insights["peak_temp"] = round(float(self.df["temp_max"].max()), 1)
        insights["lowest_temp"] = round(float(self.df["temp_min"].min()), 1)
        insights["total_rainfall"] = round(float(self.df["precipitation"].sum()), 1)

        return insights

    def print_insights(self):
        """In các nhận xét/insights chính từ dữ liệu ra console."""
        insights = self.get_insights()
        print("\n--- INSIGHTS ---")
        print(f"  Thành phố biên độ nhiệt lớn nhất: {insights['largest_temp_range_city']}")

        hot = insights["hot_days_by_city"]
        hot_str = "\n".join([f"    {city}: {days}" for city, days in hot.items()])
        print(f"  Ngày nắng nóng (>35°C) theo thành phố:\n{hot_str}")

        for region, month in insights["wettest_month_by_region"].items():
            print(f"  Tháng mưa nhiều nhất ở miền {region}: Tháng {month}")
