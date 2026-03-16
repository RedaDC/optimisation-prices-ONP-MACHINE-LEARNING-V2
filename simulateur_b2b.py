"""
Simulateur B2B (Marge Mareyeur) — ONP Premium
==============================================
Module de simulation des marges pour les acheteurs (mareyeurs/industriels).
Permet de calculer le coût de revient total (Prix d'achat + Taxes + Logistique)
et de visualiser la marge nette finale via un graphique Waterfall (Cascade).
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st

# 1. PARAMÈTRES ET TAXES OFFICIELLES

# Taxes appliquées à l'achat en Halle (à la charge de l'acheteur)
TAXE_HALLE_ACHETEUR = 0.03       # 3% (Taxe pour l'ONP)
TAXE_COMMUNALE_ACHETEUR = 0.01   # 1% (Taxe pour la commune)
TOTAL_TAXES_ACHA = TAXE_HALLE_ACHETEUR + TAXE_COMMUNALE_ACHETEUR

# Coûts logistiques par défaut (peuvent être modifiés par l'utilisateur)
DEFAULT_COSTS = {
    'glace_dh_kg': 0.50,         # Coût moyen de la glace par kg
    'manutention_dh_kg': 0.30,   # Chargement/Déchargement personnel halla
    'transport_dh_kg': 1.20,     # Coût moyen transport inter-ville
    'emballage_dh_kg': 0.40      # Caisses plastiques / polystyrène
}

# 2. FONCTION DE CALCUL DES MARGES

def calculate_mareyeur_margin(
    volume_kg: float,
    prix_achat_dh_kg: float,
    prix_revente_dh_kg: float,
    couts_perso: dict = None
) -> dict:
    """
    Calcule tous les éléments de coût et la marge nette pour une transaction.
    """
    if couts_perso is None:
        couts_perso = DEFAULT_COSTS

    # --- 1. Achats et Taxes ---
    valeur_achat_brute = volume_kg * prix_achat_dh_kg
    montant_taxe_halle = valeur_achat_brute * TAXE_HALLE_ACHETEUR
    montant_taxe_commune = valeur_achat_brute * TAXE_COMMUNALE_ACHETEUR
    total_achat_ttc = valeur_achat_brute + montant_taxe_halle + montant_taxe_commune

    # --- 2. Coûts Logistiques ---
    cout_glace = volume_kg * couts_perso.get('glace_dh_kg', 0)
    cout_manutention = volume_kg * couts_perso.get('manutention_dh_kg', 0)
    cout_transport = volume_kg * couts_perso.get('transport_dh_kg', 0)
    cout_emballage = volume_kg * couts_perso.get('emballage_dh_kg', 0)
    
    total_logistique = cout_glace + cout_manutention + cout_transport + cout_emballage

    # --- 3. Coût de Revient et Marge ---
    cout_revient_total = total_achat_ttc + total_logistique
    prix_revient_unitaire = cout_revient_total / volume_kg if volume_kg > 0 else 0
    
    chiffre_affaires_revente = volume_kg * prix_revente_dh_kg
    marge_nette_globale = chiffre_affaires_revente - cout_revient_total
    marge_nette_unitaire = prix_revente_dh_kg - prix_revient_unitaire
    
    # ROI: Return on Investment (%)
    roi_pct = (marge_nette_globale / cout_revient_total * 100) if cout_revient_total > 0 else 0

    return {
        'volume_kg': volume_kg,
        'prix_achat_unitaire': prix_achat_dh_kg,
        'valeur_achat_brute': valeur_achat_brute,
        'montant_taxes': montant_taxe_halle + montant_taxe_commune,
        'details_taxes': {
            'ONP (3%)': montant_taxe_halle,
            'Commune (1%)': montant_taxe_commune
        },
        'total_logistique': total_logistique,
        'details_logistique': {
            'Glace': cout_glace,
            'Manutention': cout_manutention,
            'Transport': cout_transport,
            'Emballage': cout_emballage
        },
        'cout_revient_total': cout_revient_total,
        'prix_revient_unitaire': prix_revient_unitaire,
        'chiffre_affaires_revente': chiffre_affaires_revente,
        'marge_nette_globale': marge_nette_globale,
        'marge_nette_unitaire': marge_nette_unitaire,
        'roi_pct': roi_pct
    }

# 3. VISUALISATION (WATERFALL)

def build_waterfall_chart(calc_res: dict) -> go.Figure:
    """
    Génère un graphique en cascade (Waterfall) détaillé montrant 
    le passage du prix d'achat initial au prix de revient, puis au prix de revente.
    """
    
    # Formatage des valeurs (montants totaux)
    v_achat = calc_res['valeur_achat_brute']
    v_taxes = calc_res['montant_taxes']
    v_glace = calc_res['details_logistique']['Glace']
    v_manu = calc_res['details_logistique']['Manutention']
    v_trans = calc_res['details_logistique']['Transport']
    v_emb = calc_res['details_logistique']['Emballage']
    v_marge = calc_res['marge_nette_globale']
    
    # Configuration du Waterfall
    fig = go.Figure(go.Waterfall(
        name="Cost Breakdown",
        orientation="v",
        measure=["relative", "relative", "relative", "relative", "relative", "relative", "total", "relative", "total"],
        x=["Achat Brut", "Taxes", "Glace", "Manutention", "Transport", "Emballage", "Total Revient", "Marge Nette", "Revente"],
        textposition="outside",
        text=[f"{v:,.0f} DH" for v in [v_achat, v_taxes, v_glace, v_manu, v_trans, v_emb, calc_res['cout_revient_total'], v_marge, calc_res['chiffre_affaires_revente']]],
        y=[v_achat, v_taxes, v_glace, v_manu, v_trans, v_emb, 0, v_marge, 0],
        connector={"line":{"color":"#94A3B8", "width":1.5, "dash":"dot"}},
        decreasing={"marker":{"color":"#EF4444"}}, # Rouge pour baisse (marge négative)
        increasing={"marker":{"color":"#F59E0B"}}, # Orange pour hausse des coûts
        totals={"marker":{"color":"#0EA5E9"}}      # Bleu pour totaux
    ))

    # Mise à jour des styles
    fig.update_traces(
        # On définit les couleurs spécifiques par trace si nécessaire, 
        # mais le Waterfall gère généralement via increasing/decreasing/totals
        # Pour une personnalisation plus fine, on utilise les paramètres ci-dessus.
    )

    fig.update_layout(
        title=dict(
            text="Décomposition du Prix et Marge Nette (Waterfall)",
            font=dict(size=18, family="Outfit", color="#1E293B")
        ),
        showlegend=False,
        plot_bgcolor='rgba(248, 250, 252, 0.8)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Outfit', size=12),
        margin=dict(t=80, b=40, l=40, r=40),
        xaxis=dict(
            showgrid=False,
            tickangle=-25
        ),
        yaxis=dict(
            title="Montant Cumulé (DH)",
            gridcolor='rgba(226, 232, 240, 0.8)'
        )
    )

    return fig
