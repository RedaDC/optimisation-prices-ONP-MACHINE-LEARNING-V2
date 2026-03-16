import pandas as pd

f = 'Extraction 2024-2025-traitée avec variation.xlsx'

def get_totals_from_recap(file):
    print(f"\n--- Totals from RECAP ---")
    df = pd.read_excel(file, sheet_name='RECAP', header=None)
    # Search for "Total général" in column 0
    mask = df[0].astype(str).str.contains('Total général', case=False, na=False)
    total_row = df[mask]
    if not total_row.empty:
        print("Total Général Row found:")
        print(total_row.to_string())
        # Based on index from previous run:
        # Col 4: CA 2025, Col 5: CA 2024
        ca_2025 = total_row.iloc[0, 4]
        ca_2024 = total_row.iloc[0, 5]
        print(f"Official Total CA 2024: {ca_2024:,.2f} KDh")
        print(f"Official Total CA 2025: {ca_2025:,.2f} KDh")
        return ca_2024, ca_2025
    else:
        print("Total général NOT found in RECAP.")
        return None, None

def check_vf_headers(file):
    print(f"\n--- Headers: extraction retraitée VF ---")
    df = pd.read_excel(file, sheet_name='extraction retraitée VF', nrows=5, header=None)
    print(df.to_string())

get_totals_from_recap(f)
check_vf_headers(f)
