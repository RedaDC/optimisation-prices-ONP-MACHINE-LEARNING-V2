import pandas as pd

f = 'New Report(2024-2025) -DR (3).xlsx'
try:
    df = pd.read_excel(f, sheet_name='Feuil2', header=None)
    print(f"--- Sheet: Feuil2 of {f} ---")
    
    # Search for MG CASABLANCA
    mask = df.apply(lambda row: row.astype(str).str.contains('MG CASABLANCA', case=False).any(), axis=1)
    mg_rows = df[mask]
    
    if not mg_rows.empty:
        print("MG CASABLANCA rows in Feuil2:")
        print(mg_rows.to_string())
    else:
        print("MG CASABLANCA NOT found in Feuil2.")
    
    # Let's also check the headers at index 2 (as identified by trace)
    print("\nHeaders at index 2:")
    print(df.iloc[2].tolist())

except Exception as e:
    print(f"Error: {e}")
