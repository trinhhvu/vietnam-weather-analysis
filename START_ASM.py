"""
One-click Launcher for Vietnam Weather Analysis System.
Starts the Backend Pipeline (if needed), Backend API, and Frontend Dashboard.
"""

import subprocess
import os
import sys
import time
import io

# Setup for Windows console Unicode output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Project Root Directories
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

# Ensure fixed Windows PATH for Python/Node (Common environment)
PYTHON_PATH = r"C:\Program Files\Python312"
NODE_PATH = r"C:\Program Files\nodejs"
os.environ["PATH"] = f"{PYTHON_PATH};{PYTHON_PATH}\\Scripts;{NODE_PATH};" + os.environ["PATH"]

def start_process(cwd, command, name):
    """Starts a subprocess and returns the handle."""
    if not os.path.exists(cwd):
        print(f"[ERROR] {name}: Directory not found: {cwd}")
        return None
    print(f"[STARTING] {name}...")
    return subprocess.Popen(command, cwd=cwd, shell=True)

def main():
    print("=" * 60)
    print("      VIETNAM WEATHER ANALYSIS - SYSTEM LAUNCHER")
    print("=" * 60)

    # 1. Run Data Pipeline if cleaned data is missing
    processed_csv = os.path.join(BACKEND_DIR, "data", "processed", "weather_cleaned.csv")
    if not os.path.exists(processed_csv):
        print("\n[PIPELINE] Processed data not found. Running initial pipeline...")
        subprocess.run([sys.executable, "pipeline.py"], cwd=BACKEND_DIR)

    # 2. Start Backend API (Flask: Port 5001)
    api = start_process(BACKEND_DIR, f'"{sys.executable}" api.py', "Backend API (Flask:5001)")
    time.sleep(3) # Wait for API initialization

    # 3. Start Frontend Dashboard (Streamlit: Port 8503)
    frontend = start_process(
        FRONTEND_DIR,
        f'"{sys.executable}" -m streamlit run dashboard.py --server.port 8503',
        "Frontend Dashboard (Streamlit:8503)"
    )

    print("\n[SUCCESS] System is booting up...")
    time.sleep(2)

    print("\n--- Access URLs ---")
    print("Dashboard:  http://localhost:8503")
    print("API Stats:  http://localhost:5001/api/summary")
    print("\nPress Ctrl + C to stop all services.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[STOPPING] Shutting down services...")
        if api: api.terminate()
        if frontend: frontend.terminate()
        print("[DONE] Cleanup complete.")

if __name__ == "__main__":
    main()
