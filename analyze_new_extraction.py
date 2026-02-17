"""
Analyse du nouveau fichier d'extraction 2024-2025
"""
import pandas as pd

excel_file = 'Extraction 2024-2025-traitée avec variation.xlsx'

print("="*80)
print(f"ANALYSE: {excel_file}")
print("="*80)

# Lire le fichier
xl = pd.ExcelFile(excel_file)
print(f"\nFeuilles disponibles: {xl.sheet_names}")

for sheet_name in xl.sheet_names:
    print(f"\n{'='*80}")
    print(f"FEUILLE: {sheet_name}")
    print("="*80)
    
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    
    print(f"Dimensions: {df.shape}")
    print(f"\nColonnes: {df.columns.tolist()}")
    print(f"\nAperçu (10 premières lignes):")
    print(df.head(10).to_string())
    
    # Statistiques de base
    if 'annee' in df.columns or 'Annee' in df.columns or 'ANNEE' in df.columns:
        annee_col = [c for c in df.columns if 'annee' in c.lower()][0]
        print(f"\nAnnées présentes: {sorted(df[annee_col].unique())}")
    
    if 'espece' in df.columns or 'Espece' in df.columns or 'ESPECE' in df.columns:
        espece_col = [c for c in df.columns if 'espece' in c.lower()][0]
        print(f"Espèces uniques: {df[espece_col].nunique()}")
        print(f"Liste: {df[espece_col].unique()[:10]}")

print("\n" + "="*80)
print("FIN DE L'ANALYSE")
print("="*80)
