import sys
import os
import pandas as pd

# Add current directory to path
sys.path.append(os.getcwd())

import data_loader

f = 'Extraction 2024-2025-traitée avec variation.xlsx'
print(f"Starting full extraction from {f}...")
data_loader.extract_ml_data(f, output_path='onp_real_ml_data.csv')

print("\nVerifying extraction results...")
if os.path.exists('onp_real_ml_data.csv'):
    df = pd.read_csv('onp_real_ml_data.csv')
    df['ca'] = df['volume_kg'] * df['prix_unitaire_dh']

    for year in [2024, 2025]:
        total_ca = df[df['annee'] == year]['ca'].sum()
        count = len(df[df['annee'] == year])
        print(f"Year {year}: {count} records, CA = {total_ca/1000:,.2f} KDh")

    # Check CAPI DAKHLA
    capi = df[df['port'] == 'CAPI DAKHLA']
    print(f"\nCAPI DAKHLA Records: {len(capi)}")
    if not capi.empty:
        print(f"CAPI DAKHLA Species Sample: {capi['espece'].unique()[:10]}")
        c24 = capi[capi['annee']==2024]['ca'].sum()
        print(f"CAPI DAKHLA CA 2024: {c24/1000:,.2f} KDh")
else:
    print("ERROR: onp_real_ml_data.csv was not created.")
