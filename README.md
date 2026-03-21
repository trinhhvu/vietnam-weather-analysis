# 🌤️ Vietnam Weather Analysis (2023–2025)

> An end-to-end data science project analyzing and comparing historical weather patterns across 6 major Vietnamese cities — built with Python, Pandas, Flask API, and an interactive Streamlit dashboard.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data_Processing-150458?style=flat-square&logo=pandas)](https://pandas.pydata.org/)
[![Flask](https://img.shields.io/badge/Flask-Backend_API-000000?style=flat-square&logo=flask)](https://flask.palletsprojects.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat-square&logo=streamlit)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive_Charts-3F4F75?style=flat-square&logo=plotly)](https://plotly.com/)
[![Status](https://img.shields.io/badge/Status-Completed-brightgreen?style=flat-square)]()

---

## 📌 Overview

This project collects 2 years of daily weather data (Jan 2023 – Jan 2025) from the **Open-Meteo Historical API** for 6 Vietnamese cities across 3 regions. It then processes, analyzes, and visualizes the data to uncover climate patterns, seasonal trends, and extreme weather events.

| Detail | Value |
|---|---|
| **Data Source** | Open-Meteo Archive API (free, no API key required) |
| **Time Period** | 01/01/2023 → 31/01/2025 (~2 years) |
| **Cities** | Hanoi, Hai Phong, Da Nang, Hue, Ho Chi Minh City, Can Tho |
| **Records** | 4,000+ rows after processing |
| **Architecture** | **Backend** (Pipeline + Flask API) → **Frontend** (Streamlit) |

---

## 🏗️ Architecture: Backend / Frontend

```text
ASM/
├── backend/                          # ← BACKEND: Xử lý dữ liệu & API
│   ├── data/
│   │   ├── raw/
│   │   │   └── weather_raw.json      # Dữ liệu thô từ API
│   │   └── processed/
│   │       └── weather_cleaned.csv   # Dữ liệu đã làm sạch
│   │
│   ├── src/                          # Core Logic (OOP Classes)
│   │   ├── __init__.py
│   │   ├── weather_collector.py      # Task 1: Thu thập API
│   │   ├── data_processor.py         # Task 2: Xử lý & Feature Engineering
│   │   ├── weather_analyzer.py       # Task 3: Phân tích thống kê
│   │   └── visualizer.py             # Task 4: Tạo biểu đồ tĩnh
│   │
│   ├── outputs/
│   │   ├── charts/                   # Biểu đồ .png (Task 4)
│   │   └── reports/                  # Báo cáo .csv (Task 3)
│   │
│   ├── pipeline.py                   # Task 5: Script điều phối pipeline
│   ├── api.py                        # Flask REST API (cung cấp data cho FE)
│   └── requirements.txt
│
├── frontend/                         # ← FRONTEND: Chỉ hiển thị, gọi API
│   └── dashboard.py                  # Streamlit Dashboard (gọi Backend API)
│
├── main.py                           # Entry Point: Khởi động cả hệ thống
├── requirements.txt
└── README.md
```

### Nguyên tắc phân tách:
- **Backend** chứa **toàn bộ** logic xử lý theo yêu cầu đề bài (Task 1→5).
- **Frontend** chỉ gọi API từ Backend qua HTTP requests rồi hiển thị — **không import bất kỳ class nào** từ Backend.

---

## 📊 Key Findings

| Metric | Value |
|---|---|
| Average temperature (nationwide) | **26.0°C** |
| Peak temperature recorded | **41.5°C** |
| Lowest temperature recorded | **6.7°C** |
| Total rainfall across all cities | **28,208 mm** |

**Insights:**
- **Hanoi** has the largest temperature swing — from ~10°C in winter to ~38°C in summer
- **Ho Chi Minh City & Can Tho** are the most thermally stable (25–35°C year-round)
- **Central Vietnam** (Da Nang, Hue) peaks in rainfall during Sep–Dec due to typhoon season

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Data Collection** | `requests` — REST API calls |
| **Data Processing** | `pandas`, `numpy` |
| **Static Visualization** | `matplotlib`, `seaborn` |
| **Backend API** | `flask` |
| **Interactive Dashboard** | `streamlit`, `plotly` |

---

## 🚀 Getting Started

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run backend pipeline (collect → analyze → export)
python backend/pipeline.py

# 3. Start backend API
python backend/api.py
# → API at: http://localhost:5001

# 4. Start frontend dashboard (in another terminal)
streamlit run frontend/dashboard.py --server.port 8503
# → Dashboard at: http://localhost:8503

# OR: Run everything at once
python main.py
```

> **Note:** Data collection only runs once. If `backend/data/raw/weather_raw.json` already exists, the pipeline skips the API call automatically.

---

## 🔌 API Endpoints (Backend)

| Endpoint | Method | Description |
|---|---|---|
| `/api/cities` | GET | Danh sách thành phố & năm |
| `/api/data` | GET | Dữ liệu đã lọc (?city=...&year=...) |
| `/api/summary` | GET | KPI tổng hợp (avg, max, min, rain) |
| `/api/monthly` | GET | Trung bình nhiệt độ theo tháng |
| `/api/extremes` | GET | Các ngày thời tiết cực đoan |
| `/api/comparison` | GET | So sánh vùng miền (Bắc/Trung/Nam) |
| `/api/insights` | GET | Nhận xét & insights chính |

---

## 👤 Author

**Trinh Vu**
- GitHub: [@trinhhvu](https://github.com/trinhhvu)

---

*Built to explore real-world data science workflows with Python. 🌏*
