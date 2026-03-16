import pandas as pd

f = "prix moyen espece.xlsx"
try:
    xl = pd.ExcelFile(f)
    print(f"Sheets in {f}: {xl.sheet_names}")
    for sheet in xl.sheet_names:
        df = pd.read_excel(f, sheet_name=sheet)
        mask = df.apply(lambda x: x.astype(str).str.contains('467283|467 283|467.283', na=False)).any(axis=1)
        if mask.any():
            print(f"FOUND 467283 in {f} [{sheet}]:")
            print(df[mask])
except Exception as e:
    print(f"Error: {e}")

f2 = "Extraction 2024-2025-traitée avec variation.xlsx"
try:
    df2 = pd.read_excel(f2, sheet_name="Variation - 2 ème Vente")
    print(f"\nSearching in {f2} [Variation - 2 ème Vente]:")
    mask2 = df2.apply(lambda x: x.astype(str).str.contains('467283|467 283|467.283', na=False)).any(axis=1)
    if mask2.any():
        print("FOUND MATCH!")
        print(df2[mask2])
except Exception as e:
    print(f"Error reading {f2}: {e}")
