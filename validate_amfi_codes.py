
import pandas as pd

fund_master = pd.read_csv("data/raw/fund_master.csv")
nav_history  = pd.read_csv("data/raw/nav_history.csv")   # adjust filename

master_codes = set(fund_master["schemeCode"].astype(str))
nav_codes    = set(nav_history["scheme_code"].astype(str))

missing_in_nav   = master_codes - nav_codes
extra_in_nav     = nav_codes - master_codes
matched          = master_codes & nav_codes

print("=== DATA QUALITY SUMMARY ===")
print(f"Fund Master records  : {len(fund_master)}")
print(f"NAV History records  : {len(nav_history)}")
print(f"Codes matched        : {len(matched)}")
print(f"In master, NOT in NAV: {len(missing_in_nav)}")
print(f"In NAV, NOT in master: {len(extra_in_nav)}")

if missing_in_nav:
    print(f"\nMissing in NAV (sample): {list(missing_in_nav)[:10]}")
if extra_in_nav:
    print(f"\nExtra in NAV (sample)  : {list(extra_in_nav)[:10]}")

# Save report
with open("reports/data_quality_day1.txt", "w") as f:
    f.write(f"Data Quality Report — Day 1\n{'-'*40}\n")
    f.write(f"Fund Master records  : {len(fund_master)}\n")
    f.write(f"NAV History records  : {len(nav_history)}\n")
    f.write(f"Codes matched        : {len(matched)}\n")
    f.write(f"Missing in NAV       : {len(missing_in_nav)}\n")
    f.write(f"Extra in NAV         : {len(extra_in_nav)}\n")

print("\nReport saved to reports/data_quality_day1.txt")