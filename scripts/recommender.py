"""
recommender.py
Bluestock Fintech — Mutual Fund Analytics Capstone | Day 6

Simple fund recommender: input risk appetite → top 3 funds by Sharpe ratio
within matching risk_grade from scheme_performance.csv
"""

import pandas as pd
import sys
from paths import RAW_DIR

# ── Risk appetite → risk_grade mapping ────────────────────────
RISK_MAP = {
    "low":      ["Low"],
    "moderate": ["Moderate", "Moderately High"],
    "high":     ["High", "Very High"],
}

def recommend(risk_appetite: str, top_n: int = 3) -> pd.DataFrame:
    """
    Returns top N funds by Sharpe ratio for a given risk appetite.

    Parameters
    ----------
    risk_appetite : str
        One of: 'Low', 'Moderate', 'High' (case-insensitive)
    top_n : int
        Number of funds to return (default 3)

    Returns
    -------
    pd.DataFrame with columns: scheme_name, fund_house, risk_grade,
                                sharpe_ratio, return_3yr_pct, expense_ratio_pct
    """
    key = risk_appetite.strip().lower()
    if key not in RISK_MAP:
        raise ValueError(f"Invalid risk appetite '{risk_appetite}'. "
                         f"Choose from: Low, Moderate, High")

    perf = pd.read_csv(RAW_DIR / "07_scheme_performance.csv")
    valid_grades = RISK_MAP[key]

    filtered = perf[perf["risk_grade"].isin(valid_grades)].copy()
    filtered = filtered.sort_values("sharpe_ratio", ascending=False)
    filtered = filtered.head(top_n)

    result = filtered[[
        "scheme_name", "fund_house", "risk_grade",
        "sharpe_ratio", "return_3yr_pct", "expense_ratio_pct",
        "morningstar_rating"
    ]].reset_index(drop=True)
    result.index += 1  # rank from 1

    return result


def print_recommendation(risk_appetite: str):
    print(f"\n{'='*65}")
    print(f"  FUND RECOMMENDATION — Risk Appetite: {risk_appetite.upper()}")
    print(f"{'='*65}")

    rec = recommend(risk_appetite)
    for rank, row in rec.iterrows():
        print(f"\n  #{rank}  {row['scheme_name']}")
        print(f"      Fund House     : {row['fund_house']}")
        print(f"      Risk Grade     : {row['risk_grade']}")
        print(f"      Sharpe Ratio   : {row['sharpe_ratio']:.2f}")
        print(f"      3-yr CAGR      : {row['return_3yr_pct']:.2f}%")
        print(f"      Expense Ratio  : {row['expense_ratio_pct']:.2f}%")
        print(f"      ★ Rating       : {'★' * int(row['morningstar_rating'])}")
    print()


# ── CLI entry point ───────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) > 1:
        appetite = sys.argv[1]
    else:
        print("Usage: python recommender.py <Low|Moderate|High>")
        print("\nRunning all three as demo...\n")
        for level in ["Low", "Moderate", "High"]:
            print_recommendation(level)
        sys.exit(0)

    print_recommendation(appetite)
