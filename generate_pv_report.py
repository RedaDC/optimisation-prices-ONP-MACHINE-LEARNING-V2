import pandas as pd
import os
from financial_analysis import calculate_price_volume_effect
from report_generator import create_comparison_word_report
from utils import clean_data

def generate_report():
    print("Demarrage de la generation du rapport...")

    # 1. Charger les données
    data_path = 'onp_real_ml_data.csv'
    if not os.path.exists(data_path):
        print(f"Erreur: Le fichier {data_path} est introuvable.")
        return

    try:
        df = pd.read_csv(data_path)
        print(f"Donnees chargees: {len(df)} lignes")
    except Exception as e:
        print(f"Erreur lors du chargement des donnees: {e}")
        return

    # 2. Nettoyage de base (si nécessaire)
    # Assurons-nous que 2024 et 2025 sont bien présents
    if 'annee' not in df.columns:
        print("Colonne 'annee' manquante. Tentative de deduction depuis 'date_vente'.")
        if 'date_vente' in df.columns:
            df['date_vente'] = pd.to_datetime(df['date_vente'])
            df['annee'] = df['date_vente'].dt.year
        else:
            print("Impossible de determiner l'annee. Annulation.")
            return

    years = df['annee'].unique()
    print(f"Annees disponibles: {years}")
    
    if 2024 not in years or 2025 not in years:
        print("Les annees 2024 et 2025 sont requises pour la comparaison.")
        return

    # 3. Calcul des effets
    print("Calcul des effets Prix/Volume...")
    df_effects = calculate_price_volume_effect(df)
    
    if df_effects.empty:
        print("Le calcul a retourne un DataFrame vide.")
        return
    
    print(f"Calcul termine pour {len(df_effects)} especes.")
    
    # 4. Génération du rapport Word
    output_filename = "Rapport_Comparaison_Prix_Volume_Espece.docx"
    print(f"Creation du document Word: {output_filename}...")
    
    try:
        final_path = create_comparison_word_report(df_effects, output_path=output_filename)
        print(f"Rapport genere avec succes: {os.path.abspath(final_path)}")
    except Exception as e:
        print(f"Erreur lors de la creation du document Word: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_report()
