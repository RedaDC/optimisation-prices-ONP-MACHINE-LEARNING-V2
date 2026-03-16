import pandas as pd

# 1. Totals from CSV
csv_file = 'onp_real_ml_data.csv'
df_csv = pd.read_csv(csv_file)
df_csv['ca'] = df_csv['volume_kg'] * df_csv['prix_unitaire_dh']

ca_2024_csv = df_csv[df_csv['annee'] == 2024]['ca'].sum()
ca_2025_csv = df_csv[df_csv['annee'] == 2025]['ca'].sum()

print("--- CSV TOTALS (DH) ---")
print(f"2024: {ca_2024_csv:,.2f} DH ({ca_2024_csv/1000:,.2f} KDh)")
print(f"2025: {ca_2025_csv:,.2f} DH ({ca_2025_csv/1000:,.2f} KDh)")

# 2. Totals from Excel Comparative Report
excel_file = 'Extraction 2024-2025-traitée avec variation.xlsx'

def get_excel_totals(file, sheet_name):
    try:
        df = pd.read_excel(file, sheet_name=sheet_name, header=None)
        # We need to find the columns for CA 2024 and CA 2025
        # From previous trace, they are often in specific columns
        # Let's search for "CA (KDh)" or similar strings in the header area
        header_rows = df.iloc[:5]
        ca_2024_col, ca_2025_col = -1, -1
        
        for r in range(len(header_rows)):
            row = header_rows.iloc[r].astype(str).tolist()
            for i, val in enumerate(row):
                if "CA" in val and "2024" in val: ca_2024_col = i
                if "CA" in val and "2025" in val: ca_2025_col = i
        
        if ca_2024_col == -1 or ca_2025_col == -1:
            # Fallback to specific columns if names differ
            # In 'Variation 1ère Vente', CA 2025 is often col 5, CA 2024 is col 6
            ca_2025_col = 5
            ca_2024_col = 6
            
        # Sum columns, skipping header rows
        data = df.iloc[3:]
        def to_float(x):
            try: return float(str(x).replace(' ', '').replace(',', '.'))
            except: return 0.0
            
        sum_2024 = data[ca_2024_col].apply(to_float).sum()
        sum_2025 = data[ca_2025_col].apply(to_float).sum()
        return sum_2024, sum_2025
    except Exception as e:
        print(f"Error reading {sheet_name}: {e}")
        return 0, 0

print("\n--- EXCEL REPORT TOTALS (KDh) ---")
s1_2024, s1_2025 = get_excel_totals(excel_file, 'Variation 1ère Vente')
print(f"Variation 1ère Vente: 2024={s1_2024:,.2f}, 2025={s1_2025:,.2f}")

s2_2024, s2_2025 = get_excel_totals(excel_file, 'Variation 2ème Vente')
print(f"Variation 2ème Vente: 2024={s2_2024:,.2f}, 2025={s2_2025:,.2f}")

total_excel_2024 = s1_2024 + s2_2024
total_excel_2025 = s1_2025 + s2_2025
print(f"GRAND TOTAL EXCEL: 2024={total_excel_2024:,.2f}, 2025={total_excel_2025:,.2f}")

print("\n--- RESULTS ---")
print(f"CSV 2024: {ca_2024_csv/1000:,.2f} KDh")
print(f"EXCEL 2024: {total_excel_2024:,.2f} KDh")
print(f"Diff 2024: {(ca_2024_csv/1000 - total_excel_2024):,.2f} KDh")

print(f"CSV 2025: {ca_2025_csv/1000:,.2f} KDh")
print(f"EXCEL 2025: {total_excel_2025:,.2f} KDh")
print(f"Diff 2025: {(ca_2025_csv/1000 - total_excel_2025):,.2f} KDh")
