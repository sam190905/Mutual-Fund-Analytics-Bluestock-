import requests
import pandas as pd
from paths import PROCESSED_DIR, RAW_DIR

BASE_URL = "https://api.mfapi.in/mf"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def fetch_nav(scheme_code, scheme_name):
    url = f"{BASE_URL}/{scheme_code}"
    print(f"\nFetching: {scheme_name} (code: {scheme_code})")

    response = requests.get(url, timeout=(10, 20))
    response.raise_for_status()

    data = response.json()
    meta = data["meta"]
    nav_records = data["data"]

    df = pd.DataFrame(nav_records)
    df["amfi_code"]       = scheme_code
    df["scheme_name"]     = meta.get("scheme_name", scheme_name)
    df["fund_house"]      = meta.get("fund_house", "")
    df["scheme_type"]     = meta.get("scheme_type", "")
    df["scheme_category"] = meta.get("scheme_category", "")

    filename = RAW_DIR / f"nav_{scheme_code}.csv"
    df.to_csv(filename, index=False)
    print(f"  ✓ Saved {len(df)} records → data/raw/{filename.name}")
    print(f"  Latest NAV: ₹{df.iloc[0]['nav']} on {df.iloc[0]['date']}")
    return df


# Step 4 — HDFC Top 100
hdfc_df = fetch_nav(125497, "HDFC Top 100 Direct")

# Step 5 — 5 key schemes
SCHEMES = [
    (119551, "SBI Bluechip Direct"),
    (120503, "ICICI Prudential Bluechip Direct"),
    (118632, "Nippon India Large Cap Direct"),
    (119092, "Axis Bluechip Direct"),
    (120841, "Kotak Bluechip Direct"),
]

all_nav = [hdfc_df]
for code, name in SCHEMES:
    df = fetch_nav(code, name)
    all_nav.append(df)

# Combine all fetched NAVs into master
master_nav = pd.concat(all_nav, ignore_index=True)
master_nav.to_csv(PROCESSED_DIR / "all_nav_master.csv", index=False)
print(f"\n✓ all_nav_master.csv saved → {master_nav.shape}")
