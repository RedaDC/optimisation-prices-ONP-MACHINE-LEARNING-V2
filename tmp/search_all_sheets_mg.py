import pandas as pd

f = "Extraction 2024-2025-traitée avec variation.xlsx"
xl = pd.ExcelFile(f)
print(f"Sheets in {f}: {xl.sheet_names}")

for sheet in xl.sheet_names:
    try:
        df = pd.read_excel(f, sheet_name=sheet, header=None)
        mask = df.apply(lambda r: r.astype(str).str.contains('MG CASABLANCA', case=False).any(), axis=1)
        matches = df[mask]
        if not matches.empty:
            print(f"\n--- {sheet} ---")
            print(matches.to_string())
    except Exception as e:
        print(f"Error reading sheet {sheet}: {e}")
