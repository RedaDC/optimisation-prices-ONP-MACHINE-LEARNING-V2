import pandas as pd
import re

f = 'Extraction 2024-2025-traitée avec variation.xlsx'
df = pd.read_excel(f, sheet_name='extraction retraitée VF')

col_port = 1
col_species = 4
col_vol = 6 # Vol 2024
col_ca = 9  # CA 2024

print(f"Checking first 50 rows of {f}...")

found = 0
skipped = 0
for idx in range(len(df)):
    p = str(df.iloc[idx, col_port]).strip()
    s = str(df.iloc[idx, col_species]).strip()
    v_raw = df.iloc[idx, col_vol]
    c_raw = df.iloc[idx, col_ca]
    
    # Logic from data_loader.py
    is_skipped = False
    if not p or p.lower() == 'nan' or 'total' in p.lower(): is_skipped = True
    elif not s or s.lower() == 'nan' or 'total' in s.lower():
        if not ("MG " in p.upper()):
            is_skipped = True
            
    if is_skipped:
        skipped += 1
        if pd.notna(c_raw) and float(str(c_raw).replace(' ','').replace(',','.')) > 1000:
            print(f"SKIPPED Row {idx+2}: Port='{p}', Spec='{s}', CA={c_raw}")
    else:
        found += 1
        if "CAPI DAKHLA" in p.upper():
             print(f"ACCEPTED CAPI DAKHLA Row {idx+2}: Spec='{s}', CA={c_raw}")

print(f"\nSummary: Found {found}, Skipped {skipped}")
