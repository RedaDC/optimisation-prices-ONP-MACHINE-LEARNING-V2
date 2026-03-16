import pandas as pd

dr_file = 'New Report(2024-2025) -DR (3).xlsx'
xl = pd.ExcelFile(dr_file)

try:
    df_var = xl.parse('Variation 1ère Vente', header=2)
    print("Variation 1ère Vente:")
    ca_2024 = df_var["Somme de Chiffre d'Affaires (KDh) 2024"].sum()
    ca_2025 = df_var["Somme de Chiffre d'Affaires (KDh) 2025"].sum()
    print(f"CA 2024 (MDH): {ca_2024/1000:,.2f}")
    print(f"CA 2025 (MDH): {ca_2025/1000:,.2f}")
except Exception as e:
    print(f"Error reading Variation 1ère Vente: {e}")

try:
    df_feuil6 = xl.parse('Feuil6', header=1)
    print("\nFeuil6 (Synthèse):")
    # Affiche le grand total si présent (souvent à la dernière ligne ou dans des colonnes spécifiques)
    print(df_feuil6.tail())
except Exception as e:
    print(f"Error reading Feuil6: {e}")
