import pandas as pd

f = 'New Report(2024-2025) -DR (3).xlsx'
try:
    # Read the sheet where the user's value was found in my initial mega-search
    sheet = 'Variation 1ère Vente'
    df = pd.read_excel(f, sheet_name=sheet, header=None)
    print(f"--- Sheet: {sheet} of {f} ---")
    
    # Search for MG CASABLANCA
    mask = df.apply(lambda row: row.astype(str).str.contains('MG CASABLANCA', case=False).any(), axis=1)
    mg_rows = df[mask]
    
    print(f"MG CASABLANCA rows in {sheet}:")
    print(mg_rows.to_string())
    
    # Let's see some context around it
    if not mg_rows.empty:
        idx = mg_rows.index[0]
        print("\nRows around the match:")
        print(df.iloc[idx-5:idx+15].to_string())

except Exception as e:
    print(f"Error: {e}")
