import pandas as pd
print("Scanning Data Sources for Species...")

try:
    df2 = pd.read_csv('onp_reinforced_ml_data.csv.bak')
    print("\n--- onp_reinforced_ml_data.csv.bak ---")
    print(f"Total Rows: {len(df2)}")
    if 'espece' in df2.columns:
        species = sorted(df2['espece'].dropna().unique())
        print(f"Unique Espèces ({len(species)}):")
        print(species[:30]) # Print first 30
        print(f"Available Years: {sorted(df2['annee'].dropna().unique())}")
        print(f"Available Months: {sorted(df2['mois'].dropna().unique())}")
except Exception as e:
    print(f"Error reading df2: {e}")
