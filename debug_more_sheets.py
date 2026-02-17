import pandas as pd

file = 'Extraction 2024-2025-traitée avec variation.xlsx'
for s in ['Feuil2', 'Feuil4', 'Feuil5']:
    try:
        df = pd.read_excel(file, sheet_name=s, nrows=10)
        print(f"\n--- SHEET: {s} ---")
        print(f"Columns: {df.columns.tolist()}")
        print(df.head(5))
    except Exception as e:
        print(f"Error {s}: {e}")
