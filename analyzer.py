"""
Capital Cost Variance Analyzer
--------------------------------
Takes planned vs. actual cost data for a capital project (broken down by
work package and cost category) and produces:

  1. A variance report ($ and %) per line item, sorted by absolute impact
  2. A roll-up by cost category (Labour / Materials / Contracts)
  3. A simple sensitivity check: how much would a +/-5% swing in each
     category shift total project cost
  4. A bar chart visualizing variance by work package

Run:
    python analyzer.py sample_data.csv

Input CSV columns:
    work_package, category, planned_cost, actual_cost
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"work_package", "category", "planned_cost", "actual_cost"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Input file is missing required columns: {missing}")
    return df


def compute_variance(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["variance_dollars"] = df["actual_cost"] - df["planned_cost"]
    df["variance_pct"] = (df["variance_dollars"] / df["planned_cost"] * 100).round(2)
    df["status"] = df["variance_dollars"].apply(
        lambda v: "Over Budget" if v > 0 else ("Under Budget" if v < 0 else "On Budget")
    )
    return df.sort_values("variance_dollars", key=abs, ascending=False)


def category_rollup(df: pd.DataFrame) -> pd.DataFrame:
    rollup = df.groupby("category")[["planned_cost", "actual_cost"]].sum()
    rollup["variance_dollars"] = rollup["actual_cost"] - rollup["planned_cost"]
    rollup["variance_pct"] = (rollup["variance_dollars"] / rollup["planned_cost"] * 100).round(2)
    return rollup.sort_values("variance_dollars", key=abs, ascending=False)


def sensitivity_check(rollup: pd.DataFrame, swing_pct: float = 5.0) -> pd.DataFrame:
    """
    For each cost category, show the total-project dollar impact of a
    +/- swing_pct change applied to that category's actual cost, holding
    everything else constant. This is a simple one-factor-at-a-time
    sensitivity view, the same kind of tornado-chart input used in
    capital planning to see which cost drivers matter most.
    """
    total_actual = rollup["actual_cost"].sum()
    impact = pd.DataFrame({
        "category": rollup.index,
        "actual_cost": rollup["actual_cost"].values,
        f"impact_of_+{swing_pct:.0f}%": rollup["actual_cost"].values * (swing_pct / 100),
        f"impact_of_-{swing_pct:.0f}%": -rollup["actual_cost"].values * (swing_pct / 100),
    }).set_index("category")
    impact["share_of_total_cost_pct"] = (impact["actual_cost"] / total_actual * 100).round(1)
    return impact.sort_values("actual_cost", ascending=False)


def plot_variance(df: pd.DataFrame, out_path: str = "variance_chart.png"):
    fig, ax = plt.subplots(figsize=(9, 5.5))
    colors = ["#B00020" if v > 0 else "#1B7A43" for v in df["variance_dollars"]]
    ax.barh(df["work_package"] + " (" + df["category"] + ")", df["variance_dollars"], color=colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Variance ($) — Actual minus Planned")
    ax.set_title("Cost Variance by Work Package")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    print(f"\nChart saved to {out_path}")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "sample_data.csv"
    df = load_data(path)

    variance = compute_variance(df)
    rollup = category_rollup(df)
    sensitivity = sensitivity_check(rollup)

    total_planned = df["planned_cost"].sum()
    total_actual = df["actual_cost"].sum()
    total_variance = total_actual - total_planned
    total_variance_pct = total_variance / total_planned * 100

    pd.set_option("display.float_format", lambda x: f"{x:,.2f}")

    print("=" * 70)
    print("CAPITAL COST VARIANCE REPORT")
    print("=" * 70)
    print(f"\nTotal Planned Cost: ${total_planned:,.0f}")
    print(f"Total Actual Cost:  ${total_actual:,.0f}")
    print(f"Total Variance:     ${total_variance:,.0f}  ({total_variance_pct:+.1f}%)")

    print("\n--- Top Variance Line Items ---")
    print(variance[["work_package", "category", "planned_cost", "actual_cost",
                     "variance_dollars", "variance_pct", "status"]].to_string(index=False))

    print("\n--- Roll-Up by Cost Category ---")
    print(rollup.to_string())

    print("\n--- Sensitivity: +/-5% Swing Impact by Category ---")
    print(sensitivity.to_string())

    variance.to_csv("variance_report.csv", index=False)
    print("\nFull line-item report saved to variance_report.csv")

    plot_variance(variance)


if __name__ == "__main__":
    main()
