import pandas as pd
import openpyxl

file = 'Extraction 2024-2025-traitée avec variation.xlsx'
sheet = 'Variation 1ère Vente'

try:
    df = pd.read_excel(file, sheet_name=sheet)
    print(f"Columns: {df.columns.tolist()}")
    print(f"First 10 rows of 'DR/ESPECE' (or similar):")
    # Clean column names
    df.columns = [str(c).replace('\n', ' ').strip() for c in df.columns]
    
    col_name = None
    for c in df.columns:
        if 'DR/ESPECE' in c:
            col_name = c
            break
            
    if col_name:
        print(df[col_name].head(20).tolist())
    else:
        print("Column DR/ESPECE not found")
        
except Exception as e:
    print(f"Error: {e}")
