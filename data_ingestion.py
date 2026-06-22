import pandas as pd 
import os 
import numpy as np
CSV_DIR="data/raw"
anomalies=[]
csv_files = [f for f in os.listdir(CSV_DIR) if f.endswith(".csv")]
#dictionary for storing the dataframe associated with each filename 
dataframes = {}

for file in csv_files:
    path=os.path.join(CSV_DIR,file)
    print('---------------------')
    print(f"File_name :{file}")
    print('---------------------')

    df=pd.read_csv(path)
    dataframes[file]=df
    print("\n")
    print(f"Shape :{df.shape}\n")
    print(f"Dtypes :\n{df.dtypes}\n")
    print(f"Head :\n{df.head()}\n")

    #checking for any anomalies , setting thresold null percentage as 20%
    null_vals=df.isnull().mean()*100
    high_null=null_vals[null_vals>20]
    if not high_null.empty:
        note=f"{file} : High null values found in {list(high_null.index)}"
        anomalies.append(note)
        print(f"Anomaly Found :\n{note}\n")
    
    #checking for duplicates now 
    dups=df.duplicated().sum()
    if dups>0:
        note=f"{file} : {dups} duplicate rows found!!"
        anomalies.append(note)
        print("Anomaly Found : \n{note}\n")

print("\n\n ---ANOMALY SUMMARY ---")
for a in anomalies:
    print(" -", a)
if not anomalies:
    print("No major anomalies detected :)")



#exploring the fundmaster 

df = pd.read_csv("data/raw/fund_master.csv")

print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(f"\nSample:\n{df.head()}")
print(f"\nTotal schemes: {len(df)}")
print(f"Unique ISIN Growth codes: {df['isinGrowth'].nunique()}")

missing_isin = df[df['isinGrowth'].isna()]
print(f"Schemes with no ISIN: {len(missing_isin)}")


