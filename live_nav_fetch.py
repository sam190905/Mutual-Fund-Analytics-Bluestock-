import requests
import pandas as pd
import numpy as np 
from datetime import datetime
import glob
#base url for the api as mentioned in the task 
BASE_URL = "https://api.mfapi.in/mf"





def fetch_nav(scheme_code, scheme_name):
    url = f"{BASE_URL}/{scheme_code}"
    print(f"\nFetching: {scheme_name} (code: {scheme_code})")
    response = requests.get(url, timeout=20)
    response.raise_for_status()

    data = response.json()
    meta = data["meta"]
    nav_records = data["data"]  

    df = pd.DataFrame(nav_records)
    df["scheme_code"]  = scheme_code
    df["scheme_name"]  = meta.get("scheme_name", scheme_name)
    df["fund_house"]   = meta.get("fund_house", "")
    df["scheme_type"]  = meta.get("scheme_type", "")
    df["scheme_category"] = meta.get("scheme_category", "")

    #saving the fetched data into csv files 
    filename = f"data/raw/nav_{scheme_code}.csv"
    df.to_csv(filename, index=False)
    print(f"   Saved {len(df)} records = {filename}")
    print(f"  Latest NAV: ₹{df.iloc[0]['nav']} on {df.iloc[0]['date']}")
    return df


#fetching the fundmaster data 
def fetch_fund_master() -> pd.DataFrame:
    url = "https://api.mfapi.in/mf"
    print("\nFetching Fund Master...")

    response = requests.get(url, timeout=(10, 20))
    data = response.json()

    df = pd.DataFrame(data)
    df.to_csv("data/raw/fund_master.csv", index=False)
    print(f"  ✓ Saved {len(df)} schemes → data/raw/fund_master.csv")
    return df

fund_master_df = fetch_fund_master()

hdfc_df = fetch_nav(125497, "HDFC Top 100 Direct")


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

master_nav = pd.concat(all_nav, ignore_index=True)
master_nav.to_csv("data/processed/all_nav_master.csv", index=False)
print(f"\nMaster NAV file saved: {master_nav.shape}")



#creating the navhistory
all_files = glob.glob("data/raw/nav_*.csv")
nav_history = pd.concat([pd.read_csv(f) for f in all_files], ignore_index=True)
nav_history.to_csv("data/raw/nav_history.csv", index=False)
print(f" nav_history.csv saved → {nav_history.shape}")