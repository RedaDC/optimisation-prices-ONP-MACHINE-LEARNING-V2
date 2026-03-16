import pandas as pd

try:
    df = pd.read_csv('onp_real_ml_data.csv')
    df_mg_casa = df[(df['port'] == 'MG CASABLANCA') & (df['annee'] == 2024)]
    
    print("MG CASABLANCA 2024 Data:")
    print(df_mg_casa)
    
    df_mg_casa['ca'] = df_mg_casa['volume_kg'] * df_mg_casa['prix_unitaire_dh']
    total_ca = df_mg_casa['ca'].sum()
    
    print(f"\nTotal CA for MG CASABLANCA in 2024: {total_ca:.2f}")
    
    # Check other MGs
    df_mgs = df[df['port'].str.startswith('MG ') & (df['annee'] == 2024)]
    df_mgs['ca'] = df_mgs['volume_kg'] * df_mgs['prix_unitaire_dh']
    mgs_ca = df_mgs.groupby('port')['ca'].sum()
    print("\nCA for other MGs in 2024:")
    print(mgs_ca)

except Exception as e:
    print(f"Error: {e}")
