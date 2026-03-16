import pandas as pd, sys, os
sys.path.insert(0, os.getcwd())

print("=" * 60)
print("VERIFICATION FINALE CA 2024-2025")
print("=" * 60)

# 1. Check onp_real_ml_data.csv
df = pd.read_csv('onp_real_ml_data.csv')
df['ca'] = df['volume_kg'] * df['prix_unitaire_dh']

ca24 = df[df['annee']==2024]['ca'].sum() / 1000
ca25 = df[df['annee']==2025]['ca'].sum() / 1000
vol24 = df[df['annee']==2024]['volume_kg'].sum() / 1000
vol25 = df[df['annee']==2025]['volume_kg'].sum() / 1000
rows24 = len(df[df['annee']==2024])
rows25 = len(df[df['annee']==2025])

print(f"\n[onp_real_ml_data.csv]")
print(f"  2024: {ca24:,.2f} KDh | {vol24:,.2f} T | {rows24} records")
print(f"  2025: {ca25:,.2f} KDh | {vol25:,.2f} T | {rows25} records")

# 2. Check RECAP benchmark
import openpyxl
wb = openpyxl.load_workbook('Extraction 2024-2025-traitée avec variation.xlsx', read_only=True, data_only=True)
ws = wb['RECAP']
total_row = None
for row in ws.iter_rows(values_only=True):
    if row[0] and 'Total général' in str(row[0]):
        total_row = row
        break
wb.close()

if total_row:
    recap_ca25 = total_row[4]
    recap_ca24 = total_row[5]
    print(f"\n[RECAP Benchmark]")
    print(f"  2024: {recap_ca24:,.2f} KDh")
    print(f"  2025: {recap_ca25:,.2f} KDh")
    
    diff24 = abs(ca24 - recap_ca24)
    diff25 = abs(ca25 - recap_ca25)
    print(f"\n[Matching Check]")
    print(f"  2024 Diff: {diff24:,.2f} KDh ({diff24/recap_ca24*100:.4f}%)")
    print(f"  2025 Diff: {diff25:,.2f} KDh ({diff25/recap_ca25*100:.4f}%)")
    
    if diff24/recap_ca24 < 0.001 and diff25/recap_ca25 < 0.001:
        print("\n  ✅ VERIFICATION PASSED: CSV matches official RECAP within 0.1%")
    else:
        print("\n  ❌ VERIFICATION FAILED: Significant discrepancy detected")
else:
    print("WARNING: Could not find 'Total général' in RECAP")

# 3. Check ca_reduction_2024_2025.csv
if os.path.exists('ca_reduction_2024_2025.csv'):
    df_red = pd.read_csv('ca_reduction_2024_2025.csv')
    red24 = df_red['ca_2024_kdh'].sum()
    red25 = df_red['ca_2025_kdh'].sum()
    print(f"\n[ca_reduction_2024_2025.csv]")
    print(f"  2024: {red24:,.2f} KDh")
    print(f"  2025: {red25:,.2f} KDh")

print("\n" + "=" * 60)
