import pandas as pd

f1 = "Extraction 2024-2025-traitée avec variation.xlsx"
df1_recap = pd.read_excel(f1, sheet_name="RECAP", nrows=5)
print(f"\n--- {f1} RECAP HEADERS ---")
print(df1_recap)

df1_row = pd.read_excel(f1, sheet_name="RECAP", skiprows=540, nrows=20)
print(f"\n--- {f1} RECAP ROW 547 AREA ---")
print(df1_row)

f2 = "prix moyen espece.xlsx"
xl2 = pd.ExcelFile(f2)
print(f"\n--- Sheets in {f2}: {xl2.sheet_names} ---")
for s in xl2.sheet_names:
    df2 = pd.read_excel(f2, sheet_name=s)
    mask = df2.apply(lambda x: x.astype(str).str.contains('467283', na=False)).any(axis=1)
    if mask.any():
        print(f"\nFound 467283 in {f2}, sheet {s}:")
        print(df2[mask])
