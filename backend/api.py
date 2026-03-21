"""
Backend API - Cung cấp dữ liệu thời tiết cho Frontend thông qua REST API.
Sử dụng Flask để tạo các endpoint JSON.
"""

import os
import sys
import io

# Fix for Unicode output in Windows terminal
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from flask import Flask, jsonify, request
from data_processor import DataProcessor
from weather_analyzer import WeatherAnalyzer
from weather_collector import WeatherCollector

app = Flask(__name__)

# ------------------------------------------------------------------ #
# LOAD DATA khi khởi động API                                         #
# ------------------------------------------------------------------ #
def _load_data():
    """Load và xử lý dữ liệu khi API khởi động."""
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    raw_path = os.path.join(backend_dir, "data", "raw", "weather_raw.json")

    # Nếu chưa có raw data → chạy collector
    if not os.path.exists(raw_path):
        print("[API] Chưa có dữ liệu. Đang thu thập từ API...")
        collector = WeatherCollector()
        collector.collect_all()

    processor = DataProcessor()
    raw_data = processor.load_data("weather_raw.json")
    df = processor.clean_data(raw_data)
    return df


# Load data 1 lần khi server start
print("[API] Đang tải dữ liệu...")
df = _load_data()
analyzer = WeatherAnalyzer(df)
print(f"[API] Sẵn sàng! ({len(df)} records)")


# ------------------------------------------------------------------ #
# HELPER: Convert DataFrame → JSON-friendly format                     #
# ------------------------------------------------------------------ #
def _df_to_json(dataframe):
    """Convert DataFrame sang list of dicts, xử lý datetime."""
    result = dataframe.copy()
    for col in result.columns:
        if hasattr(result[col], 'dt'):
            result[col] = result[col].astype(str)
    return result.to_dict(orient="records")


# ------------------------------------------------------------------ #
# API ENDPOINTS                                                        #
# ------------------------------------------------------------------ #

@app.route("/api/data", methods=["GET"])
def get_data():
    """
    Trả về dữ liệu đã lọc theo city và year.
    Query params: ?city=Hà Nội&year=2023,2024
    """
    filtered = df.copy()

    city = request.args.get("city")
    if city and city != "all":
        filtered = filtered[filtered["city"] == city]

    years = request.args.get("year")
    if years:
        year_list = [int(y) for y in years.split(",")]
        filtered = filtered[filtered["year"].isin(year_list)]

    return jsonify({
        "total": len(filtered),
        "data": _df_to_json(filtered)
    })


@app.route("/api/summary", methods=["GET"])
def get_summary():
    """Trả về thống kê tổng hợp (KPI) theo city và year."""
    filtered = df.copy()

    city = request.args.get("city")
    if city and city != "all":
        filtered = filtered[filtered["city"] == city]

    years = request.args.get("year")
    if years:
        year_list = [int(y) for y in years.split(",")]
        filtered = filtered[filtered["year"].isin(year_list)]

    summary = {
        "avg_temp": round(float(filtered["temp_mean"].mean()), 1),
        "max_temp": round(float(filtered["temp_max"].max()), 1),
        "min_temp": round(float(filtered["temp_min"].min()), 1),
        "total_rain": round(float(filtered["precipitation"].sum()), 1),
        "total_records": len(filtered),
        "cities": filtered["city"].unique().tolist(),
        "years": sorted(filtered["year"].unique().tolist()),
    }
    return jsonify(summary)


@app.route("/api/monthly", methods=["GET"])
def get_monthly():
    """Trả về trung bình nhiệt độ theo tháng."""
    monthly = analyzer.get_monthly_average()
    monthly_reset = monthly.reset_index()
    return jsonify(_df_to_json(monthly_reset))


@app.route("/api/extremes", methods=["GET"])
def get_extremes():
    """Trả về các ngày thời tiết cực đoan."""
    extreme = analyzer.find_extreme_days()
    return jsonify({
        "total": len(extreme),
        "data": _df_to_json(extreme)
    })


@app.route("/api/comparison", methods=["GET"])
def get_comparison():
    """Trả về so sánh khí hậu giữa các vùng miền."""
    comparison = analyzer.compare_cities()
    comparison_reset = comparison.reset_index()
    return jsonify(_df_to_json(comparison_reset))


@app.route("/api/insights", methods=["GET"])
def get_insights():
    """Trả về nhận xét & insights chính."""
    insights = analyzer.get_insights()
    return jsonify(insights)


@app.route("/api/cities", methods=["GET"])
def get_cities():
    """Trả về danh sách thành phố và năm có trong dữ liệu."""
    return jsonify({
        "cities": df["city"].unique().tolist(),
        "years": sorted(df["year"].unique().tolist()),
    })


# ------------------------------------------------------------------ #
# RUN SERVER                                                           #
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  WEATHER BACKEND API")
    print("  Endpoints: /api/data, /api/summary, /api/monthly,")
    print("             /api/extremes, /api/comparison, /api/insights")
    print("=" * 50)
    app.run(port=5001, debug=False)
