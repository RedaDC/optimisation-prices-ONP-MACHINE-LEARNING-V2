"""
Module d'Interprétation Machine Learning - Application ONP
==========================================================

Ce module permet d'extraire des explications intelligentes à partir
des modèles de prédiction de prix (XGBoost, Random Forest).
Il transforme les données brutes en insights métier pour les décideurs.
"""

import pandas as pd
import numpy as np
try:
    from onp_assets import LuxIcons
except ImportError:
    # Fallback si absent
    class LuxIcons:
        @staticmethod
        def render(name, **kwargs): return "ℹ️"

def get_prediction_interpretation(predictor, df_ref, species, port, volume_kg, predicted_price, month=None):
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
    
    # 2. Facteurs d'influence
    factors = []
    
    # Impact Volume (Loi de l'offre)
    if diff_vol_pct > 20:
        factors.append({"factor": "Volume Élevé", "impact": "Négatif (Baisse)", "value": f"+{diff_vol_pct:.1f}%", "weight": -0.6})
    elif diff_vol_pct < -20:
        factors.append({"factor": "Rareté (Volume Bas)", "impact": "Positif (Hausse)", "value": f"{diff_vol_pct:.1f}%", "weight": 0.8})
    else:
        factors.append({"factor": "Volume Stable", "impact": "Neutre", "value": "Normal", "weight": 0.1})
        
    # Impact Repos Biologique
    from datetime import datetime
    from utils import REPOS_BIOLOGIQUE_MAP
    check_month = month if month is not None else datetime.now().month
    is_repos = 1 if species.upper() in REPOS_BIOLOGIQUE_MAP and check_month in REPOS_BIOLOGIQUE_MAP[species.upper()] else 0
    
    if is_repos:
        factors.append({"factor": "Repos Biologique", "impact": "Positif (Rareté)", "value": "Actif", "weight": 0.9})
        
    # Impact Port (Saisonnalité/Logistique)
    if predicted_price > avg_price * 1.1:
        factors.append({"factor": "Demande Marché", "impact": "Positif", "value": "Forte", "weight": 0.5})
    
    # 3. Synthèse en langage naturel (Le "Pourquoi")
    insight = ""
    if is_repos:
        insight = f"### {LuxIcons.render('info', size=20)} Analyse de Rareté Réglementaire\n"
        insight += f"L'espèce **{species}** est actuellement sous le régime du **Repos Biologique**."
        insight += f"\n\n**Pourquoi cette hausse ?**\n"
        insight += f"- **Arrêt des captures** : La suspension temporaire de la pêche réduit drastiquement l'offre sur le marché.\n"
        insight += f"- **Pression de la demande** : La demande reste constante alors que les apports sont limités, ce qui tire les prix vers le haut (élasticité inversée).\n"
        insight += f"- **Anticipation de marché** : Le prix prédit de **{predicted_price:.2f} DH/kg** intègre ce facteur de pénurie réglementaire."
    elif diff_price_pct > 5:
        insight = f"Le prix prédit de **{predicted_price:.2f} DH/kg** est en hausse de **{diff_price_pct:.1f}%** par rapport à la normale."
        if diff_vol_pct < -10:
            insight += "\n\n**Raison principale** : **Pénurie d'offre**. Le volume injecté est nettement inférieur aux moyennes de saison, créant une tension immédiate sur les cours."
        else:
            insight += "\n\n**Raison principale** : **Pic de demande**. L'activité observée sur le port de " + port + " indique une forte concurrence entre acheteurs pour cette espèce."
    elif diff_price_pct < -5:
        insight = f"Le prix est en baisse de **{abs(diff_price_pct):.1f}%**."
        if diff_vol_pct > 10:
            insight += "\n\n**Raison principale** : **Surplus d'offre**. Une abondance exceptionnelle de " + species + " sature actuellement la demande locale."
        else:
            insight += "\n\n**Raison principale** : **Correction de marché**. Les prix s'ajustent à la baisse face à une demande plus timide."
    else:
        insight = f"Le prix est **stable**. La prédiction est conforme aux tendances historiques pour {species} au port de {port}."

    return {
        "comparison": {
            "avg_price": avg_price,
            "diff_pct": diff_price_pct,
            "avg_volume": avg_volume,
            "diff_vol_pct": diff_vol_pct
        },
        "factors": factors,
        "insight": insight,
        "status": "Haussier" if (diff_price_pct > 2 or is_repos) else ("Baissier" if diff_price_pct < -2 else "Stable")
    }

def get_global_importance_data(predictor):
    """Récupère l'importance des features pour l'affichage global."""
    if hasattr(predictor, 'get_feature_importance'):
        df = predictor.get_feature_importance(top_n=8)
        
        if df.empty or 'feature' not in df.columns:
            return pd.DataFrame(columns=['feature', 'importance', 'label'])
            
        # Traduction des labels pour le métier
        translation = {
            'volume_kg': 'Volume (Apports)',
            'port_encoded': 'Influence du Port',
            'espece_encoded': 'Type d\'Espèce',
            'mois': 'Saisonnalité (Mois)',
            'jour_semaine': 'Effet Calendaire',
            'is_repos_biologique': 'Repos Biologique',
            'volume_moyen_espece': 'Historique Espèce',
            'prix_moyen_port': 'Niveau de Prix Port',
            'ratio_prix_volume': 'Indice de Rareté'
        }
        df['label'] = df['feature'].map(lambda x: translation.get(x, x))
        return df
    return pd.DataFrame(columns=['feature', 'importance', 'label'])
