"""
Frontend Dashboard - Visualizing Vietnam Weather Data.

IMPORTANT: This file DOES NOT contain data processing logic.
All data is fetched from the Backend API (Flask) via HTTP requests.

Frontend tasks:
  1. Call Backend API
  2. Display data using Streamlit

Usage:
    streamlit run frontend/dashboard.py
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import threading
import time
import sys
import os

# Add root directory to sys.path to allow importing from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from backend.api import app as flask_app
except ImportError:
    st.error("❌ Could not import backend.api. Ensure project structure is correct.")
    st.stop()

def run_backend():
    """Run the Flask app in a separate thread."""
    flask_app.run(port=5001, debug=False, use_reloader=False)

# ------------------------------------------------------------------ #
# PAGE CONFIGURATION                                                  #
# ------------------------------------------------------------------ #
st.set_page_config(
    page_title="Vietnam Weather Dashboard",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE = "http://localhost:5001"

# ------------------------------------------------------------------ #
# LOADING / WAIT FOR BACKEND                                          #
# ------------------------------------------------------------------ #
def check_backend():
    """Check if the backend is responding."""
    try:
        requests.get(f"{API_BASE}/api/cities", timeout=1)
        return True
    except:
        return False

def show_loading_screen():
    """A visual splash screen during initial startup."""
    placeholder = st.empty()
    
    with placeholder.container():
        st.markdown("""
            <style>
            .loader-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 70vh;
                text-align: center;
            }
            .spinner-io {
                width: 80px;
                height: 80px;
                border: 8px solid rgba(255, 255, 255, 0.1);
                border-top: 8px solid #a5c9ff;
                border-radius: 50%;
                animation: spin_io 1.5s linear infinite;
                margin-bottom: 20px;
            }
            @keyframes spin_io {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .loading-text {
                font-family: 'Outfit', sans-serif;
                font-size: 1.5rem;
                color: #a5c9ff;
                font-weight: 600;
                letter-spacing: 2px;
            }
            </style>
            <div class="loader-container">
                <div class="spinner-io"></div>
                <div class="loading-text">INITIALIZING ANALYSIS SYSTEM...</div>
                <p style='color: #888; margin-top: 10px;'>Warming up Backend API (Port 5001)</p>
            </div>
        """, unsafe_allow_html=True)

        # Attempt to start backend in a thread if not responding
        if not check_backend():
            thread = threading.Thread(target=run_backend, daemon=True)
            thread.start()
            
            # Wait up to 10 seconds for initial load
            for i in range(10):
                time.sleep(1)
                if check_backend():
                    break
        
        if not check_backend():
            st.error("❌ Connection failed. The background API cannot be reached.")
            st.warning("Please ensure port 5001 is available.")
            st.stop()
            
    # Remove loading screen after success
    placeholder.empty()

# Show splash screen on first session load
if "loaded" not in st.session_state:
    show_loading_screen()
    st.session_state["loaded"] = True

# ------------------------------------------------------------------ #
# CUSTOM CSS - iOS Weather Style (Glassmorphism)                      #
# ------------------------------------------------------------------ #
st.markdown("""
    <style>
    /* Global and Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Outfit', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        color: white;
    }
    
    h1, h2, h3 {
        background: linear-gradient(to right, #ffffff, #a5c9ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }

    p, span, label {
        color: #e0e0e0 !important;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 24px;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        transition: transform 0.3s ease, background 0.3s ease;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    .metric-card:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 5px 0;
    }

    .metric-label {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        opacity: 0.8;
    }
    
    section[data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(10px);
    }
    
    .chart-box {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 24px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 30px;
    }

    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: rgba(0,0,0,0.1); }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------ #
# HELPER: API Fetcher                                                 #
# ------------------------------------------------------------------ #
def call_api(endpoint, params=None):
    """Fetch data from Backend API and return JSON."""
    try:
        resp = requests.get(f"{API_BASE}{endpoint}", params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to Backend API! Please run `python backend/api.py` first.")
        st.stop()
    except Exception as e:
        st.error(f"❌ API Error: {e}")
        st.stop()


# ------------------------------------------------------------------ #
# SIDEBAR FILTERS                                                     #
# ------------------------------------------------------------------ #
st.sidebar.title("☁️ Weather Menu")

# Fetch cities & years from API
meta = call_api("/api/cities")
all_cities = meta["cities"]
all_years = meta["years"]

city_list = all_cities
selected_cities = st.sidebar.multiselect("Select Cities", city_list, default=all_cities)

selected_year = st.sidebar.multiselect("Select Year", all_years, default=all_years)

# Build query params for API
api_params = {}
if selected_cities:
    api_params["city"] = ",".join(selected_cities)
if selected_year:
    api_params["year"] = ",".join(map(str, selected_year))


# ------------------------------------------------------------------ #
# MAIN PAGE                                                            #
# ------------------------------------------------------------------ #
st.title("🇻🇳 Vietnam Weather Analysis Report")

# Display city names in subheader
city_display = "All Cities" if len(selected_cities) == len(all_cities) else ", ".join(selected_cities)
st.subheader(f"Dataset: {city_display} ({', '.join(map(str, selected_year))})")

# 1. KPI Metrics — from /api/summary
summary = call_api("/api/summary", api_params)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Avg Temperature</div>
        <div class="metric-value">{summary['avg_temp']:.1f}°C</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Max Temp</div>
        <div class="metric-value" style="color: #ff6b6b;">{summary['max_temp']:.1f}°C</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Min Temp</div>
        <div class="metric-value" style="color: #4facfe;">{summary['min_temp']:.1f}°C</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Total Rainfall</div>
        <div class="metric-value">{summary['total_rain']:,.0f} mm</div>
    </div>""", unsafe_allow_html=True)

st.write("")  # Spacer

# 2. Charts — from /api/data
data_response = call_api("/api/data", api_params)
filtered_df = pd.DataFrame(data_response["data"])

if not filtered_df.empty:
    filtered_df["date"] = pd.to_datetime(filtered_df["date"])

    c1, c2 = st.columns([2, 1])

    with c1:
        st.write("### 📈 Temperature Trends")
        trend_df = filtered_df.groupby(['date', 'city'])['temp_mean'].mean().reset_index()
        fig_line = px.line(
            trend_df, x='date', y='temp_mean', color='city',
            labels={'temp_mean': 'Temperature (°C)', 'date': 'Time'},
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_line.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig_line, use_container_width=True)

    with c2:
        st.write("### 🌡️ Temp Distribution")
        fig_box = px.box(
            filtered_df, x='city', y='temp_mean', color='city',
            template="plotly_dark"
        )
        fig_box.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

    # 3. Heatmap
    st.write("---")
    st.write("### 🗓️ Heatmap: Avg Temp by Month")
    pivot = filtered_df.pivot_table(
        values="temp_mean", index="city", columns="month", aggfunc="mean"
    )
    fig_heat = px.imshow(
        pivot, text_auto=".1f", aspect="auto",
        color_continuous_scale="RdYlBu_r",
        labels=dict(x="Month", y="City", color="Temp"),
        template="plotly_dark"
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    # 4. Insights — from /api/insights
    st.write("### 💡 Insights & Analysis")
    insights = call_api("/api/insights")

    i1, i2 = st.columns(2)
    with i1:
        st.markdown(f"""
        <div class="chart-box">
            <h4 style='margin-top:0;'>🌡️ Temp Characteristics</h4>
            <ul style='margin-bottom:0;'>
                <li><b>Hottest:</b> {insights['largest_temp_range_city']} has a temp range of <b>{insights['largest_temp_range_value']}°C</b>.</li>
                <li><b>Peak Temp:</b> <b>{insights['peak_temp']}°C</b> | Lowest: <b>{insights['lowest_temp']}°C</b></li>
                <li><b>National Avg:</b> <b>{insights['avg_temp_nationwide']}°C</b></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with i2:
        hot_total = sum(insights["hot_days_by_city"].values())
        rainy_total = sum(insights["rainy_days_by_city"].values())
        wettest = insights["wettest_month_by_region"]
        st.markdown(f"""
        <div class="chart-box">
            <h4 style='margin-top:0;'>🌧️ Rainfall & Extremes</h4>
            <ul style='margin-bottom:0;'>
                <li><b>Extreme events:</b> <b>{hot_total}</b> heatwave days (>35°C) and <b>{rainy_total}</b> heavy rain days (>50mm).</li>
                <li><b>Wettest Month:</b> North ({wettest.get('Bắc','?')}), Central ({wettest.get('Trung','?')}), South ({wettest.get('Nam','?')})</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # 5. Data Table
    with st.expander("🔍 View detailed data"):
        st.dataframe(filtered_df.sort_values('date', ascending=False).head(100), use_container_width=True)

else:
    st.warning("No data matches the selected filters.")

# ------------------------------------------------------------------ #
# FOOTER                                                              #
# ------------------------------------------------------------------ #
st.sidebar.markdown("---")
st.sidebar.markdown(f"""
    <div style='text-align: center; opacity: 0.8;'>
        <p>Developed by</p>
        <a href='https://github.com/trinhhvu' target='_blank' style='text-decoration: none;'>
            <img src='https://img.shields.io/badge/GitHub-trinhhvu-blue?style=for-the-badge&logo=github' alt='GitHub'>
        </a>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
    <p style='text-align: center; opacity: 0.7;'>
        <b>Vietnam Weather Analysis Project</b> | PDS301m Assignment <br>
        Developed by <a href='https://github.com/trinhhvu' target='_blank' style='color: #a5c9ff; text-decoration: none;'>@trinhhvu</a>
    </p>
""", unsafe_allow_html=True)
