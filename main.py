"""
main.py - Entry Point cho toàn bộ hệ thống Weather Analysis.

Chạy file này để:
  1. Chạy Backend Pipeline (Collect → Clean → Analyze → Visualize)
  2. Khởi động Backend API (Flask, port 5001)
  3. Khởi động Frontend Dashboard (Streamlit, port 8503)

Usage:
    python main.py
"""

import subprocess
import os
import sys
import time
import io

# Fix for Unicode output in Windows terminal
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

# PATH setup for Windows
PYTHON_PATH = r"C:\Program Files\Python312"
NODE_PATH = r"C:\Program Files\nodejs"
os.environ["PATH"] = f"{PYTHON_PATH};{PYTHON_PATH}\\Scripts;{NODE_PATH};" + os.environ["PATH"]


def start_process(cwd, command, name):
    """Khởi động một subprocess."""
    if not os.path.exists(cwd):
        print(f"[SKIPPING] {name}: Thư mục không tồn tại: {cwd}")
        return None
    print(f"[STARTING] {name} at {cwd}...")
    return subprocess.Popen(command, cwd=cwd, shell=True)


def main():
    print("=" * 60)
    print("      WEATHER ANALYSIS - BACKEND / FRONTEND LAUNCHER")
    print("=" * 60)

    # 1. Chạy Pipeline nếu chưa có dữ liệu
    processed_csv = os.path.join(BACKEND_DIR, "data", "processed", "weather_cleaned.csv")
    if not os.path.exists(processed_csv):
        print("\n[PIPELINE] Chạy pipeline lần đầu...")
        subprocess.run([sys.executable, "pipeline.py"], cwd=BACKEND_DIR)

    # 2. Start Backend API (Flask)
    api = start_process(BACKEND_DIR, f"{sys.executable} api.py", "Backend API (Flask:5001)")

    time.sleep(3)  # Đợi API sẵn sàng

    # 3. Start Frontend Dashboard (Streamlit)
    frontend = start_process(
        FRONTEND_DIR,
        f"streamlit run dashboard.py --server.port 8503",
        "Frontend Dashboard (Streamlit:8503)"
    )

    print("\n[OK] Hệ thống đang khởi động...")
    time.sleep(3)

    print("\n--- Danh mục truy cập ---")
    print("Dashboard:  http://localhost:8503")
    print("API:        http://localhost:5001/api/summary")
    print("\nNhấn Ctrl + C để dừng toàn bộ.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[STOPPING] Đang tắt hệ thống...")
        if api: api.terminate()
        if frontend: frontend.terminate()
        print("[DONE] Đã tắt sạch.")


if __name__ == "__main__":
    main()
