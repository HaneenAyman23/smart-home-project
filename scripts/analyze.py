"""
analyze.py
----------
Step 3 (optional, ahead of Power BI): runs exploratory analysis on the
cleaned project data and exports summary stats + chart images that get
embedded in the README / used as a sanity check before building the
Power BI dashboard.

Usage:
    python scripts/analyze.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "data" / "processed" / "projects_clean.csv"
ASSETS_DIR = REPO_ROOT / "assets"

TEAL = "#0F766E"
AMBER = "#D97706"
PALETTE = [TEAL, AMBER, "#64748B"]

plt.rcParams.update({
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#334155",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["StartDate"] = pd.to_datetime(df["StartDate"])
    df["EndDate"] = pd.to_datetime(df["EndDate"])
    return df


def print_summary(df: pd.DataFrame) -> None:
    total_revenue = df["RevenueAfterDiscount"].sum()
    total_cost = df["ProjectCost"].sum()
    avg_discount = df["Discount"].mean()
    avg_duration = df["ProjectDuration"].mean()
    total_devices = df["DevicesInstalled"].sum()

    print("=== Smart Home Projects — Summary ===")
    print(f"Total projects:            {len(df)}")
    print(f"Total revenue (after disc.): ${total_revenue:,.2f}")
    print(f"Total listed project cost: ${total_cost:,.2f}")
    print(f"Average discount applied:  {avg_discount:.1%}")
    print(f"Average project duration:  {avg_duration:.1f} days")
    print(f"Total devices installed:   {total_devices}")
    print()
    print("By region:")
    print(df.groupby("Region")["RevenueAfterDiscount"].agg(["count", "sum", "mean"]).round(2))
    print()
    print("By project type:")
    print(df.groupby("ProjectType")["RevenueAfterDiscount"].agg(["count", "sum", "mean"]).round(2))


def chart_revenue_by_region(df: pd.DataFrame) -> None:
    summary = df.groupby("Region")["RevenueAfterDiscount"].sum().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.barh(summary.index, summary.values, color=TEAL)
    for i, v in enumerate(summary.values):
        ax.text(v + 3000, i, f"${v:,.0f}", va="center", fontsize=10, color="#334155")
    ax.set_title("Revenue After Discount by Region", fontsize=13, weight="bold", loc="left")
    ax.set_xlabel("Revenue ($)")
    ax.set_xlim(0, summary.values.max() * 1.25)
    fig.tight_layout()
    fig.savefig(ASSETS_DIR / "revenue_by_region.png", dpi=200)
    plt.close(fig)


def chart_monthly_trend(df: pd.DataFrame) -> None:
    summary = df.groupby("ProjectMonth")["RevenueAfterDiscount"].sum()
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.plot(summary.index, summary.values, marker="o", color=AMBER, linewidth=2.5)
    ax.fill_between(range(len(summary)), summary.values, color=AMBER, alpha=0.12)
    for i, v in enumerate(summary.values):
        ax.text(i, v + 8000, f"${v:,.0f}", ha="center", fontsize=9, color="#334155")
    ax.set_title("Monthly Revenue Trend", fontsize=13, weight="bold", loc="left")
    ax.set_ylabel("Revenue ($)")
    ax.set_ylim(0, summary.values.max() * 1.3)
    fig.tight_layout()
    fig.savefig(ASSETS_DIR / "monthly_revenue_trend.png", dpi=200)
    plt.close(fig)


def chart_project_type_split(df: pd.DataFrame) -> None:
    summary = df.groupby("ProjectType")["RevenueAfterDiscount"].agg(["count", "sum"])
    fig, ax = plt.subplots(figsize=(6, 3.5))
    bars = ax.bar(summary.index, summary["sum"], color=[TEAL, AMBER])
    for bar, count in zip(bars, summary["count"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 5000,
            f"{count} projects",
            ha="center",
            fontsize=10,
            color="#334155",
        )
    ax.set_title("Revenue by Project Type", fontsize=13, weight="bold", loc="left")
    ax.set_ylabel("Revenue ($)")
    ax.set_ylim(0, summary["sum"].max() * 1.3)
    fig.tight_layout()
    fig.savefig(ASSETS_DIR / "project_type_split.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    data = load_data()
    print_summary(data)
    chart_revenue_by_region(data)
    chart_monthly_trend(data)
    chart_project_type_split(data)
    print(f"\nCharts saved to {ASSETS_DIR}/")
