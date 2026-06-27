"""
transform.py
------------
Step 2 of the pipeline: takes the Excel-cleaned project data and adds a
ProjectMonth column (used later for the Power BI monthly trend chart).

Usage:
    python scripts/transform.py
    python scripts/transform.py --input data/raw/custom.csv --output data/processed/custom_clean.csv

By default it reads/writes relative to the repo root, so it runs the same
way on any machine.
"""

import argparse
from pathlib import Path

import pandas as pd

# Repo root = one level up from this script (scripts/transform.py -> repo/)
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = REPO_ROOT / "excel" / "smart_home_projects_with_calculations.csv"
DEFAULT_OUTPUT = REPO_ROOT / "data" / "processed" / "projects_clean.csv"


def transform(input_path: Path, output_path: Path) -> pd.DataFrame:
    df = pd.read_csv(input_path)

    # Parse dates (already cleaned to ISO format in Excel step)
    df["StartDate"] = pd.to_datetime(df["StartDate"], errors="coerce")
    df["EndDate"] = pd.to_datetime(df["EndDate"], errors="coerce")

    # Surface any rows that failed to parse instead of silently dropping them
    bad_dates = df["StartDate"].isna().sum() + df["EndDate"].isna().sum()
    if bad_dates:
        print(f"Warning: {bad_dates} date values could not be parsed.")

    # Derive Year-Month for monthly aggregation in the dashboard
    df["ProjectMonth"] = df["StartDate"].dt.to_period("M").astype(str)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean and enrich smart home project data.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to input CSV")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Path to output CSV")
    args = parser.parse_args()

    result = transform(args.input, args.output)
    print(f"Done. {len(result)} rows saved to {args.output}")
