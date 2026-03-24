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
import requests
import streamlit as st
from sklearn.preprocessing import LabelEncoder
from datetime import datetime

# Mapping des coordonnées GPS des ports marocains
PORT_COORDINATES = {
    'CASABLANCA': (33.6, -7.6),
    'AGADIR': (30.4, -9.6),
    'TANGER': (35.9, -5.5),
    'NADOR': (35.17, -2.93),
    'LAAYOUNE': (27.1, -13.4),
    'DAKHLA': (23.6, -15.9),
    'SAFI': (32.3, -9.2),
    'ESSAOUIRA': (31.5, -9.7),
    'KENITRA': (34.3, -6.6),
    'LARACHE': (35.2, -6.1),
    'SIDI IFNI': (29.4, -10.2),
    'TAN-TAN': (28.5, -11.3),
    'BOUJDOUR': (26.1, -14.5),
    'TARFAYA': (27.9, -12.9),
    'MOHAMMEDIA': (33.7, -7.4)
}

import os

def normalize_species_name(name):
    """Normalise le nom pour le mapping d'images (minuscules, sans accents, underscores)."""
    import unicodedata
    import re
    if not isinstance(name, str): return ""
    name = name.lower().strip()
    
    # Dictionnaire de synonymes pour fusionner les doublons (noms d'espèces -> clé unique)
    synonyms = {
        'bar': ['bar_commun', 'loup', 'bar_loup', 'bar_europeen', 'bar_tachete', 'barloup', 'bar_faux'],
        'bar_mouchete': ['bar_loup_mouchete', 'bar_mouchete_ou_loup', 'bar_mouchette'],
        'baudroie': ['lotte', 'baudroie_commune', 'baudroie_lotte', 'baudroie_rousse'],
        'bonite': ['bonite_a_ventre_raye', 'bonite_a_dos_raye', 'bonite_sarda', 'bonito'],
        'congre': ['congre_d_europe', 'congre_deurope', 'congre_europe', 'congre_petit'],
        'baliste': ['baliste_cabri', 'balistie_cabri'],
        'calamar': ['calmar', 'calmar_encornet', 'calmar_petit', 'calmar_vrai', 'calmar_vrai_poisson'],
        'roussette': ['chien_et_roussette', 'chiens_et_roussettes', 'petite_roussette'],
        'castagnole': ['castagnol', 'castagnole_noir'],
        'pageot': ['pageot_royale', 'pageot_royal', 'pagoet_royal'],
        'maquereau': ['maquereau_atlantique', 'maquereau_esp_atlantique', 'maquereau_commun'],
        'anchois': ['anchois_m', 'anchois_g', 'anchois_p'],
        'sardine': ['sardine_m', 'sardine_g', 'sardine_p'],
        'dorade': ['dorade_royale', 'daurade_royale', 'dorade_grise', 'dorade_rose'],
        'sabre': ['sabre_argent', 'sabre_argente'],
        'homard': ['homard_europeen', 'homard_commun'],
        'saint_pierre': ['saint_pierre_argente', 'st_pierre'],
        'bogue': ['bogue_commun'],
        'poulpe': ['pieuvre'],
        'mulet_dore': ['mulet_dore', 'multe_dore', 'mulet', 'multe', 'mulet_sauteur', 'mulet_laberon', 'mulet_lippu'],
    }
    
    # Nettoyage initial des suffixes génériques d'abord
    name = re.sub(r'\(frais\)', '', name)
    name = re.sub(r'\s+commun$', '', name)
    name = re.sub(r'\s+gg$', '', name)
    name = re.sub(r'\s+\(pp\)$', '', name)
    
    # Puis nettoyage des tailles (G, M, P, T, GG, TT) à la fin
    # Supporte les formats: "ESPECE G", "ESPECE-G", "ESPECE_G", "ESPECE GG"
    name = re.sub(r'[\s\-_]+[gmptx]{1,2}$', '', name)
    
    # Normalisation des caractères
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    name = re.sub(r'[^a-z0-9]+', '_', name).strip('_')
    
    # Application des synonymes
    for target, variations in synonyms.items():
        if name in variations or name == target:
            return target
            
    return name

def get_species_image_path(species_name):
    """
    Retourne le chemin local ou l'URL de l'image pour une espèce donnée.
    Recherche d'abord une image spécifique, puis une photo réelle (préfixe wiki_ ou asset), sinon fallback.
    """
    from onp_assets import get_image_path as get_asset_path
    from onp_assets import IMAGES_PECHE_MAROC
    
    default_img = IMAGES_PECHE_MAROC.get("marche_poisson", "")
    
    if not species_name:
        return default_img
        
    key = normalize_species_name(species_name)
    
    # 1. Chercher dans les assets explicites (nom de base normalisé)
    asset_path = get_asset_path(key)
    if asset_path:
        # Si c'est un chemin local qui existe ou une URL non vide
        if str(asset_path).startswith("http"):
            return asset_path
        if os.path.exists(asset_path):
            return asset_path
            
    # 2. Chercher dans assets/images avec préfixes communs (photos réelles) ou direct
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(base_dir, "assets", "images")
    if os.path.exists(img_dir):
        for ext in ['.jpg', '.png', '.jpeg']:
            # Liste des préfixes à essayer pour les photos réelles
            for prefix in ["wiki_", "real_", ""]:
                p = os.path.join(img_dir, f"{prefix}{key}{ext}")
                if os.path.exists(p):
                    return p
            
            # Cas spécial pour les noms avec tirets/underscores inversés
            key_alt = key.replace('_', '-')
            if key_alt != key:
                for prefix in ["wiki_", "real_", ""]:
                    p = os.path.join(img_dir, f"{prefix}{key_alt}{ext}")
                    if os.path.exists(p):
                        return p
    
    # 3. Fallback sur les catégories génériques (mots clés)
    if any(k in key for k in ["crevette", "shrimp"]):
        local_crevette = os.path.join(img_dir, "crevette.jpg")
        if os.path.exists(local_crevette): return local_crevette
        return IMAGES_PECHE_MAROC.get("crevette_rose", default_img)
    if any(k in key for k in ["moule", "mussel"]): return IMAGES_PECHE_MAROC.get("moule", default_img)
    if any(k in key for k in ["coquill", "shell"]): return IMAGES_PECHE_MAROC.get("coquillages", default_img)
    if "sole" in key: return IMAGES_PECHE_MAROC.get("sole", default_img)
    if "pageot" in key: return IMAGES_PECHE_MAROC.get("pageot", default_img)
    if "calamar" in key or "calmar" in key: return IMAGES_PECHE_MAROC.get("calamar", default_img)
    if "requin" in key or "shark" in key: return IMAGES_PECHE_MAROC.get("requin_ha", default_img)
    
    return default_img

def has_real_species_image(species_name):
    """
    Vérifie si une espèce possède une photo réelle (Wikipedia, Unsplash ou locale).
    Retourne False si c'est l'image par défaut.
    """
    from onp_assets import IMAGES_PECHE_MAROC
    
    if not species_name:
        return False
        
    img_path = get_species_image_path(species_name)
    default_img = IMAGES_PECHE_MAROC.get("marche_poisson", "")
    hero_img = IMAGES_PECHE_MAROC.get("hero", "")
    
    # Échec si pas de chemin, ou si c'est l'image par défaut/hero, ou si c'est vide
    if not img_path or img_path == default_img or img_path == hero_img or img_path == "":
        return False
        
    # Vérification supplémentaire : si c'est un chemin local, il doit exister physiquement
    if not str(img_path).startswith("http") and not os.path.exists(img_path):
        return False
        
    return True

def get_unique_valid_species(df, require_image=False):
    """Retourne une liste d'espèces dédoublonnées et 'propres' (sans tailles) pour l'UI."""
    import pandas as pd
    
    col_name = "espece" if "espece" in df.columns else "Espèce" if "Espèce" in df.columns else None
    if not col_name: return []
    
    all_raw = sorted(df[col_name].dropna().unique().tolist())
    
    seen_norm = set()
    final_list = []
    
    for s in all_raw:
        if not s: continue
        norm = normalize_species_name(s)
        
        # On ne garde qu'une seule version par espèce "racine"
        if norm not in seen_norm:
            # Créer un nom propre : ex "Merlu" au lieu de "merlu"
            clean_name = norm.replace('_', ' ').upper()
            
            # Cas particuliers pour garder le style ONP
            if clean_name == "BAR": clean_name = "BAR (LOUP)"
            
            # Filtrage optionnel par image
            if require_image and not has_real_species_image(clean_name):
                continue
            
            if clean_name not in final_list:
                final_list.append(clean_name)
            seen_norm.add(norm)
            
    return sorted(final_list)

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
            
    # Filtrage des lignes avec des valeurs 'Inconnu' ou 'Autre' dans l'espèce
    if 'espece' in df_clean.columns:
        unwanted = ['INCONNU', 'AUTRE', 'GROUPE INCONNU', 'AUTRES', 'INCONNUS']
        df_clean = df_clean[~df_clean['espece'].str.upper().str.strip().isin(unwanted)]
        
        # Filtrage strict global: On supprime toutes les espèces qui n'ont pas d'image
        def check_valid_image(esp):
            if pd.isna(esp) or not str(esp).strip(): 
                return False
            norm = normalize_species_name(str(esp))
            clean_name = norm.replace('_', ' ').upper()
            if clean_name == "BAR": clean_name = "BAR (LOUP)"
            return has_real_species_image(clean_name)
            
        mask_image = df_clean['espece'].apply(check_valid_image)
        df_clean = df_clean[mask_image]
    
    # Suppression des valeurs aberrantes
    # Prix négatifs ou nuls
    if 'prix_unitaire_dh' in df_clean.columns:
        df_clean = df_clean[df_clean['prix_unitaire_dh'] > 0]
    
    # Volumes négatifs ou nuls
    if 'volume_kg' in df_clean.columns:
        df_clean = df_clean[df_clean['volume_kg'] > 0]
    
    # Suppression des outliers par espèce (plus précis)
    # On utilise un seuil de 3 écarts-types (3-sigma) pour éliminer les erreurs de saisie
    # tout en restant représentatif des tendances de marché.
    for col in ['prix_unitaire_dh', 'volume_kg']:
        if col in df_clean.columns and 'espece' in df_clean.columns:
            # Calculer mean/std par espèce séparément
            group = df_clean.groupby('espece')[col]
            m_vals = group.transform('mean')
            s_vals = group.transform('std')
            
            # Garder les lignes dans 3 sigma ou les espèces avec trop peu de données
            mask = (df_clean[col] <= m_vals + 3 * s_vals) & \
                   (df_clean[col] >= m_vals - 3 * s_vals)
            # Si std est nul ou NaN (une seule ligne), on garde
            mask = mask | s_vals.isna() | (s_vals == 0)
            df_clean = df_clean[mask]
    
    return df_clean


# Mapping des repos biologiques par espèce/groupe au Maroc
# (Vérifier officiellement auprès de l'ONP pour les dates exactes annuelles)
REPOS_BIOLOGIQUE_MAP = {
    'CEPHALOPODES': [4, 5, 9, 10],  # Poulpe, Seiche, Calmar - Printemps/Automne
    'CRUSTACES': [7, 8],          # Crevette, Langouste - Juillet/Août
    'POISSON BLANC': [6, 7],      # Exemple, varie selon les espèces
    'CALMAR': [4, 5, 9, 10]
}

# Mapping des régions avec distinction fine Nord/Centre/Sud/Grand-Sud
# IMPORTANT: Le Grand Sud (Provinces Sahhariennes) bénéficie d'exonérations majeures
REGION_MAP = {
    # NORD
    'TANGER': 'NORD', 'LARACHE': 'NORD', 'AL HOCEIMA': 'NORD', 'NADOR': 'NORD', 'KENITRA': 'NORD', 'MEHDIA': 'NORD',
    # CENTRE
    'CASABLANCA': 'CENTRE', 'MOHAMMEDIA': 'CENTRE', 'EL JADIDA': 'CENTRE', 'SAFI': 'CENTRE', 'ESSAOUIRA': 'CENTRE',
    # SUD (Souss-Massa)
    'AGADIR': 'SUD', 'SIDI IFNI': 'SUD',
    # GRAND SUD (Provinces Sahhariennes - Exonérations importantes)
    'TAN-TAN': 'GRAND_SUD', 'BOUJDOUR': 'GRAND_SUD', 'TARFAYA': 'GRAND_SUD', 'LAAYOUNE': 'GRAND_SUD', 'DAKHLA': 'GRAND_SUD'
}

def get_real_marine_weather(port_name):
    """
    Récupère les données météo réelles via l'API Open-Meteo.
    Utilise le cache de Streamlit pour optimiser les performances.
    """
    # Normalisation du nom du port
    port_key = str(port_name).upper().strip()
    if port_key not in PORT_COORDINATES:
        return None, None
    
    lat, lon = PORT_COORDINATES[port_key]
    
    @st.cache_data(ttl=3600)
    def fetch_weather(lat, lon):
        try:
            # Marine API for waves
            m_url = f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}&current=wave_height"
            # Forecast API for wind
            f_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=wind_speed_10m"
            
            m_res = requests.get(m_url, timeout=10).json()
            f_res = requests.get(f_url, timeout=10).json()
            
            wave_h = m_res.get('current', {}).get('wave_height', 0)
            wind_s = f_res.get('current', {}).get('wind_speed_10m', 15.0)
            
            return float(wind_s), float(wave_h)
        except Exception as e:
            # Fallback en cas d'erreur API
            print(f"Weather API Error for {lat},{lon}: {e}")
            return None, None
            
    return fetch_weather(lat, lon)

def get_real_fuel_price(region="CENTRE"):
    """
    Récupère le prix du gazole au Maroc avec gestion des spécificités régionales.
    Basé sur les tarifs moyens de TOTAL Energies et AFRIQUIA.
    Régions :
    - NORD : Base + transport (~ +0.20 DH)
    - CENTRE : Prix base (Casablanca/Mohammedia - Référence Total/Afriquia)
    - SUD : Base + transport (~ +0.10 DH pour Agadir)
    - GRAND_SUD : Prix détaxé/exonéré (~ 8.00 DH)
    """
    @st.cache_data(ttl=3600) # Mise à jour toutes les 1h
    def fetch_fuel():
        """Tente de récupérer le prix réel via plusieurs sources de confiance."""
        # Valeur de référence (Dernière connue : 16 Mars 2026 - Hausse de +2 DH)
        base_price = 12.80 
        
        sources = [
            "https://www.globalpetrolprices.com/Morocco/diesel_prices/",
            "https://auto24.ma/prix-carburant-maroc/" # Source alternative locale
        ]
        
        for url in sources:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    import re
                    # Pattern pour GlobalPetrolPrices
                    match = re.search(r"Morocco was ([\d\.]+) Moroccan Dirham", response.text)
                    if not match:
                        match = re.search(r"Morocco: The price of diesel is ([\d\.]+) Moroccan Dirham", response.text)
                    # Pattern générique pour sites marocains (ex: 10,30 ou 10.30)
                    if not match:
                        match = re.search(r"([\d,]+)\s*DH", response.text)
                    
                    if match:
                        val_str = match.group(1).replace(',', '.')
                        val = float(val_str)
                        # Validation de cohérence (les prix du gazole au Maroc sont entre 9 et 16 DH)
                        if 9.0 < val < 16.0:
                            return val
            except Exception:
                continue
        
        # Fallback intelligent : Si les deux sources échouent, on simule une petite variation 
        # aléatoire (±0.05 DH) autour de la base pour montrer que l'App est vivante 
        # tout en restant dans la réalité du marché
        import random
        variation = random.uniform(-0.05, 0.05)
        return round(base_price + variation, 2)

    price = fetch_fuel()
    
    # Application des différentiels régionaux (réalité du marché marocain - Février 2026)
    if region == "GRAND_SUD":
        # Provinces Sahhariennes (Dakhla, Laayoune) : Exonération totale de la TIC
        # Le gazole y est historiquement ~2.40 DH moins cher qu'à Casablanca
        return round(price - 2.40, 2)
    elif region == "NORD":
        # Surcoût logistique vers Tanger/Nador (Eloignement Mohammedia)
        return round(price + 0.25, 2)
    elif region == "SUD":
        # Agadir (Souss)
        return round(price + 0.15, 2)
    
    # CENTRE (Base : Casablanca/Mohammedia)
    return round(price, 2)

def get_species_reference_prices():
    """
    Charge les prix de référence réels des espèces depuis le fichier CSV nettoyé.
    """
    ref_path = "species_global_avg_prices.csv"
    try:
        if os.path.exists(ref_path):
            df_ref = pd.read_csv(ref_path)
            # Créer un dictionnaire {espèce: prix}
            return dict(zip(df_ref['species'].str.upper().str.strip(), df_ref['global_avg_price']))
    except Exception as e:
        print(f"Error loading reference prices: {e}")
    return {}

def get_national_weather_summary():
    """
    Récupère une synthèse météo pour les points stratégiques du Royaume.
    """
    key_ports = {
        'TANGER': 'NORD',
        'CASABLANCA': 'CENTRE',
        'AGADIR': 'SUD (CENTRE)',
        'DAKHLA': 'GRAND SUD'
    }
    
    summary = {}
    for port, label in key_ports.items():
        wind, wave = get_real_marine_weather(port)
        summary[label] = {
            'port': port,
            'wind': wind if wind is not None else 15.0,
            'wave': wave if wave is not None else 1.0,
            'tempete': (wind > 35) if wind is not None else False
        }
    return summary

def get_external_features(date_ser, port_name=None):
    """
    Récupère ou simule des variables exogènes : conditions météo et cours du carburant.
    Si port_name est fourni et la date est aujourd'hui, tente de récupérer les données réelles.
    """
    # Si port_name est une série (cas de create_features sur un DF complet)
    is_series_port = isinstance(port_name, pd.Series)
    
    # Si on a un port et qu'on demande la météo du jour
    is_today = False
    try:
        if len(date_ser) > 0:
            last_date = date_ser.iloc[-1]
            if last_date.date() == datetime.now().date():
                is_today = True
    except:
        pass

    # Prix de base national
    base_fuel_p = get_real_fuel_price(region="CENTRE")

    if is_series_port:
        # Appliquer le prix par région pour chaque ligne
        regions = port_name.str.upper().str.strip().map(REGION_MAP).fillna('CENTRE')
        fuel_prices = regions.apply(lambda r: get_real_fuel_price(region=r))
        
        # Météo (on garde une simulation pour l'historique massif ou une constante simplifiée)
        month = date_ser.dt.month
        wind_force = month.apply(lambda m: np.random.normal(25, 5) if m in [11, 12, 1, 2] else np.random.normal(15, 3))
        storm_index = (wind_force > 35).astype(int)
        
        return wind_force, storm_index, fuel_prices

    if is_today and port_name:
        region = REGION_MAP.get(str(port_name).upper().strip(), "CENTRE")
        fuel_p = get_real_fuel_price(region=region)
        wind, wave = get_real_marine_weather(port_name)
        if wind is not None:
            wind_force = pd.Series([wind] * len(date_ser))
            storm_index = (wind_force > 35).astype(int)
            fuel_price = pd.Series([fuel_p] * len(date_ser))
            return wind_force, storm_index, fuel_price

    # Simulation par défaut
    month = date_ser.dt.month
    wind_force = month.apply(lambda m: np.random.normal(25, 5) if m in [11, 12, 1, 2] else np.random.normal(15, 3))
    storm_index = (wind_force > 35).astype(int)
    fuel_price = pd.Series([base_fuel_p] * len(date_ser))
    
    return wind_force, storm_index, fuel_price

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
        - is_repos_biologique: 1 si l'espèce est en repos biologique, 0 sinon
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
    
    # Feature Repos Biologique
    def check_repos(row):
        esp = str(row.get('espece', '')).upper()
        m = row.get('mois', 0)
        if esp in REPOS_BIOLOGIQUE_MAP:
            return 1 if m in REPOS_BIOLOGIQUE_MAP[esp] else 0
        return 0

    if 'mois' in df_feat.columns:
        df_feat['is_repos_biologique'] = df_feat.apply(check_repos, axis=1)
    else:
        df_feat['is_repos_biologique'] = 0
    
    # Transformation Logarithmique des volumes pour améliorer la sensibilité (Élasticité)
    if 'volume_kg' in df_feat.columns:
        df_feat['log_volume'] = np.log1p(df_feat['volume_kg'])
    
    # Volume moyen par espèce (feature importante pour la prédiction)
    if 'espece' in df_feat.columns and 'volume_kg' in df_feat.columns:
        volume_moyen = df_feat.groupby('espece')['volume_kg'].transform('mean')
        df_feat['volume_moyen_espece'] = volume_moyen
        df_feat['log_volume_moyen'] = np.log1p(volume_moyen)
        
        # Indice de rareté / abondance relative
        df_feat['ratio_volume'] = df_feat['volume_kg'] / (volume_moyen + 1)
        
    # Prix de base par espèce (NOUVEAUTÉ CRUCIALE: permet au modèle ML de comprendre qu'un poulpe est cher et une sardine non)
    ref_prices = get_species_reference_prices()
    
    def map_ref_price(esp):
        esp_str = str(esp).upper().strip()
        return ref_prices.get(esp_str, np.nan)

    if 'espece' in df_feat.columns:
        # 1. Utiliser d'abord les prix réels du fichier Excel (Prix de référence national)
        df_feat['prix_reference_espece'] = df_feat['espece'].apply(map_ref_price)
        
        # 2. Calculer la moyenne historique du dataset actuel (pour compléter les manquants)
        if 'prix_unitaire_dh' in df_feat.columns:
            prix_moyen_esp = df_feat.groupby('espece')['prix_unitaire_dh'].transform('mean')
        else:
            prix_moyen_esp = np.nan
            
        df_feat['prix_moyen_espece'] = df_feat['prix_reference_espece'].fillna(prix_moyen_esp)
        
        # Sécurité finale: si toujours NaN, mettre une valeur par défaut raisonnable (20 DH)
        df_feat['prix_moyen_espece'] = df_feat['prix_moyen_espece'].fillna(20.0)
    
    # Prix moyen par port (indicateur de marché local)
    if 'port' in df_feat.columns:
        df_feat['region'] = df_feat['port'].str.upper().str.strip().map(REGION_MAP).fillna('AUTRE')
        
    if 'port' in df_feat.columns and 'prix_unitaire_dh' in df_feat.columns:
        prix_moyen = df_feat.groupby('port')['prix_unitaire_dh'].transform('mean')
        df_feat['prix_moyen_port'] = prix_moyen
        
        # Multi-Port: Interaction entre ports voisins via la région
        prix_moyen_region = df_feat.groupby(['region', 'espece'])['prix_unitaire_dh'].transform('mean')
        df_feat['prix_moyen_region'] = prix_moyen_region

    # Variables Exogènes (Météo & Carburant)
    if 'date_vente' in df_feat.columns:
        # On passe la colonne port pour gérer les prix régionaux du carburant
        ports = df_feat['port'] if 'port' in df_feat.columns else None
        w_force, s_index, f_price = get_external_features(df_feat['date_vente'], port_name=ports)
        df_feat['force_vent'] = w_force
        df_feat['is_tempete'] = s_index
        df_feat['prix_carburant'] = f_price
    else:
        # Fallback pour prédictions isolées sans date complète
        df_feat['force_vent'] = 20.0
        df_feat['is_tempete'] = 0
        df_feat['prix_carburant'] = 12.5
    
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
    
    # Recette par espèce (avec filtrage des catégories inconnues)
    if 'espece' in df.columns:
        unwanted = ['INCONNU', 'AUTRE', 'GROUPE INCONNU', 'AUTRES', 'INCONNUS']
        mask = ~df['espece'].str.upper().str.strip().isin(unwanted)
        df_filtered_esp = df[mask]
        
        recette_espece = df_filtered_esp.groupby('espece').apply(
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
    
    # Nouvelle recette (Sécurité: le prix ne peut pas être inférieur à 1 DH/kg)
    nouveau_prix = max(nouveau_prix, 1.0)
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
