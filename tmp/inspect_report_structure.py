import pandas as pd

f = 'Extraction 2024-2025-traitée avec variation.xlsx'

def inspect_sheet(file, sheet):
    print(f"\n--- Inspecting Sheet: {sheet} ---")
    try:
        df = pd.read_excel(file, sheet_name=sheet, nrows=20, header=None)
        print("First 20 rows:")
        print(df.to_string())
    except Exception as e:
        print(f"Error: {e}")

inspect_sheet(f, 'Variation 1ère Vente')
inspect_sheet(f, 'RECAP')
