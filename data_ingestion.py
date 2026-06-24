import pandas as pd
import os

CSV_DIR = "data/raw"
anomalies = []

csv_files = sorted([f for f in os.listdir(CSV_DIR) if f.endswith(".csv")])
dataframes = {}

for file in csv_files:
    path = os.path.join(CSV_DIR, file)
    print(f"\n{'='*60}")
    print(f"FILE: {file}")
    print(f"{'='*60}")

    df = pd.read_csv(path)
    dataframes[file] = df

    print(f"Shape  : {df.shape}")
    print(f"\nDtypes :\n{df.dtypes}")
    print(f"\nHead   :\n{df.head()}")

    # Anomaly Check 1 — High nulls
    null_vals = df.isnull().mean() * 100
    high_null = null_vals[null_vals > 20]
    if not high_null.empty:
        note = f"{file}: High nulls in {list(high_null.index)}"
        anomalies.append(note)
        print(f"\n ANOMALY: {note}")

    # Anomaly Check 2 — Duplicates
    dups = df.duplicated().sum()
    if dups > 0:
        note = f"{file}: {dups} duplicate rows"
        anomalies.append(note)
        print(f"⚠ ANOMALY: {note}")

print("\n\n=== ANOMALY SUMMARY ===")
for a in anomalies:
    print(" -", a)
if not anomalies:
    print("No major anomalies detected.")

