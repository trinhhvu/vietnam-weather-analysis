"""
Frontend Dashboard - Giao diện trực quan hóa thời tiết Việt Nam.

QUAN TRỌNG: File này KHÔNG chứa bất kỳ logic xử lý dữ liệu nào.
Mọi dữ liệu được lấy từ Backend API (Flask) qua HTTP requests.

Frontend chỉ làm 2 việc:
  1. Gọi API từ Backend
  2. Hiển thị dữ liệu lên giao diện Streamlit

Usage:
    streamlit run frontend/dashboard.py
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import subprocess
import time
import os
import sys

# ------------------------------------------------------------------ #
# HỖ TRỢ DEPLOY (Tự động khởi động Backend API)                       #
# ------------------------------------------------------------------ #
def ensure_backend_running():
    """Kiểm tra và khởi động Backend API nếu chưa chạy."""
    try:
        # Thử gọi API để kiểm tra trạng thái
        requests.get("http://localhost:5001/api/cities", timeout=1)
    except:
        # Nếu lỗi (chưa chạy) -> khởi động backend/api.py
        with st.spinner("⏳ Đang khởi động Backend API..."):
            backend_script = os.path.join(os.getcwd(), "backend", "api.py")
            if os.path.exists(backend_script):
                subprocess.Popen([sys.executable, backend_script])
                time.sleep(5)  # Đợi 5s để Flask kịp khởi động
            else:
                st.error(f"❌ Không tìm thấy file backend: {backend_script}")
                st.stop()

# Gọi hàm kiểm tra ngay khi load dashboard
ensure_backend_running()

# ------------------------------------------------------------------ #
# CẤU HÌNH                                                            #
# ------------------------------------------------------------------ #
API_BASE = "http://localhost:5001"

st.set_page_config(
    page_title="Vietnam Weather Dashboard",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------ #
# CUSTOM CSS - Giao diện iOS Weather (Glassmorphism)                   #
# ------------------------------------------------------------------ #
st.markdown("""
    <style>
    /* Tổng thể và Font */
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
# HELPER: Gọi API từ Backend                                          #
# ------------------------------------------------------------------ #
def call_api(endpoint, params=None):
    """Gọi Backend API và trả về JSON response."""
    try:
        resp = requests.get(f"{API_BASE}{endpoint}", params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Không thể kết nối Backend API! Hãy chạy `python backend/api.py` trước.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Lỗi khi gọi API: {e}")
        st.stop()


# ------------------------------------------------------------------ #
# SIDEBAR FILTERS                                                     #
# ------------------------------------------------------------------ #
st.sidebar.title("☁️ Weather Menu")

# Lấy danh sách cities & years từ API
meta = call_api("/api/cities")
all_cities = meta["cities"]
all_years = meta["years"]

city_list = ["Tất cả"] + all_cities
selected_city = st.sidebar.selectbox("Chọn Thành phố", city_list)

selected_year = st.sidebar.multiselect("Chọn Năm", all_years, default=all_years)

# Build query params cho API
api_params = {}
if selected_city != "Tất cả":
    api_params["city"] = selected_city
if selected_year:
    api_params["year"] = ",".join(map(str, selected_year))


# ------------------------------------------------------------------ #
# MAIN PAGE                                                            #
# ------------------------------------------------------------------ #
st.title("🇻🇳 Báo Cáo Thời Tiết Việt Nam")
st.subheader(f"Dữ liệu: {selected_city if selected_city != 'Tất cả' else 'Toàn quốc'} ({', '.join(map(str, selected_year))})")

# 1. KPI Metrics — lấy từ /api/summary
summary = call_api("/api/summary", api_params)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Nhiệt độ TB</div>
        <div class="metric-value">{summary['avg_temp']:.1f}°C</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Cao nhất</div>
        <div class="metric-value" style="color: #ff6b6b;">{summary['max_temp']:.1f}°C</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Thấp nhất</div>
        <div class="metric-value" style="color: #4facfe;">{summary['min_temp']:.1f}°C</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Lượng mưa tổng</div>
        <div class="metric-value">{summary['total_rain']:,.0f} mm</div>
    </div>""", unsafe_allow_html=True)

st.write("")  # Spacer

# 2. Charts — lấy dữ liệu từ /api/data
data_response = call_api("/api/data", api_params)
filtered_df = pd.DataFrame(data_response["data"])

if not filtered_df.empty:
    filtered_df["date"] = pd.to_datetime(filtered_df["date"])

    c1, c2 = st.columns([2, 1])

    with c1:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.write("### 📈 Xu hướng nhiệt độ")
        trend_df = filtered_df.groupby(['date', 'city'])['temp_mean'].mean().reset_index()
        fig_line = px.line(
            trend_df, x='date', y='temp_mean', color='city',
            labels={'temp_mean': 'Nhiệt độ (°C)', 'date': 'Thời gian'},
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_line.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.write("### 🌡️ Phân bố nhiệt độ")
        fig_box = px.box(
            filtered_df, x='city', y='temp_mean', color='city',
            template="plotly_dark"
        )
        fig_box.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 3. Heatmap
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.write("### 🗓️ Heatmap: Nhiệt độ TB theo tháng")
    pivot = filtered_df.pivot_table(
        values="temp_mean", index="city", columns="month", aggfunc="mean"
    )
    fig_heat = px.imshow(
        pivot, text_auto=".1f", aspect="auto",
        color_continuous_scale="RdYlBu_r",
        labels=dict(x="Tháng", y="Thành phố", color="Temp"),
        template="plotly_dark"
    )
    st.plotly_chart(fig_heat, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 4. Insights — lấy từ /api/insights
    st.write("### 💡 Phân tích & Nhận xét")
    insights = call_api("/api/insights")

    i1, i2 = st.columns(2)
    with i1:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.write("#### 🌡️ Đặc điểm nhiệt độ")
        st.markdown(f"""
        - **Nóng nhất:** {insights['largest_temp_range_city']} có biên độ nhiệt **{insights['largest_temp_range_value']}°C**.
        - **Nhiệt độ đỉnh:** **{insights['peak_temp']}°C** | Thấp nhất: **{insights['lowest_temp']}°C**
        - **TB toàn quốc:** **{insights['avg_temp_nationwide']}°C**
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    with i2:
        st.markdown('<div class="chart-box">', unsafe_allow_html=True)
        st.write("#### 🌧️ Lượng mưa & Cực đoan")
        hot_total = sum(insights["hot_days_by_city"].values())
        rainy_total = sum(insights["rainy_days_by_city"].values())
        wettest = insights["wettest_month_by_region"]
        st.markdown(f"""
        - **Sự kiện cực đoan:** **{hot_total}** ngày nắng nóng (>35°C) và **{rainy_total}** ngày mưa lớn (>50mm).
        - **Mưa nhiều nhất:** Bắc (T{wettest.get('Bắc','?')}), Trung (T{wettest.get('Trung','?')}), Nam (T{wettest.get('Nam','?')})
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    # 5. Data Table
    with st.expander("🔍 Xem dữ liệu chi tiết"):
        st.dataframe(filtered_df.sort_values('date', ascending=False).head(100), use_container_width=True)

else:
    st.warning("Không có dữ liệu phù hợp với bộ lọc đã chọn.")

st.markdown("---")
st.markdown("<p style='text-align: center; opacity: 0.7;'>Vietnam Weather Analysis Project | PDS301m Assignment</p>", unsafe_allow_html=True)
