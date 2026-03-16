"""
Lire les chiffres officiels dans toutes les feuilles notamment Feuil6 et Feuil2
"""
import pandas as pd
import numpy as np

dr_file = 'New Report(2024-2025) -DR (3).xlsx'
xl = pd.ExcelFile(dr_file)
print("Sheets:", xl.sheet_names)

# Lire Feuil6 - Résumé par DR
print("\n=== FEUIL6 (Résumé DR) ===")
try:
    df6 = xl.parse('Feuil6', header=None)
    print(f"Shape: {df6.shape}")
    print(df6.iloc[:30, :10].to_string())
except Exception as e:
    print(f"Error: {e}")

# Lire Feuil2 - Détail
print("\n=== FEUIL2 - header search ===")
try:
    df2 = xl.parse('Feuil2', header=None, nrows=5)
    print(df2.to_string())
except Exception as e:
    print(f"Error: {e}")
