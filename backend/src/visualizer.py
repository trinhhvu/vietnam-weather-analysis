"""
Task 4: Analysis & Visualization
Visualizer - Generates weather analysis charts for offline reporting.
"""

import os
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Use non-interactive backend for server-side plot generation
matplotlib.use("Agg")
plt.rcParams["font.family"] = "DejaVu Sans"

class Visualizer:
    """Class to manage data visualization generation."""

    def __init__(self, df: pd.DataFrame):
        """Initializes charts directory and visual palette."""
        self.df = df
        base_dir = os.path.dirname(__file__)
        self.charts_dir = os.path.join(base_dir, "..", "outputs", "charts")
        os.makedirs(self.charts_dir, exist_ok=True)

        # Set unique color palette for city identification
        cities = df["city"].unique()
        self.palette = dict(zip(cities, sns.color_palette("tab10", len(cities))))

    def _save_plot(self, filename: str):
        """Standard plot saving helper."""
        filepath = os.path.join(self.charts_dir, filename)
        plt.savefig(filepath, dpi=150)
        plt.close()
        print(f"  [OK] Saved chart: {filepath}")

    def plot_temperature_trend(self):
        """Monthly average temperature line chart for each city."""
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
                linewidth=1.8, marker="o", markersize=3, alpha=0.9
            )

        ax.set_title("Monthly Average Temperature Trends (2023-2025)", fontsize=15, fontweight="bold")
        ax.set_xlabel("Time", fontsize=12)
        ax.set_ylabel("Temp (°C)", fontsize=12)
        ax.legend(loc="upper right", fontsize=9, ncol=2)
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%m/%Y"))
        ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator(interval=3))
        fig.autofmt_xdate()
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.set_facecolor("#fcfcfc")
        plt.tight_layout()
        self._save_plot("temperature_trend.png")

    def plot_temperature_boxplot(self):
        """Box plot for cross-city temperature distribution analysis."""
        fig, ax = plt.subplots(figsize=(12, 6))

        # Order cities by median temperature
        city_order = self.df.groupby("city")["temp_mean"].median().sort_values().index.tolist()
        palette_list = [self.palette[c] for c in city_order]

        sns.boxplot(
            data=self.df, x="city", y="temp_mean", hue="city",
            order=city_order, palette=palette_list, ax=ax,
            legend=False, flierprops=dict(marker=".", markersize=3, alpha=0.4)
        )

        ax.set_title("Average Temperature Distribution by City (2023-2025)", fontsize=15, fontweight="bold")
        ax.set_xlabel("City", fontsize=12)
        ax.set_ylabel("Daily Mean Temp (°C)", fontsize=12)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.set_facecolor("#fcfcfc")
        plt.tight_layout()
        self._save_plot("temperature_boxplot.png")

    def plot_monthly_heatmap(self):
        """Heatmap of monthly average temperatures by city."""
        pivot = self.df.pivot_table(
            values="temp_mean", index="city", columns="month", aggfunc="mean"
        ).round(1)

        month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        fig, ax = plt.subplots(figsize=(14, 6))
        sns.heatmap(
            pivot, annot=True, fmt=".1f", cmap="RdYlBu_r",
            linewidths=0.5, linecolor="white", ax=ax,
            cbar_kws={"label": "Temp (°C)"}
        )
        ax.set_xticklabels(month_labels, rotation=0)
        ax.set_title("Mean Temperature Heatmap: City vs Month (°C)", fontsize=15, fontweight="bold")
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("City", fontsize=12)
        plt.tight_layout()
        self._save_plot("monthly_heatmap.png")

    def generate_all(self):
        """Batch generates all default charts."""
        self.plot_temperature_trend()
        self.plot_temperature_boxplot()
        self.plot_monthly_heatmap()
