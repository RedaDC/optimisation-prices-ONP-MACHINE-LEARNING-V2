import pandas as pd

file = 'Extraction 2024-2025-traitée avec variation.xlsx'
sheet = 'Feuil6'

try:
    df = pd.read_excel(file, sheet_name=sheet)
    print(f"Columns: {df.columns.tolist()}")
    print(df.head(10))
except Exception as e:
    print(f"Error: {e}")
