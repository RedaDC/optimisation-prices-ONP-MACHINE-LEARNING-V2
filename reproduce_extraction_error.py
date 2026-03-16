from data_loader import extract_ml_data
import os

files = [
    "Extraction 2024-2025-traitée avec variation.xlsx",
    "New Report(2024-2025) (1).xlsx",
    "New Report(2024-2025) -DR (3).xlsx",
    "test_feuil2.xlsx"
]

for f in files:
    if os.path.exists(f):
        print(f"\nTesting: {f}")
        try:
            df = extract_ml_data(f, output_path=f"{f}.csv")
            if df is not None:
                print(f"SUCCESS: Found {len(df)} records.")
            else:
                print("FAILURE: extract_ml_data returned None.")
        except Exception as e:
            print(f"CRASH: {e}")
