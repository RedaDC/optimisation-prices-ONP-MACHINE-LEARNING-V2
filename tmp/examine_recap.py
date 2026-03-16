import pandas as pd

f = "Extraction 2024-2025-traitée avec variation.xlsx"
sheet = "RECAP"

try:
    df = pd.read_excel(f, sheet_name=sheet)
    print(f"Data for MG CASABLANCA in {f} [{sheet}]:")
    mask = df.apply(lambda x: x.astype(str).str.contains('MG CASABLANCA', case=False, na=False)).any(axis=1)
    results = df[mask]
    print(results)
    
    # Also look for the value 467283 in the whole sheet
    mask_val = df.apply(lambda x: x.astype(str).str.contains('467283', na=False)).any(axis=1)
    if mask_val.any():
        print("\nFOUND 467283 in this sheet:")
        print(df[mask_val])

except Exception as e:
    print(f"Error: {e}")
