"""
Module des Opérations ML - Application ONP
=========================================

Ce module contient la logique métier opérationnelle pour l'usage quotidien
par les employés de l'ONP (Crieurs, Gestionnaires de Port, Contrôleurs).
"""

import pandas as pd
import numpy as np
import os
from data_loader import extract_ml_data
from ml_models import train_and_save_model

def retrain_model_from_excel(uploaded_file):
    """
    Réentraîne les modèles ML à partir d'un nouveau fichier Excel ONP.
    """
    try:
        # 1. Extraction des données (sauvegarde dans le CSV temporaire pour ml_models)
        temp_csv = "onp_real_ml_data.csv"
        df_ml = extract_ml_data(uploaded_file, output_path=temp_csv)
        
        if df_ml is None or df_ml.empty:
            return {"error": "Impossible d'extraire les données du fichier (Format non reconnu ou feuille 'Feuil2' manquante)."}
            
        # 2. Réentraînement
        predictor, results = train_and_save_model(temp_csv)
        
        if results:
            return {
                "success": True,
                "row_count": len(df_ml),
                "results": results,
                "predictor": predictor
            }
        else:
            return {"error": "L'entraînement a échoué sans erreur explicite."}
            
    except Exception as e:
        return {"error": f"Erreur lors du réentraînement : {str(e)}"}

def get_landing_recommendation(predictor, df_ref, species, volume_kg):
    """
    Simule les revenus potentiels sur tous les ports pour recommander le meilleur landing.
    """
    ports = df_ref['port'].unique()
    recommendations = []
    
    for port in ports:
        try:
            pred_price = predictor.predict_single(df_ref, species, port, volume_kg)
            potential_revenue = pred_price * volume_kg
            recommendations.append({
                "port": port,
                "predicted_price": pred_price,
                "potential_revenue": potential_revenue
            })
        except:
            continue
            
    if not recommendations:
        return None
        
    # Trier par revenu potentiel
    df_rec = pd.DataFrame(recommendations).sort_values("potential_revenue", ascending=False)
    return df_rec

def get_auction_starting_price(predictor, df_ref, species, port, volume_kg):
    """
    Suggère une mise à prix pour les crieurs (Auctioneers).
    Basé sur le prix prédit avec une marge de sécurité.
    """
    try:
        pred_price = predictor.predict_single(df_ref, species, port, volume_kg)
        
        # Stratégie de mise à prix (ex: 85% du prix prédit pour stimuler les enchères)
        starting_price = pred_price * 0.85
        
        # Récupérer le maximum historique récent
        mask = (df_ref['espece'] == species) & (df_ref['port'] == port)
        recent_max = df_ref[mask]['prix_unitaire_dh'].tail(10).max()
        
        return {
            "suggested_starting_price": round(starting_price, 2),
            "target_price": round(pred_price, 2),
            "recent_max": round(recent_max, 2) if not np.isnan(recent_max) else None
        }
    except:
        return None

def detect_market_anomalies(df_recent, predictor):
    """
    Identifie les transactions suspectes ou les erreurs de saisie avec explications.
    """
    anomalies = []
    
    # Échantillon pour le test (dernières transactions pour réactivité)
    # Dans un environnement réel, on pourrait scanner tout le batch
    test_df = df_recent.tail(50).copy()
    
    for idx, row in test_df.iterrows():
        try:
            # 1. Analyse basée sur le modèle ML (Écart de prédiction)
            pred = predictor.predict_single(df_recent, row['espece'], row['port'], row['volume_kg'])
            actual = row['prix_unitaire_dh']
            deviation = (actual - pred) / pred
            
            # 2. Analyse statistique locale (Z-Score simplifié sur l'espèce)
            mask = df_recent['espece'] == row['espece']
            avg_price = df_recent[mask]['prix_unitaire_dh'].mean()
            std_price = df_recent[mask]['prix_unitaire_dh'].std()
            z_score = (actual - avg_price) / std_price if std_price > 0 else 0
            
            reason = ""
            if abs(deviation) > 0.4:
                if deviation > 0:
                    reason = f"Prix {abs(deviation)*100:.1f}% supérieur à la prédiction IA."
                else:
                    reason = f"Prix {abs(deviation)*100:.1f}% inférieur à la prédiction IA."
            
            if abs(z_score) > 3:
                reason += f" Écart statistique critique (Z-score: {z_score:.1f})."
            
            if reason:
                anomalies.append({
                    "date": row['date_vente'],
                    "espece": row['espece'],
                    "port": row['port'],
                    "actual_price": actual,
                    "expected_price": round(pred, 2),
                    "deviation_pct": round(deviation * 100, 1),
                    "reason": reason,
                    "severity": "High" if abs(deviation) > 0.6 or abs(z_score) > 4 else "Medium"
                })
        except:
            continue
            
    return pd.DataFrame(anomalies)
