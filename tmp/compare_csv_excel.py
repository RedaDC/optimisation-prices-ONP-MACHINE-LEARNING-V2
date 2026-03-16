import pandas as pd

try:
    df = pd.read_csv('onp_real_ml_data.csv')
    df_mg_casa = df[(df['port'] == 'MG CASABLANCA') & (df['annee'] == 2024)]
    
    total_volume_kg = df_mg_casa['volume_kg'].sum()
    total_ca = (df_mg_casa['volume_kg'] * df_mg_casa['prix_unitaire_dh']).sum()
    
    print(f"MG CASABLANCA 2024 (CSV):")
    print(f"Total Volume: {total_volume_kg:,.2f} kg ({total_volume_kg/1000:,.2f} Tonnes)")
    print(f"Total CA: {total_ca:,.2f} Dh")
    
    print(f"\nExcel Expected (Sheet: Variation - 2 ème Vente):")
    print(f"Total Volume: 110,994.888 Tonnes")
    print(f"Total CA: 467,283.1626 KDh (467,283,162.6 Dh)")
    
    diff_vol = 110994.888 - (total_volume_kg/1000)
    diff_ca = 467283.1626 - (total_ca/1000)
    
    print(f"\nDiscrepancy:")
    print(f"Volume Diff: {diff_vol:,.2f} Tonnes")
    print(f"CA Diff: {diff_ca:,.2f} KDh")

except Exception as e:
    print(f"Error: {e}")
