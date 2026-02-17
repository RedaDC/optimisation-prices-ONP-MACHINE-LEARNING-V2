"""
Module Utilitaire pour l'Application ONP
=========================================

Ce module contient toutes les fonctions utilitaires pour:
- Nettoyage des données
- Feature Engineering
- Encodage des variables catégorielles
- Calculs statistiques et financiers

Auteur: PFE Master Finance & Data Science
Contexte: Office National des Pêches (ONP) - Maroc
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from datetime import datetime


def clean_data(df):
    """
    Nettoie les données en gérant les valeurs manquantes et aberrantes.
    
    Args:
        df (pd.DataFrame): DataFrame brut
        
    Returns:
        pd.DataFrame: DataFrame nettoyé
        
    Explications métier:
        - Les valeurs manquantes sont remplies par la médiane pour éviter l'impact des outliers
        - Les prix négatifs sont supprimés (erreurs de saisie)
        - Les volumes négatifs sont supprimés (erreurs de saisie)
    """
    df_clean = df.copy()
    
    # Conversion de la date
    if 'date_vente' in df_clean.columns:
        df_clean['date_vente'] = pd.to_datetime(df_clean['date_vente'])
    
    # Gestion des valeurs manquantes
    # Pour les colonnes numériques, on remplit avec la médiane
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df_clean[col].isnull().any():
            median_val = df_clean[col].median()
            df_clean[col] = df_clean[col].fillna(median_val if not pd.isna(median_val) else 0)
    
    # Pour les colonnes catégorielles, on remplit avec le mode
    categorical_cols = df_clean.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if df_clean[col].isnull().any():
            df_clean[col].fillna(df_clean[col].mode()[0], inplace=True)
    
    # Suppression des valeurs aberrantes
    # Prix négatifs ou nuls
    if 'prix_unitaire_dh' in df_clean.columns:
        df_clean = df_clean[df_clean['prix_unitaire_dh'] > 0]
    
    # Volumes négatifs ou nuls
    if 'volume_kg' in df_clean.columns:
        df_clean = df_clean[df_clean['volume_kg'] > 0]
    
    # Suppression des outliers extrêmes (au-delà de 3 écarts-types)
    for col in ['prix_unitaire_dh', 'volume_kg']:
        if col in df_clean.columns:
            mean = df_clean[col].mean()
            std = df_clean[col].std()
            df_clean = df_clean[
                (df_clean[col] >= mean - 3*std) & 
                (df_clean[col] <= mean + 3*std)
            ]
    
    return df_clean


def create_features(df):
    """
    Crée de nouvelles features à partir des données existantes.
    
    Args:
        df (pd.DataFrame): DataFrame nettoyé
        
    Returns:
        pd.DataFrame: DataFrame avec nouvelles features
        
    Features créées:
        - saison: Printemps, Été, Automne, Hiver
        - mois: Numéro du mois (1-12)
        - jour_semaine: Jour de la semaine (0=Lundi, 6=Dimanche)
        - volume_moyen_espece: Volume moyen par espèce
        - prix_moyen_port: Prix moyen par port
        - recette_totale: Prix × Volume
    """
    df_feat = df.copy()
    
    # Saison helper
    def get_saison(m):
        if m in [3, 4, 5]: return 'Printemps'
        elif m in [6, 7, 8]: return 'Été'
        elif m in [9, 10, 11]: return 'Automne'
        else: return 'Hiver'

    # Features temporelles
    if 'date_vente' in df_feat.columns:
        df_feat['mois'] = df_feat['date_vente'].dt.month
        df_feat['jour_semaine'] = df_feat['date_vente'].dt.dayofweek
        df_feat['annee'] = df_feat['date_vente'].dt.year
        df_feat['saison'] = df_feat['mois'].apply(get_saison)
    elif 'mois' in df_feat.columns and 'annee' in df_feat.columns:
        df_feat['saison'] = df_feat['mois'].apply(get_saison)
        try:
            # pd.to_datetime nécessite les noms de colonnes year, month, day
            date_df = df_feat[['annee', 'mois']].copy()
            date_df.columns = ['year', 'month']
            date_df['day'] = 1
            df_feat['date_vente'] = pd.to_datetime(date_df)
        except Exception as e:
            print(f"WARN: Erreur creation date_vente: {e}")
            pass
    elif 'mois' in df_feat.columns:
        df_feat['saison'] = df_feat['mois'].apply(get_saison)
    
    # Volume moyen par espèce (feature importante pour la prédiction)
    if 'espece' in df_feat.columns and 'volume_kg' in df_feat.columns:
        volume_moyen = df_feat.groupby('espece')['volume_kg'].transform('mean')
        df_feat['volume_moyen_espece'] = volume_moyen
    
    # Prix moyen par port (indicateur de marché local)
    if 'port' in df_feat.columns and 'prix_unitaire_dh' in df_feat.columns:
        prix_moyen = df_feat.groupby('port')['prix_unitaire_dh'].transform('mean')
        df_feat['prix_moyen_port'] = prix_moyen
    
    # Recette totale (métrique financière clé)
    if 'prix_unitaire_dh' in df_feat.columns and 'volume_kg' in df_feat.columns:
        df_feat['recette_totale'] = df_feat['prix_unitaire_dh'] * df_feat['volume_kg']
    
    return df_feat


def encode_categorical(df, columns_to_encode=None):
    """
    Encode les variables catégorielles en variables numériques.
    
    Args:
        df (pd.DataFrame): DataFrame avec variables catégorielles
        columns_to_encode (list): Liste des colonnes à encoder (optionnel)
        
    Returns:
        tuple: (DataFrame encodé, dictionnaire des encoders)
        
    Explications métier:
        Le LabelEncoder transforme les noms de ports et espèces en nombres
        pour que les modèles ML puissent les utiliser.
        Exemple: Casablanca=0, Agadir=1, Tanger=2, etc.
    """
    df_encoded = df.copy()
    encoders = {}
    
    if columns_to_encode is None:
        # Par défaut, encoder port, espece, categorie, calibre
        columns_to_encode = ['port', 'espece', 'categorie', 'calibre', 'saison']
    
    for col in columns_to_encode:
        if col in df_encoded.columns:
            le = LabelEncoder()
            df_encoded[f'{col}_encoded'] = le.fit_transform(df_encoded[col].astype(str))
            encoders[col] = le
    
    return df_encoded, encoders


def calculate_financial_metrics(df):
    """
    Calcule les métriques financières clés.
    
    Args:
        df (pd.DataFrame): DataFrame avec données de vente
        
    Returns:
        dict: Dictionnaire avec métriques financières
        
    Métriques calculées:
        - Recette totale (en DH)
        - Recette par port
        - Recette par espèce
        - Prix moyen global
        - Volume total
        - Top espèces rentables
    """
    metrics = {
        'recette_totale_dh': 0,
        'recette_totale_mdh': 0,
        'recette_par_port': pd.Series(dtype=float),
        'recette_par_espece': pd.Series(dtype=float),
        'top_especes': pd.Series(dtype=float),
        'prix_moyen_dh_kg': 0,
        'volume_total_kg': 0,
        'volume_total_tonnes': 0,
        'espece_plus_rentable': 'Aucune',
        'recette_espece_top': 0
    }
    
    if df.empty:
        return metrics
    
    # Recette totale
    if 'recette_totale' in df.columns:
        metrics['recette_totale_dh'] = df['recette_totale'].sum()
        metrics['recette_totale_mdh'] = df['recette_totale'].sum() / 1_000_000
    else:
        metrics['recette_totale_dh'] = (df['prix_unitaire_dh'] * df['volume_kg']).sum()
        metrics['recette_totale_mdh'] = metrics['recette_totale_dh'] / 1_000_000
    
    # Recette par port
    if 'port' in df.columns:
        recette_port = df.groupby('port').apply(
            lambda x: (x['prix_unitaire_dh'] * x['volume_kg']).sum()
        )
        if not recette_port.empty:
            recette_port = recette_port.sort_values(ascending=False)
        metrics['recette_par_port'] = recette_port
        metrics['recette_par_port'] = recette_port
    
    # Recette par espèce
    if 'espece' in df.columns:
        recette_espece = df.groupby('espece').apply(
            lambda x: (x['prix_unitaire_dh'] * x['volume_kg']).sum()
        )
        if not recette_espece.empty:
            recette_espece = recette_espece.sort_values(ascending=False)
        metrics['recette_par_espece'] = recette_espece
        metrics['top_especes'] = recette_espece.head(10)
    
    # Prix moyen global
    if 'prix_unitaire_dh' in df.columns:
        metrics['prix_moyen_dh_kg'] = df['prix_unitaire_dh'].mean()
    
    # Volume total
    if 'volume_kg' in df.columns:
        metrics['volume_total_kg'] = df['volume_kg'].sum()
        metrics['volume_total_tonnes'] = df['volume_kg'].sum() / 1000
    
    # Espèce la plus rentable
    if 'recette_par_espece' in metrics and not metrics['recette_par_espece'].empty:
        metrics['espece_plus_rentable'] = metrics['recette_par_espece'].idxmax()
        metrics['recette_espece_top'] = metrics['recette_par_espece'].max()
    
    return metrics


def get_price_statistics(df, group_by='espece'):
    """
    Calcule des statistiques de prix par groupe.
    
    Args:
        df (pd.DataFrame): DataFrame avec données
        group_by (str): Colonne pour grouper ('espece', 'port', etc.)
        
    Returns:
        pd.DataFrame: Statistiques par groupe
    """
    if group_by not in df.columns or 'prix_unitaire_dh' not in df.columns:
        return pd.DataFrame()
    
    stats = df.groupby(group_by)['prix_unitaire_dh'].agg([
        ('prix_min', 'min'),
        ('prix_max', 'max'),
        ('prix_moyen', 'mean'),
        ('prix_median', 'median'),
        ('ecart_type', 'std')
    ]).round(2)
    
    return stats.sort_values('prix_moyen', ascending=False)


def simulate_price_impact(df, espece, port, volume_change_pct):
    """
    Simule l'impact d'un changement de volume sur le prix et la recette.
    
    Args:
        df (pd.DataFrame): DataFrame historique
        espece (str): Nom de l'espèce
        port (str): Nom du port
        volume_change_pct (float): Changement de volume en % (ex: 10 pour +10%)
        
    Returns:
        dict: Résultats de la simulation
        
    Explications métier:
        Cette fonction aide les décideurs de l'ONP à comprendre:
        "Si on augmente/diminue le volume de pêche de X%, 
         quel sera l'impact sur le prix et les recettes?"
    """
    # Filtrer les données pour l'espèce et le port
    mask = (df['espece'] == espece) & (df['port'] == port)
    df_filtered = df[mask]
    
    if df_filtered.empty:
        return {
            'error': f"Aucune donnée pour {espece} à {port}"
        }
    
    # Calculer les moyennes actuelles
    volume_actuel = df_filtered['volume_kg'].mean()
    prix_actuel = df_filtered['prix_unitaire_dh'].mean()
    recette_actuelle = volume_actuel * prix_actuel
    
    # Simuler le nouveau volume
    nouveau_volume = volume_actuel * (1 + volume_change_pct / 100)
    
    # Estimation simple: le prix baisse quand le volume augmente (loi de l'offre)
    # Élasticité prix-volume estimée à -0.3 (à ajuster selon l'analyse économétrique)
    elasticite = -0.3
    variation_prix_pct = elasticite * volume_change_pct
    nouveau_prix = prix_actuel * (1 + variation_prix_pct / 100)
    
    # Nouvelle recette
    nouvelle_recette = nouveau_volume * nouveau_prix
    
    return {
        'espece': espece,
        'port': port,
        'volume_actuel_kg': round(volume_actuel, 2),
        'nouveau_volume_kg': round(nouveau_volume, 2),
        'variation_volume_pct': volume_change_pct,
        'prix_actuel_dh_kg': round(prix_actuel, 2),
        'nouveau_prix_dh_kg': round(nouveau_prix, 2),
        'variation_prix_pct': round(variation_prix_pct, 2),
        'recette_actuelle_dh': round(recette_actuelle, 2),
        'nouvelle_recette_dh': round(nouvelle_recette, 2),
        'impact_recette_dh': round(nouvelle_recette - recette_actuelle, 2),
        'impact_recette_pct': round((nouvelle_recette - recette_actuelle) / recette_actuelle * 100, 2)
    }


if __name__ == "__main__":
    # Test des fonctions
    print("Module utils.py charge avec succes!")
    print("\nFonctions disponibles:")
    print("- clean_data(df)")
    print("- create_features(df)")
    print("- encode_categorical(df)")
    print("- calculate_financial_metrics(df)")
    print("- get_price_statistics(df)")
    print("- simulate_price_impact(df, espece, port, volume_change_pct)")
