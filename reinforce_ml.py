"""
Script de Renforcement du Machine Learning - Couverture Totale des Espèces
========================================================================
Utilise l'extracteur hiérarchique pour intégrer toutes les espèces dans le ML.
"""
import pandas as pd
import numpy as np
import os
from extraction_2024_2025 import extract_summary_data
from ml_models import train_and_save_model

def reinforce_ml_training(base_data_path='onp_real_ml_data.csv',
                         output_path='onp_reinforced_ml_data.csv'):
    """
    Fusionne les données historiques avec l'intégralité des espèces 2024-2025.
    """
    print("="*80)
    print("RENFORCEMENT DU MACHINE LEARNING - COUVERTURE TOTALE")
    print("="*80)
    
    # 1. Charger les données de base (historiques)
    if os.path.exists(base_data_path):
        df_base = pd.read_csv(base_data_path)
        print(f"[OK] Donnees de base chargees: {len(df_base)} lignes")
    else:
        df_base = pd.DataFrame()
        print("[!] Aucun fichier de base trouve.")
    
    # 2. Utiliser l'extracteur amélioré pour obtenir toutes les espèces détaillée
    print("\n[Extraction] Analyse du fichier 2024-2025 avec parser hierarchique...")
    try:
        # Cette fonction contient déjà la logique de parsing DR -> Cat -> Espèce
        df_detailed = extract_summary_data()
        
        # Conversion au format ML (Long)
        new_records = []
        for _, row in df_detailed.iterrows():
            # Record 2024
            if row['volume_2024_t'] > 0:
                new_records.append({
                    'port': row['dr'],
                    'espece': row['espece'],
                    'annee': 2024,
                    'mois': 6,
                    'volume_kg': row['volume_2024_t'] * 1000,
                    'prix_unitaire_dh': row['ca_2024_kdh'] / row['volume_2024_t']
                })
            
            # Record 2025
            if row['volume_2025_t'] > 0:
                new_records.append({
                    'port': row['dr'],
                    'espece': row['espece'],
                    'annee': 2025,
                    'mois': 6,
                    'volume_kg': row['volume_2025_t'] * 1000,
                    'prix_unitaire_dh': row['ca_2025_kdh'] / row['volume_2025_t']
                })
        
        df_extracted = pd.DataFrame(new_records)
        print(f"[OK] {len(df_extracted)} nouveaux records generes pour {df_detailed['espece'].nunique()} especes.")
        
    except Exception as e:
        print(f"[ERROR] Echec de la preparation: {e}")
        df_extracted = pd.DataFrame()

    # 3. Fusion et Nettoyage
    if not df_extracted.empty:
        df_final = pd.concat([df_base, df_extracted], ignore_index=True)
        df_final = df_final.drop_duplicates()
        
        # Sauvegarde
        df_final.to_csv(output_path, index=False)
        print(f"\n[SAVE] Dataset final enregistre: {output_path} ({len(df_final)} lignes)")
        
        # 4. Réentraînement
        print("\n[ML] Lancement du réentraînement global...")
        predictor, results = train_and_save_model(output_path)
        
        # Vérification du nombre d'espèces dans le modèle final
        n_species = df_final['espece'].nunique()
        print(f"\n[VERIFICATION] Le modele supporte desormais {n_species} especes uniques.")
        
        return results
    else:
        print("[!] Echec de l'expansion.")
        return None

if __name__ == "__main__":
    reinforce_ml_training()
