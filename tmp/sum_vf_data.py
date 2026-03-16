import pandas as pd

f = 'Extraction 2024-2025-traitée avec variation.xlsx'
sheet = 'extraction retraitée VF'

def sum_vf_data(file, sheet_name):
    print(f"\n--- Summing {sheet_name} ---")
    df = pd.read_excel(file, sheet_name=sheet_name, header=0) # Index 0 is header
    
    # We saw headers in index 0:
    # 'CA (KDh) 2025' and 'CA (KDh) 2024'
    
    ca_cols = [c for c in df.columns if 'CA' in str(c) and 'KDh' in str(c)]
    print(f"CA Columns found: {ca_cols}")
    
    for c in ca_cols:
        s = df[c].fillna(0).sum()
        print(f"Sum {c}: {s:,.2f} KDh")

sum_vf_data(f, sheet)
