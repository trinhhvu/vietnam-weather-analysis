"""
Task 4: Analysis & Visualization
Visualizer - Tạo các biểu đồ trực quan hóa dữ liệu thời tiết.
"""

import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

# Use non-interactive backend
matplotlib.use("Agg")
plt.rcParams["font.family"] = "DejaVu Sans"


class Visualizer:
    """Tạo các biểu đồ phân tích thời tiết."""

    def __init__(self, df: pd.DataFrame):
        """
        Initialize Visualizer.

        Args:
            df: DataFrame đã được xử lý từ DataProcessor.
        """
        self.df = df
        base_dir = os.path.dirname(__file__)
        self.charts_dir = os.path.join(base_dir, "..", "outputs", "charts")
        os.makedirs(self.charts_dir, exist_ok=True)

        # Color palette for cities
        cities = df["city"].unique()
        self.palette = dict(zip(cities, sns.color_palette("tab10", len(cities))))

    # ------------------------------------------------------------------ #
    # Chart 1: Line Chart - Xu hướng nhiệt độ theo thời gian              #
    # ------------------------------------------------------------------ #
    def plot_temperature_trend(self):
        """
        Biểu đồ 1: Line Chart - Nhiệt độ trung bình hàng tháng theo thành phố.
        """
        monthly = (
            self.df.groupby(["city", "year", "month"])["temp_mean"]
            .mean()
            .reset_index()
        )
        monthly["date"] = pd.to_datetime(
            monthly[["year", "month"]].assign(day=1)
        )

        fig, ax = plt.subplots(figsize=(14, 6))
        for city, grp in monthly.groupby("city"):
            ax.plot(
                grp["date"], grp["temp_mean"],
                label=city, color=self.palette[city],
                linewidth=1.8, marker="o", markersize=2.5
            )

        ax.set_title("Xu Hướng Nhiệt Độ Trung Bình Tháng (2023-2025)", fontsize=15, fontweight="bold")
        ax.set_xlabel("Thời gian", fontsize=12)
        ax.set_ylabel("Nhiệt độ (°C)", fontsize=12)
        ax.legend(loc="upper right", fontsize=9, ncol=2)
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%m/%Y"))
        ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=3))
        fig.autofmt_xdate()
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.set_facecolor("#f9f9f9")
        plt.tight_layout()

        filepath = os.path.join(self.charts_dir, "temperature_trend.png")
        plt.savefig(filepath, dpi=150)
        plt.close()
        print(f"  [OK] Biểu đồ 1 đã lưu: {filepath}")

    # ------------------------------------------------------------------ #
    # Chart 2: Box Plot - Phân bố nhiệt độ theo thành phố                 #
    # ------------------------------------------------------------------ #
    def plot_temperature_boxplot(self):
        """
        Biểu đồ 2: Box Plot - So sánh phân bố nhiệt độ giữa các thành phố.
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        city_order = (
            self.df.groupby("city")["temp_mean"].median()
            .sort_values()
            .index.tolist()
        )
        palette_list = [self.palette[c] for c in city_order]

        sns.boxplot(
            data=self.df, x="city", y="temp_mean", hue="city",
            order=city_order, palette=palette_list, ax=ax,
            legend=False,
            flierprops=dict(marker="o", markersize=2, alpha=0.5)
        )

        ax.set_title("Phân Bố Nhiệt Độ Trung Bình theo Thành Phố (2023-2025)", fontsize=15, fontweight="bold")
        ax.set_xlabel("Thành phố", fontsize=12)
        ax.set_ylabel("Nhiệt độ TB ngày (°C)", fontsize=12)
        ax.tick_params(axis="x", labelrotation=15)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.set_facecolor("#f9f9f9")
        plt.tight_layout()

        filepath = os.path.join(self.charts_dir, "temperature_boxplot.png")
        plt.savefig(filepath, dpi=150)
        plt.close()
        print(f"  [OK] Biểu đồ 2 đã lưu: {filepath}")

    # ------------------------------------------------------------------ #
    # Chart 3: Heatmap - Nhiệt độ TB theo tháng và thành phố              #
    # ------------------------------------------------------------------ #
    def plot_monthly_heatmap(self):
        """
        Biểu đồ 3: Heatmap - Nhiệt độ trung bình theo tháng và thành phố.
        """
        pivot = self.df.pivot_table(
            values="temp_mean", index="city", columns="month", aggfunc="mean"
        ).round(1)

        month_labels = ["T1","T2","T3","T4","T5","T6","T7","T8","T9","T10","T11","T12"]

        fig, ax = plt.subplots(figsize=(14, 6))
        sns.heatmap(
            pivot, annot=True, fmt=".1f", cmap="YlOrRd",
            linewidths=0.5, linecolor="white",
            ax=ax, cbar_kws={"label": "Nhiệt độ (°C)"}
        )
        ax.set_xticklabels(month_labels, rotation=0)
        ax.set_title("Nhiệt Độ Trung Bình Theo Tháng và Thành Phố (°C)", fontsize=15, fontweight="bold")
        ax.set_xlabel("Tháng", fontsize=12)
        ax.set_ylabel("Thành phố", fontsize=12)
        plt.tight_layout()

        filepath = os.path.join(self.charts_dir, "monthly_heatmap.png")
        plt.savefig(filepath, dpi=150)
        plt.close()
        print(f"  [OK] Biểu đồ 3 đã lưu: {filepath}")

    def generate_all(self):
        """Tạo tất cả 3 biểu đồ."""
        print("\n=== TASK 4: VISUALIZATION ===")
        self.plot_temperature_trend()
        self.plot_temperature_boxplot()
        self.plot_monthly_heatmap()
