"""
Task 5: Scripting & Automation
pipeline.py - Script chạy toàn bộ Vietnam Weather Analysis pipeline.

Usage:
    python backend/pipeline.py
"""

import os
import sys
import io

# Fix for Unicode output in Windows terminal (Vietnamese characters)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from weather_collector import WeatherCollector
from data_processor import DataProcessor
from weather_analyzer import WeatherAnalyzer
from visualizer import Visualizer


def run_pipeline():
    """Chạy toàn bộ pipeline: Collect → Process → Analyze → Visualize → Export."""
    print("=" * 55)
    print("  VIETNAM WEATHER ANALYSIS 2023-2025")
    print("  PDS301m - Python for Applied Data Science")
    print("=" * 55)

    backend_dir = os.path.dirname(os.path.abspath(__file__))
    raw_json_path = os.path.join(backend_dir, "data", "raw", "weather_raw.json")

    # ------------------------------------------------------------------ #
    # TASK 1: Data Collection                                              #
    # ------------------------------------------------------------------ #
    if not os.path.exists(raw_json_path):
        print("\n[TASK 1] Bắt đầu thu thập dữ liệu từ Open-Meteo API...")
        collector = WeatherCollector()
        collector.collect_all(start_date="2023-01-01", end_date="2025-01-31")
    else:
        print(f"\n[TASK 1] Raw data đã tồn tại: {raw_json_path}. Bỏ qua bước thu thập.")

    # ------------------------------------------------------------------ #
    # TASK 2 & 3: Data Processing & OOP                                   #
    # ------------------------------------------------------------------ #
    print("\n[TASK 2] Bắt đầu xử lý và làm sạch dữ liệu...")
    processor = DataProcessor()
    raw_data = processor.load_data("weather_raw.json")
    df = processor.clean_data(raw_data)
    processor.export_results("weather_cleaned.csv")

    print(f"\n  DataFrame shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Thành phố: {df['city'].unique().tolist()}")
    print(f"  Thời gian: {df['date'].min().date()} → {df['date'].max().date()}")
    print(f"  Missing values: {df.isnull().sum().sum()}")

    # ------------------------------------------------------------------ #
    # TASK 3 (cont): Weather Analysis                                      #
    # ------------------------------------------------------------------ #
    print("\n[TASK 3] Bắt đầu phân tích thống kê...")
    analyzer = WeatherAnalyzer(df)
    summary = analyzer.get_summary_stats()
    monthly = analyzer.get_monthly_average()
    extreme = analyzer.find_extreme_days()
    comparison = analyzer.compare_cities()
    analyzer.print_insights()

    print(f"\n  Tổng ngày cực đoan: {len(extreme)}")
    print(f"\n--- Summary Stats ---")
    print(summary.to_string())
    print(f"\n--- Regional Comparison ---")
    print(comparison.to_string())

    # ------------------------------------------------------------------ #
    # TASK 4: Visualization                                                #
    # ------------------------------------------------------------------ #
    print("\n[TASK 4] Tạo biểu đồ...")
    viz = Visualizer(df)
    viz.generate_all()

    # ------------------------------------------------------------------ #
    # Done                                                                 #
    # ------------------------------------------------------------------ #
    print("\n" + "=" * 55)
    print("  HOÀN THÀNH! Kết quả lưu tại thư mục backend/outputs/")
    print("=" * 55)

    return df


if __name__ == "__main__":
    run_pipeline()
