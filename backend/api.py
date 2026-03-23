"""
Backend API - Provides weather data to the Frontend via REST API.
Uses Flask to create JSON endpoints.
"""

import os
import sys
import io
from flask import Flask, jsonify, request

# Fix for Unicode output in Windows terminal
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from data_processor import DataProcessor
from weather_analyzer import WeatherAnalyzer
from weather_collector import WeatherCollector

app = Flask(__name__)

# Load data once at server startup
print("[API] Initializing data layer...")
backend_dir = os.path.dirname(os.path.abspath(__file__))
raw_path = os.path.join(backend_dir, "data", "raw", "weather_raw.json")

def _load_data():
    """Initial data load and processing on startup."""
    if not os.path.exists(raw_path):
        print(f"[API] Data not found at {raw_path}. Collecting from Open-Meteo...")
        WeatherCollector().collect_all()

    processor = DataProcessor()
    # Process relative to data directory
    raw_data = processor.load_data("weather_raw.json")
    return processor.clean_data(raw_data)

df = _load_data()
analyzer = WeatherAnalyzer(df)
print(f"[API] Ready! ({len(df)} records loaded)")

def _df_to_json(dataframe):
    """Convert DataFrame to list of dicts with string dates."""
    result = dataframe.copy()
    for col in result.columns:
        if hasattr(result[col], 'dt'):
            result[col] = result[col].astype(str)
    return result.to_dict(orient="records")

def _filter_dataframe(dataset):
    """Common filtering logic for endpoints."""
    filtered = dataset.copy()
    
    city = request.args.get("city")
    if city and city.lower() != "all":
        city_list = city.split(",")
        filtered = filtered[filtered["city"].isin(city_list)]

    years = request.args.get("year")
    if years:
        year_list = [int(y) for y in years.split(",")]
        filtered = filtered[filtered["year"].isin(year_list)]
    
    return filtered

# --- API ENDPOINTS ---

@app.route("/api/data", methods=["GET"])
def get_data():
    """Returns filtered weather dataset."""
    filtered = _filter_dataframe(df)
    return jsonify({
        "total": len(filtered),
        "data": _df_to_json(filtered)
    })

@app.route("/api/summary", methods=["GET"])
def get_summary():
    """Returns aggregated KPI stats."""
    filtered = _filter_dataframe(df)
    if filtered.empty:
        return jsonify({"error": "No data found for the given filters"}), 404
        
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
    """Returns monthly average weather data."""
    return jsonify(_df_to_json(analyzer.get_monthly_average().reset_index()))

@app.route("/api/extremes", methods=["GET"])
def get_extremes():
    """Returns specific extreme weather events."""
    extreme = analyzer.find_extreme_days()
    return jsonify({
        "total": len(extreme),
        "data": _df_to_json(extreme)
    })

@app.route("/api/comparison", methods=["GET"])
def get_comparison():
    """Returns climate comparison between North, Central, and South regions."""
    return jsonify(_df_to_json(analyzer.compare_cities().reset_index()))

@app.route("/api/insights", methods=["GET"])
def get_insights():
    """Returns analytical insights generated from the data."""
    return jsonify(analyzer.get_insights())

@app.route("/api/cities", methods=["GET"])
def get_cities():
    """Returns a list of available cities and years in the dataset."""
    return jsonify({
        "cities": df["city"].unique().tolist(),
        "years": sorted(df["year"].unique().tolist()),
    })

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  WEATHER BACKEND API - Running on Port 5001")
    print("=" * 50)
    app.run(port=5001, debug=False)
