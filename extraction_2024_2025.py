"""
Module d'Extraction et Traitement des Données 2024-2025
========================================================
Extrait et prépare les données du fichier 'Extraction 2024-2025-traitée avec variation.xlsx'
"""
import pandas as pd
import numpy as np

EXTRACTION_FILE = 'Extraction 2024-2025-traitée avec variation.xlsx'

def extract_all_sheets():
    """
    Extrait toutes les feuilles du fichier d'extraction
    
    Returns:
        dict: Dictionnaire {nom_feuille: DataFrame}
    """
    xl = pd.ExcelFile(EXTRACTION_FILE)
    sheets = {}
    
    for sheet_name in xl.sheet_names:
        df = pd.read_excel(EXTRACTION_FILE, sheet_name=sheet_name)
        sheets[sheet_name] = df
        print(f"Loaded sheet '{sheet_name}': {df.shape[0]} rows")
    
    return sheets

def extract_summary_data():
    """
    Extrait les données de synthèse (Feuil6) en gérant la hiérarchie.
    Identifie les DR, les catégories et les espèces détaillées.
    """
    df = pd.read_excel(EXTRACTION_FILE, sheet_name='Feuil6')
    df.columns = [str(c).strip() for c in df.columns]
    
    # Liste des DRs connues dans ce fichier (basé sur l'analyse)
    DR_LIST = ['CS', 'MS', 'LSH', 'GON', 'DAKHLA OUED EDAHAB', 'DOED', 'TTAH', 'ORIENTALE', 'GLOBAL']
    # Liste des catégories à filtrer (ce sont des totaux)
    CAT_LIST = ['ALGUES', 'CEPHALOPODES', 'POISSON BLANC', 'POISSON PELAGIQUE', 'CRUSTACES', 'COQUILLAGES', 'AUTRE']
    
    records = []
    current_dr = "GLOBAL"
    current_cat = "AUTRE"
    
    col_label = 'DR/ESPECE'
    
    for idx, row in df.iterrows():
        label = str(row[col_label]).strip()
        if label == 'nan' or label == '': continue
        
        # 1. Détecter si c'est une DR
        if label.upper() in DR_LIST:
            current_dr = label.upper()
            continue
            
        # 2. Détecter si c'est une catégorie (Total)
        if label.upper() in CAT_LIST:
            current_cat = label.upper()
            continue
            
        # 3. C'est une espèce
        # On vérifie si les données sont valides
        try:
            v25 = float(row['Volume Commercialisé (Tonne) 2025'])
            v24 = float(row['Volume Commercialisé (Tonne) 2024'])
            c25 = float(row['CA (KDh) 2025'])
            c24 = float(row['CA (KDh) 2024'])
            
            # On vérifie que ce n'est pas une ligne de total "pêchée" par erreur
            # (Parfois le total d'une catégorie a le même nom que la catégorie)
            # Mais ici les espèces sont sous les catégories.
            
            # Sécurité: on ne prend que si volume > 0
            if (v25 > 0 or v24 > 0):
                records.append({
                    'dr': current_dr,
                    'categorie': current_cat,
                    'espece': label,
                    'volume_2025_t': v25,
                    'volume_2024_t': v24,
                    'ca_2025_kdh': c25,
                    'ca_2024_kdh': c24
                })
        except:
            continue
            
    df_clean = pd.DataFrame(records)
    
    # Calculer les KPIs
    df_clean['var_volume_pct'] = ((df_clean['volume_2025_t'] - df_clean['volume_2024_t']) / df_clean['volume_2024_t'] * 100).fillna(0).replace([np.inf, -np.inf], 0)
    df_clean['var_ca_pct'] = ((df_clean['ca_2025_kdh'] - df_clean['ca_2024_kdh']) / df_clean['ca_2024_kdh'] * 100).fillna(0).replace([np.inf, -np.inf], 0)
    df_clean['var_ca_kdh'] = (df_clean['ca_2025_kdh'] - df_clean['ca_2024_kdh']).fillna(0)
    
    return df_clean

def extract_vente_data(vente_type='1ere'):
    """
    Extrait les données de variation par type de vente
    
    Args:
        vente_type: '1ere' ou '2eme'
        
    Returns:
        pd.DataFrame: Données de variation
    """
    sheet_name = f'Variation {vente_type} Vente' if vente_type == '1ère' else 'Variation 2ème Vente'
    
    df = pd.read_excel(EXTRACTION_FILE, sheet_name=sheet_name)
    
    # Nettoyer et renommer
    col_prefix = 'DR/ESPECE' if vente_type == '1ère' else 'DT/ESPECE'
    
    df = df.rename(columns={
        col_prefix: 'location_espece',
        'Somme de Volume Commercialisé (Tonne) 2025': 'volume_2025_t',
        'Somme de Volume Commercialisé (Tonne) 2024': 'volume_2024_t',
        "Somme de Chiffre d'Affaires (KDh) 2025": 'ca_2025_kdh',
        "Somme de Chiffre d'Affaires (KDh) 2024": 'ca_2024_kdh'
    })
    
    # Calculer variations
    df['var_volume_pct'] = ((df['volume_2025_t'] - df['volume_2024_t']) / df['volume_2024_t'] * 100).fillna(0)
    df['var_ca_pct'] = ((df['ca_2025_kdh'] - df['ca_2024_kdh']) / df['ca_2024_kdh'] * 100).fillna(0)
    df['var_ca_kdh'] = (df['ca_2025_kdh'] - df['ca_2024_kdh']).fillna(0)
    
    df['type_vente'] = vente_type
    
    return df

def prepare_ml_dataset():
    """
    Prépare un dataset formaté pour le machine learning
    
    Returns:
        pd.DataFrame: Dataset ML avec features et target
    """
    df_summary = extract_summary_data()
    
    # Features pour ML
    ml_data = df_summary[[
        'dr', 'espece',
        'volume_2024_t', 'ca_2024_kdh',
        'volume_2025_t', 'ca_2025_kdh',
        'var_volume_pct', 'var_ca_pct'
    ]].copy()
    
    # Calculer prix moyens
    ml_data['prix_moyen_2024'] = ml_data['ca_2024_kdh'] / (ml_data['volume_2024_t'] + 1e-6) * 1000  # DH/kg
    ml_data['prix_moyen_2025'] = ml_data['ca_2025_kdh'] / (ml_data['volume_2025_t'] + 1e-6) * 1000
    ml_data['var_prix_pct'] = ((ml_data['prix_moyen_2025'] - ml_data['prix_moyen_2024']) / ml_data['prix_moyen_2024'] * 100).fillna(0)
    
    # Target: CA 2025
    ml_data['target_ca_2025'] = ml_data['ca_2025_kdh']
    
    # Supprimer les lignes avec données manquantes
    ml_data = ml_data.dropna()
    
    return ml_data

def calculate_global_kpis():
    """
    Calcule les KPIs globaux
    
    Returns:
        dict: KPIs globaux
    """
    df = extract_summary_data()
    
    kpis = {
        'ca_2024_total_mdh': df['ca_2024_kdh'].sum() / 1000,
        'ca_2025_total_mdh': df['ca_2025_kdh'].sum() / 1000,
        'var_ca_mdh': (df['ca_2025_kdh'].sum() - df['ca_2024_kdh'].sum()) / 1000,
        'var_ca_pct': ((df['ca_2025_kdh'].sum() - df['ca_2024_kdh'].sum()) / df['ca_2024_kdh'].sum() * 100),
        'volume_2024_total_t': df['volume_2024_t'].sum(),
        'volume_2025_total_t': df['volume_2025_t'].sum(),
        'var_volume_pct': ((df['volume_2025_t'].sum() - df['volume_2024_t'].sum()) / df['volume_2024_t'].sum() * 100),
        'nb_dr': df['dr'].nunique(),
        'nb_especes': df['espece'].nunique()
    }
    
    return kpis

if __name__ == "__main__":
    print("="*80)
    print("TEST DU MODULE D'EXTRACTION")
    print("="*80)
    
    # Test extraction
    print("\n1. Extraction des données de synthèse...")
    df_summary = extract_summary_data()
    print(f"   Lignes: {len(df_summary)}")
    print(f"   Colonnes: {df_summary.columns.tolist()}")
    
    # Test KPIs
    print("\n2. Calcul des KPIs globaux...")
    kpis = calculate_global_kpis()
    for key, value in kpis.items():
        print(f"   {key}: {value:,.2f}")
    
    # Test ML dataset
    print("\n3. Préparation du dataset ML...")
    ml_data = prepare_ml_dataset()
    print(f"   Lignes: {len(ml_data)}")
    print(f"   Features: {ml_data.columns.tolist()}")
    
    print("\n[OK] Module d'extraction opérationnel")
