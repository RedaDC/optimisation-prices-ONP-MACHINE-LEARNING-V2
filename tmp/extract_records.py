import pandas as pd

f1 = "prix moyen espece.xlsx"
df1 = pd.read_excel(f1)
print(f"Full record for 467283 in {f1}:")
mask1 = df1.apply(lambda x: x.astype(str).str.contains('467283', na=False)).any(axis=1)
print(df1[mask1].to_string())

f2 = "Extraction 2024-2025-traitée avec variation.xlsx"
df2 = pd.read_excel(f2, sheet_name="Variation - 2 ème Vente")
print(f"\nMG CASABLANCA record in {f2}:")
mask2 = df2.apply(lambda x: x.astype(str).str.contains('MG CASABLANCA', case=False, na=False)).any(axis=1)
print(df2[mask2].to_string())

# List first row as headers for df2
print(f"\n{f2} Variation - 2 ème Vente Headers:")
print(df2.head(2).to_string())
