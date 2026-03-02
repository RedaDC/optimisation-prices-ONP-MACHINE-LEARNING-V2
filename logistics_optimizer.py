"""
Module d'Optimisation Logistique - OceanSense AI
===============================================
Ce module suggère les ports de débarquement les plus rentables pour une espèce donnée
en comparant les prédictions de prix sur différents sites.
"""

import pandas as pd
import numpy as np

def suggest_optimal_ports(predictor, df_ref, species, volume_kg, current_port=None):
    """
    Compare les prix prédits pour une espèce dans différents ports et suggère les meilleurs.
    """
    all_ports = df_ref['port'].unique()
    recommendations = []
    
    # Obtenir les prédictions pour tous les ports
    for port in all_ports:
        predicted_price = predictor.predict_single(df_ref, species, port, volume_kg)
        
        # Simulation d'un coût de transport simplifié (si on change de port)
        transport_cost = 0
        if current_port and port != current_port:
            transport_cost = 1.5 # Coût forfaitaire de transport/logistique en DH/kg
            
        net_price = predicted_price - transport_cost
        
        recommendations.append({
            'port': port,
            'prix_predit': predicted_price,
            'cout_transport': transport_cost,
            'prix_net_estime': net_price,
            'recette_estimee': net_price * volume_kg
        })
    
    # Trier par recette estimée
    df_rec = pd.DataFrame(recommendations).sort_values('recette_estimee', ascending=False)
    
    # Calculer le gain potentiel par rapport au port actuel
    if current_port:
        current_recette = df_rec[df_rec['port'] == current_port]['recette_estimee'].values[0]
        df_rec['gain_potentiel_dh'] = df_rec['recette_estimee'] - current_recette
    else:
        df_rec['gain_potentiel_dh'] = 0
        
    return df_rec.head(5)

def get_market_saturation_alerts(df_recent):
    """
    Analyse les volumes récents pour détecter des risques de saturation (chute de prix).
    """
    alerts = []
    # Calculer le volume moyen par port sur les dernières entrées
    port_volumes = df_recent.groupby('port')['volume_kg'].mean()
    global_avg_volume = df_recent['volume_kg'].mean()
    
    for port, vol in port_volumes.items():
        if vol > global_avg_volume * 1.5:
            alerts.append({
                'type': 'WARNING',
                'message': f"Risque de saturation au port de {port}. Volume {vol/1000:.1f}T (+50% vs moyenne).",
                'port': port
            })
            
    return alerts
