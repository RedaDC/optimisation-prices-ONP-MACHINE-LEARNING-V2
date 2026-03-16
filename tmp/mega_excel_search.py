import pandas as pd
import os

files = [
    "Extraction 2024-2025-traitée avec variation.xlsx",
    "New Report(2024-2025) (1).xlsx",
    "New Report(2024-2025) -DR (3).xlsx",
    "prix moyen espece.xlsx",
    "test_feuil2.xlsx"
]

target = 467283
target_str = "467 283"

for f in files:
    if not os.path.exists(f):
        print(f"File not found: {f}")
        continue
    print(f"\n--- Checking {f} ---")
    try:
        xl = pd.ExcelFile(f)
        for sheet in xl.sheet_names:
            df = pd.read_excel(f, sheet_name=sheet)
            # Search for value
            for col in df.columns:
                matches = df[df[col].astype(str).str.contains('467283|467 283|467.283', na=False)]
                if not matches.empty:
                    print(f"FOUND in {f}, sheet '{sheet}', col '{col}':")
                    print(matches)
            
            # Search for sums or metrics close to it
            for col in df.select_dtypes(include=['number']).columns:
                if abs(df[col].sum() - target) < 100:
                    print(f"SUM of {f}, sheet '{sheet}', col '{col}' is {df[col].sum():.2f} (matches target!)")
                if abs(df[col].mean() - target) < 100:
                    print(f"MEAN of {f}, sheet '{sheet}', col '{col}' is {df[col].mean():.2f} (matches target!)")

    except Exception as e:
        print(f"Error reading {f}: {e}")
