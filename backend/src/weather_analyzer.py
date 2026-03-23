"""
Task 3 & 4: Weather Analysis
Performs statistical analysis and generates weather-related insights.
"""

import os
import numpy as np
import pandas as pd

class WeatherAnalyzer:
    """Class for data aggregation and comparative analysis."""

    def __init__(self, df: pd.DataFrame):
        """Initializes report directory and weather dataset."""
        self.df = df
        base_dir = os.path.dirname(__file__)
        self.reports_dir = os.path.join(base_dir, "..", "outputs", "reports")
        os.makedirs(self.reports_dir, exist_ok=True)

    def get_summary_stats(self) -> pd.DataFrame:
        """Calculates descriptive statistics (mean, max, min) for each city."""
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
        return stats

    def get_monthly_average(self) -> pd.DataFrame:
        """Calculates monthly average statistics for each city."""
        monthly = self.df.groupby(["city", "month"]).agg(
            temp_mean=("temp_mean", "mean"),
            precipitation=("precipitation", "mean"),
            humidity=("humidity", "mean"),
        ).round(2)

        filepath = os.path.join(self.reports_dir, "monthly_average.csv")
        monthly.to_csv(filepath, encoding="utf-8-sig")
        return monthly

    def find_extreme_days(self) -> pd.DataFrame:
        """Identifies days with extremely high temperature or rainfall."""
        extreme = self.df[(self.df["is_hot_day"]) | (self.df["is_rainy_day"])].copy()
        extreme = extreme[["date", "city", "region", "temp_max", "precipitation"]].sort_values("date")

        filepath = os.path.join(self.reports_dir, "extreme_days.csv")
        extreme.to_csv(filepath, index=False, encoding="utf-8-sig")
        return extreme

    def compare_cities(self) -> pd.DataFrame:
        """Compares climate characteristics across North, Central, and South regions."""
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
        return region_stats

    def get_insights(self) -> dict:
        """Generates a dict of key insights for display."""
        insights = {}
        
        # City with largest temperature swing
        city_range = self.df.groupby("city").apply(
            lambda g: g["temp_max"].max() - g["temp_min"].min()
        )
        insights["largest_temp_range_city"] = city_range.idxmax()
        insights["largest_temp_range_value"] = round(float(city_range.max()), 1)

        # Count hot/rainy days
        insights["hot_days_by_city"] = self.df.groupby("city")["is_hot_day"].sum().sort_values(ascending=False).to_dict()
        insights["rainy_days_by_city"] = self.df.groupby("city")["is_rainy_day"].sum().sort_values(ascending=False).to_dict()

        # Find wettest month per region (using North, Central, South labels)
        monthly_rain = self.df.groupby(["region", "month"])["precipitation"].mean()
        wettest_months = {}
        for region in ["North", "Central", "South"]:
            if region in monthly_rain.index.get_level_values(0):
                wettest_months[region] = int(monthly_rain[region].idxmax())
        insights["wettest_month_by_region"] = wettest_months

        # Aggregated stats
        insights["total_records"] = len(self.df)
        insights["avg_temp_nationwide"] = round(float(self.df["temp_mean"].mean()), 1)
        insights["peak_temp"] = round(float(self.df["temp_max"].max()), 1)
        insights["lowest_temp"] = round(float(self.df["temp_min"].min()), 1)
        insights["total_rainfall"] = round(float(self.df["precipitation"].sum()), 1)

        return insights

    def print_insights(self):
        """Prints high-level analytical insights to console."""
        insights = self.get_insights()
        print("\n--- ANALYTICAL INSIGHTS ---")
        print(f"  City with widest temp range: {insights['largest_temp_range_city']}")
        
        print("  Heatwave counts (>35°C):")
        for city, days in insights["hot_days_by_city"].items():
            print(f"    - {city}: {days} days")

        for region, month in insights["wettest_month_by_region"].items():
            print(f"  Region {region} wettest month: {month}")
