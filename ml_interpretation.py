"""
Module d'Interprétation Machine Learning - Application ONP
==========================================================

Ce module permet d'extraire des explications intelligentes à partir
des modèles de prédiction de prix (XGBoost, Random Forest).
Il transforme les données brutes en insights métier pour les décideurs.
"""

import pandas as pd
import numpy as np

def get_prediction_interpretation(predictor, df_ref, species, port, volume_kg, predicted_price):
    """
    Génère une interprétation complète d'une prédiction.
    
    Returns:
        dict: Contient le résumé, les facteurs et l'insight métier.
    """
    # 1. Calculer la moyenne historique pour comparaison
    hist_mask = (df_ref["espece"] == species)
    if not df_ref[hist_mask & (df_ref["port"] == port)].empty:
        hist_mask = hist_mask & (df_ref["port"] == port)
        
    avg_price = df_ref[hist_mask]["prix_unitaire_dh"].mean()
    avg_volume = df_ref[hist_mask]["volume_kg"].mean()
    
    diff_price_pct = ((predicted_price - avg_price) / avg_price) * 100
    diff_vol_pct = ((volume_kg - avg_volume) / avg_volume) * 100
    
    # 2. Facteurs d'influence (Simulé basé sur les corrélations métier ONP)
    # Dans une version réelle, on utiliserait SHAP values ici.
    factors = []
    
    # Impact Volume (Loi de l'offre)
    if diff_vol_pct > 20:
        factors.append({"factor": "Volume Élevé", "impact": "Négatif (Baisse)", "value": f"+{diff_vol_pct:.1f}%", "weight": -0.6})
    elif diff_vol_pct < -20:
        factors.append({"factor": "Rareté (Volume Bas)", "impact": "Positif (Hausse)", "value": f"{diff_vol_pct:.1f}%", "weight": 0.8})
    else:
        factors.append({"factor": "Volume Stable", "impact": "Neutre", "value": "Normal", "weight": 0.1})
        
    # Impact Port (Saisonnalité/Logistique)
    if predicted_price > avg_price * 1.1:
        factors.append({"factor": "Demande Marché", "impact": "Positif", "value": "Forte", "weight": 0.5})
    
    # 3. Synthèse en langage naturel
    insight = ""
    if diff_price_pct > 5:
        insight = f"Le prix prédit de {predicted_price:.2f} DH/kg est supérieur à la moyenne historique ({avg_price:.2f} DH/kg)."
        if diff_vol_pct < -10:
            insight += " Cette hausse s'explique principalement par un volume d'apport inférieur à la normale, créant une tension sur l'offre."
        else:
            insight += " Cette tendance reflète une forte demande actuelle sur le port de " + port + "."
    elif diff_price_pct < -5:
        insight = f"On observe une baisse de {abs(diff_price_pct):.1f}% par rapport au prix moyen."
        if diff_vol_pct > 10:
            insight += " La forte disponibilité de " + species + " sur le marché pèse sur les cours."
        else:
            insight += " Les conditions de marché sont actuellement favorables aux acheteurs."
    else:
        insight = "Le prix prédit est stable et conforme aux tendances saisonnières observées pour le port de " + port + "."

    return {
        "comparison": {
            "avg_price": avg_price,
            "diff_pct": diff_price_pct,
            "avg_volume": avg_volume,
            "diff_vol_pct": diff_vol_pct
        },
        "factors": factors,
        "insight": insight,
        "status": "Haussier" if diff_price_pct > 2 else ("Baissier" if diff_price_pct < -2 else "Stable")
    }

def get_global_importance_data(predictor):
    """Récupère l'importance des features pour l'affichage global."""
    if hasattr(predictor, 'get_feature_importance'):
        df = predictor.get_feature_importance(top_n=8)
        # Traduction des labels pour le métier
        translation = {
            'volume_kg': 'Volume (Apports)',
            'port_encoded': 'Influence du Port',
            'espece_encoded': 'Type d\'Espèce',
            'mois': 'Saisonnalité (Mois)',
            'jour_semaine': 'Effet Calendaire',
            'volume_moyen_espece': 'Historique Espèce',
            'prix_moyen_port': 'Niveau de Prix Port',
            'ratio_prix_volume': 'Indice de Rareté'
        }
        df['label'] = df['feature'].map(lambda x: translation.get(x, x))
        return df
    return pd.DataFrame()
