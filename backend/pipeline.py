"""
Task 5: Scripting & Automation
pipeline.py - Orchestrates the full Vietnam Weather Analysis pipeline.
"""

import os
import sys
import io

# Setup for Windows terminal Unicode output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add src to system path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from weather_collector import WeatherCollector
from data_processor import DataProcessor
from weather_analyzer import WeatherAnalyzer
from visualizer import Visualizer

def run_pipeline():
    """Execute pipeline: Collect → Process → Analyze → Visualize.”""
    print("=" * 55)
    print("  VIETNAM WEATHER ANALYSIS PIPELINE (2023-2025)")
    print("=" * 55)

    backend_dir = os.path.dirname(os.path.abspath(__file__))
    raw_path = os.path.join(backend_dir, "data", "raw", "weather_raw.json")

    # 1. DATA COLLECTION
    if not os.path.exists(raw_path):
        print("\n[PIPELINE] Collecting data from Open-Meteo API...")
        WeatherCollector().collect_all(start_date="2023-01-01", end_date="2025-01-31")
    else:
        print(f"\n[PIPELINE] Data already exists at: {raw_path}")

    # 2. DATA PROCESSING
    print("\n[PIPELINE] Cleaning and transforming data...")
    processor = DataProcessor()
    raw_data = processor.load_data("weather_raw.json")
    df = processor.clean_data(raw_data)
    processor.export_results("weather_cleaned.csv")

    # Stats Summary
    print(f"\n  Final dataset size: {df.shape}")
    print(f"  Cities: {df['city'].unique().tolist()}")
    print(f"  Dates: {df['date'].min().date()} to {df['date'].max().date()}")

    # 3. STATISTICAL ANALYSIS
    print("\n[PIPELINE] Analyzing weather patterns...")
    analyzer = WeatherAnalyzer(df)
    analyzer.get_summary_stats()
    analyzer.get_monthly_average()
    analyzer.find_extreme_days()
    analyzer.compare_cities()
    analyzer.print_insights()

    # 4. VISUALIZATION
    print("\n[PIPELINE] Generating trend charts and heatmaps...")
    Visualizer(df).generate_all()

    print("\n" + "=" * 55)
    print("  COMPLETED! Results available in backend/outputs/")
    print("=" * 55)

    return df

if __name__ == "__main__":
    run_pipeline()
