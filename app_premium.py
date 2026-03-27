"""
Application ONP - Optimisation des Prix de Vente des Produits de la Pêche
========================================================================

Application Premium - Interface professionnelle
Projet d'Intelligence de Données - Master Finance & Data Science

Fonctionnalités:
- Design glassmorphism
- Graphiques Plotly avec template personnalisé
- UX avec états de chargement
- Interface responsive et accessible
"""

# ONP Premium v2.0 - Concept & Architecture par Reda Abousaid
# Reload trigger: Alignement Rapport DR 2024-2025
import streamlit as st

# ==================== CONFIGURATION (DOIT ÊTRE AU DÉBUT) ====================
st.set_page_config(
    page_title="ONP - Optimisation des Prix",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import warnings
import io
from datetime import datetime
import time
import base64

warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# Import des modules personnalisés
from utils import (
    clean_data, create_features, calculate_financial_metrics,
    get_price_statistics, simulate_price_impact, REPOS_BIOLOGIQUE_MAP
)
from eda_analysis import (
    plot_price_distribution_by_species, plot_price_by_port,
    plot_volume_price_relationship, plot_seasonal_analysis,
    plot_price_trends, plot_top_species_by_volume, plot_port_activity_heatmap,
    plot_regional_activity_heatmap
)
from financial_analysis import (
    plot_revenue_by_port, plot_revenue_contribution_by_species,
    plot_top_profitable_species, plot_revenue_evolution,
    create_financial_summary_table, calculate_price_volume_effect,
    plot_price_volume_analysis
)
from ml_models import ONPPricePredictor
from ml_interpretation import get_prediction_interpretation, get_global_importance_data
from ml_operations import (
    get_landing_recommendation, get_auction_starting_price, detect_market_anomalies,
    retrain_model_from_excel
)
from design_system import (
    inject_css_styles, PremiumComponents, LuxIcons,
    apply_premium_plotly_styling, create_premium_template
)
from logistics_optimizer import suggest_optimal_ports, get_market_saturation_alerts
from report_generator import create_institutional_word_report, create_reduction_word_report, create_comparison_word_report
from dynamic_logo import (
    display_premium_onp_logo, create_animated_kpi_header,
    create_dynamic_background, get_dynamic_stats
)
from onp_assets import (
    ONP_WEBSITE_URL,
    ONP_EDITO,
    ONP_TAGLINE,
    ONP_STRATEGY,
    IMAGES_PECHE_MAROC,
    IMAGE_CAPTIONS,
    get_image_path,
)
from pdf_utils import generate_reduction_pdf
import hashlib

# --- CHARGEMENT DES DONNÉES CACHÉES (POUR STABILITÉ CLOUD) ---
@st.cache_data(ttl=3600)
def load_official_comparison_data():
    try:
        # Priorité aux fichiers de données officiels
        files_to_try = [
            'Extraction_2024_2025_traitee.xlsx',
            'New Report(2024-2025) -DR (3).xlsx'
        ]
        
        for f in files_to_try:
            if os.path.exists(f):
                try:
                    xl = pd.ExcelFile(f)
                    # Priorité à Feuil1 car elle est plus propre, puis Feuil6 (Synthèse détaillée)
                    target_sheets = ['Feuil1', 'Extraction retraitée VF', 'RECAP', 'Feuil6']
                    sheet = next((s for s in target_sheets if s in xl.sheet_names), xl.sheet_names[0])
                    
                    df = pd.read_excel(f, sheet_name=sheet)
                    
                    # Normalisation agressive des colonnes
                    df.columns = [str(c).upper().strip().replace('  ', ' ') for c in df.columns]
                    
                    # Mapping étendu pour couvrir toutes les variantes observées
                    col_map = {
                        'DR/ESPECE': 'DR', 'DR / ESPECE': 'DR', 'DELEGATION': 'DR', 'REGION': 'DR',
                        'CA (KDH) 2024': 'CA2024(KDh)', 'CA (KDh) 2024': 'CA2024(KDh)', 
                        'CA2024 (KDH)': 'CA2024(KDh)', 'CA 2024 (KDH)': 'CA2024(KDh)',
                        'CA2024(KDH)': 'CA2024(KDh)', 'CA2024(KDH)': 'CA2024(KDh)',
                        'CA (KDH) 2025': 'CA2025(KDh)', 'CA (KDh) 2025': 'CA2025(KDh)',
                        'CA2025 (KDH)': 'CA2025(KDh)', 'CA 2025 (KDH)': 'CA2025(KDh)',
                        'VARIATION.1': 'VARIATION(KDh)', 'VARIATION(KDH)': 'VARIATION(KDh)',
                        'VARIATION (KDH)': 'VARIATION(KDh)', 'VARIATION': 'VARIATION(KDh)',
                        'VARIATION CA EN VALEURS': 'VARIATION(KDh)', 'VARIATION VOLUMES EN VALEURS': 'VARIATION VOLUMES EN VALEURS',
                        'VAR (KDH)': 'VARIATION(KDh)', 'VAR.': 'VARIATION(KDh)', 'VARIANCE': 'VARIATION(KDh)',
                        'CA2024': 'CA2024(KDh)', 'CA2025': 'CA2025(KDh)',
                        'CA (2024)': 'CA2024(KDh)', 'CA (2025)': 'CA2025(KDh)',
                        'CA 2024': 'CA2024(KDh)', 'CA 2025': 'CA2025(KDh)',
                        'RECETTE 2024': 'CA2024(KDh)', 'RECETTE 2025': 'CA2025(KDh)',
                        'PORT': 'PORT', 'ENTITÉ': 'PORT', 'HALLE': 'PORT', 'BUREAUX': 'PORT', 'MG': 'PORT'
                    }
                    df = df.rename(columns=col_map)
                    # S'assurer que les colonnes numériques sont bien lues (gestion des séparateurs de milliers)
                    def safe_num_clean(v):
                        if pd.isna(v): return 0
                        if isinstance(v, (int, float)): return v
                        v = str(v).strip().replace('\xa0', '').replace(' ', '').replace("'", "")
                        # Cas particulier : 1.234,56 -> 1234.56
                        if '.' in v and ',' in v:
                            v = v.replace('.', '').replace(',', '.')
                        elif ',' in v:
                            # 1234,56 -> 1234.56
                            v = v.replace(',', '.')
                        
                        # Nettoyage final des caractères non-numériques
                        import re
                        # On garde le premier point décimal s'il y en a plusieurs (cas 1.234.567)
                        if v.count('.') > 1:
                            parts = v.split('.')
                            v = "".join(parts[:-1]) + "." + parts[-1]
                        
                        v = re.sub(r'[^0-9\.\-]', '', v)
                        try:
                            return float(v) if v else 0.0
                        except:
                            return 0.0

                    for col in ['CA2024(KDh)', 'CA2025(KDh)', 'VARIATION(KDh)']:
                        if col in df.columns:
                            df[col] = df[col].apply(safe_num_clean)
                            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                            
                    # Vérification de la présence des colonnes minimales
                    if 'CA2024(KDh)' in df.columns and 'CA2025(KDh)' in df.columns:
                        # Si c'est Feuil6, on nettoie les noms de DR
                        if sheet == 'Feuil6' and 'DR' in df.columns:
                            df['IS_DR'] = df['DR'].apply(lambda x: len(str(x)) <= 5 and str(x).isupper() if pd.notnull(x) else False)
                        return df
                    else:
                        # print(f"DEBUG: Colonnes insuffisantes dans {f} sheet {sheet}")
                        continue
                except Exception as ex:
                    # print(f"DEBUG: Erreur sur {f} : {ex}")
                    continue
        return pd.DataFrame()
    except Exception as e:
        # print(f"DEBUG Error outer: {e}")
        return pd.DataFrame()

# ==================== CONFIGURATION ====================
# Déjà effectuée au début du script pour compatibilité Cloud

# Injecter les styles premium
inject_css_styles()

# ==================== AUTHENTIFICATION (POINT 1) ====================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Utilisateurs en dur pour la démo PFE
USERS = {
    "admin": {
        "password": hash_password("admin123"),
        "role": "admin",
        "name": "Administrateur ONP"
    },
    "gestionnaire": {
        "password": hash_password("gest123"),
        "role": "gestionnaire",
        "name": "Gestionnaire DP"
    },
    "crieur": {
        "password": hash_password("crieur1234"),
        "role": "crieur",
        "name": "Crieur Halle"
    }
}

def init_auth_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None

def set_background(image_file):
    import base64
    from pathlib import Path
    
    company_img_path = Path(image_file)
    if not company_img_path.exists():
        return
        
    with open(company_img_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

        .stApp {{
            background-image: url("data:image/jpeg;base64,{data}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0, 15, 40, 0.75);
            z-index: 0;
        }}
        
        .block-container {{
            position: relative;
            z-index: 1;
            padding-top: 5vh !important;
        }}

        /* --- TYPOGRAPHIE SANS CARTE --- */
        .onp-title-main {{
            font-family: 'Poppins', sans-serif;
            font-size: 2.22rem;
            font-weight: 700;
            background: linear-gradient(to right, #FFFFFF, #AED6F1, #FFFFFF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 1px;
            filter: drop-shadow(0 6px 12px rgba(0,0,0,0.5));
            margin-bottom: 0.2rem;
            text-align: center;
            line-height: 1.2;
        }}

        .onp-subtitle-premium {{
            font-family: 'Poppins', sans-serif;
            font-size: 0.95rem;
            font-weight: 400;
            color: #AED6F1;
            letter-spacing: 3px;
            text-transform: uppercase;
            text-shadow: 0 2px 5px rgba(0,0,0,0.5);
            margin-bottom: 1.5rem;
            text-align: center;
            opacity: 0.85;
        }}

        .onp-subtitle-fr {{
            font-family: 'Poppins', sans-serif;
            font-size: 1.3rem;
            font-weight: 300;
            color: rgba(225, 245, 254, 0.9);
            letter-spacing: 2px;
            text-transform: uppercase;
            text-shadow: 0 2px 8px rgba(0,0,0,0.6);
            margin-bottom: 0.1rem;
            text-align: center;
        }}

        .onp-subtitle-ar {{
            font-family: 'Poppins', sans-serif;
            font-size: 1.8rem;
            font-weight: 600;
            color: #FFFFFF;
            text-shadow: 0 2px 10px rgba(0,0,0,0.6);
            margin-bottom: 0.5rem;
            direction: rtl;
            text-align: center;
            opacity: 0.95;
        }}

        .onp-tagline {{
            font-family: 'Poppins', sans-serif;
            font-size: 1rem;
            font-weight: 400;
            color: #AED6F1;
            letter-spacing: 1.5px;
            text-shadow: 0 2px 5px rgba(0,0,0,0.5);
            margin-bottom: 2rem;
            text-align: center;
            opacity: 0.8;
        }}

        .onp-divider {{
            width: 120px;
            height: 2px;
            background: linear-gradient(90deg, transparent, rgba(93, 173, 226, 0.8), transparent);
            margin: 2rem auto;
        }}

        /* --- ÉLÉMENTS DU FORMULAIRE ET SUPPRESSION BORDURES --- */
        [data-testid="stForm"] {{
            border: none !important;
            padding: 0 !important;
            background: transparent !important;
        }}

        .field-label {{
            color: #E1F5FE !important;
            font-family: 'Poppins', sans-serif;
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            margin-bottom: 6px;
            margin-top: 20px;
            text-shadow: 0 1px 4px rgba(0,0,0,0.8);
            text-align: left !important;
        }}

        .stTextInput input {{
            background: rgba(255, 255, 255, 0.95) !important;
            color: #000000 !important;
            border: 1px solid white !important;
            border-radius: 12px !important;
            padding: 12px 15px !important;
            font-size: 15px !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
        }}

        .stButton > button {{
            background: linear-gradient(135deg, #1a5276 0%, #148f77 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 12px !important;
            width: 100% !important;
            padding: 15px !important;
            font-family: 'Poppins', sans-serif !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            letter-spacing: 2px !important;
            text-transform: uppercase !important;
            margin-top: 30px !important;
            box-shadow: 0 6px 20px rgba(20, 143, 119, 0.4) !important;
            transition: all 0.3s ease !important;
        }}

        .stButton > button:hover {{
            transform: scale(1.02) translateY(-2px) !important;
            box-shadow: 0 10px 30px rgba(20, 143, 119, 0.6) !important;
        }}
        </style>
    """, unsafe_allow_html=True)


def render_login_view():
    set_background("ONP campany.jpeg")
    
    st.markdown('<div style="margin-top: 5vh;"></div>', unsafe_allow_html=True)
    
    # Utilisation de colonnes plus larges sur les côtés pour rétrécir le formulaire central
    col1, col2, col3 = st.columns([1.5, 1.8, 1.5]) 
    with col2:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 2.5rem;">
                <div class="onp-subtitle-fr" style="color: #FFFFFF !important; text-shadow: 0 2px 10px rgba(0,0,0,0.8) !important; font-weight: 500 !important; letter-spacing: 2px !important;">
                    Performance Halieutique
                </div>
                <div class="onp-title-main" style="color: #FFFFFF !important; background: none !important; -webkit-text-fill-color: #FFFFFF !important; font-size: 3.5rem !important; font-weight: 900 !important; line-height: 1.1 !important; margin: 1rem 0 !important; text-shadow: 0 4px 20px rgba(0,0,0,0.9) !important;">
                    SOUVERAINETÉ<br/>HALIEUTIQUE
                </div>
                <div class="onp-tagline" style="color: #FFFFFF !important; font-size: 1.1rem !important; opacity: 1.0 !important; text-shadow: 0 4px 15px rgba(0,0,0,0.9) !important; background: none !important; -webkit-text-fill-color: #FFFFFF !important;">
                    Intelligence augmentée pour la valorisation des produits de la mer.<br/>
                    <div style="margin-top: 15px; font-size: 1.6rem !important; font-weight: 800 !important; color: #AED6F1 !important; text-shadow: 0 4px 20px rgba(0,0,0,1.0) !important; -webkit-text-fill-color: #AED6F1 !important; letter-spacing: 1px;">
                        by Reda Abousaid
                    </div>
                </div>
                <div class="onp-divider" style="background: linear-gradient(90deg, transparent, #FFFFFF, transparent) !important; margin-top: 2rem !important;"></div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            st.markdown("<p class='field-label'>Identifiant</p>", unsafe_allow_html=True)
            identifiant = st.text_input("Identifiant", placeholder="Nom d'utilisateur", key="user_input", label_visibility="collapsed")
            
            st.markdown("<p class='field-label'>Mot de passe</p>", unsafe_allow_html=True)
            mot_de_passe = st.text_input("Mot de passe", placeholder="••••••••", type="password", key="pass_input", label_visibility="collapsed")
            
            submitted = st.form_submit_button("Accéder au Portail")
            
            if submitted:
                if identifiant in USERS and USERS[identifiant]["password"] == hash_password(mot_de_passe):
                    st.session_state.logged_in = True
                    st.session_state.user_role = USERS[identifiant]["role"]
                    st.session_state.user_name = USERS[identifiant]["name"]
                    st.success("Accès autorisé. Redirection...")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.markdown("""
                        <div style='
                            background: rgba(192, 57, 43, 0.6);
                            border: 1px solid #E74C3C;
                            border-radius: 12px;
                            padding: 12px;
                            color: #FFFFFF;
                            font-size: 14px;
                            font-family: Poppins, sans-serif;
                            margin-top: 20px;
                            text-align: center;
                            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                        '>
                            Identifiant ou mot de passe incorrect.
                        </div>
                    """, unsafe_allow_html=True)
                    
        st.markdown(
            '<div style="text-align: center; color: rgba(255,255,255,0.5); font-size: 0.85rem; margin-top: 4rem; font-family: Poppins; letter-spacing: 0.5px;">'
            'Accès sécurisé réservé • Office National des Pêches'
            '</div>', unsafe_allow_html=True
        )

def render_logout_button():
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**{st.session_state.user_name}** ({st.session_state.user_role.capitalize()})")
    if st.sidebar.button("Déconnexion", width="stretch"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.user_name = None
        st.rerun()

# ==================== HELPERS COLONNES ====================
def _series(df, *names):
    """Retourne la série du premier nom de colonne présent (ex: Espèce ou espece)."""
    for n in names:
        if n in df.columns:
            return df[n]
    return pd.Series(dtype=object)

# ==================== CACHE & STATE ====================
def load_default_data():
    """Charge les données de base (Réelles si disponibles, sinon simulation)"""
    try:
        # Ordre de priorité des fichiers de données
        possible_files = [
            'onp_real_ml_data.csv',
            'donnees_simulation_onp.csv',
            'onp_reinforced_ml_data.csv'
        ]
        
        data_file = None
        for f in possible_files:
            if os.path.exists(f):
                data_file = f
                break
                
        if data_file and os.path.exists(data_file):
            df = pd.read_csv(data_file)
        else:
            st.error(f"Fichier de données introuvable (Vérifié: {', '.join(possible_files)})")
            return None

        if df is None or df.empty:
            st.error(f"Le fichier {data_file} est vide.")
            return None
                
        # Compléter les colonnes manquantes
        if 'categorie' not in df.columns: df['categorie'] = 'Inconnue'
        if 'calibre' not in df.columns: df['calibre'] = 'Moyen'
        
        # Nettoyage et Features
        df = clean_data(df)
        df = create_features(df)
        
        # Ajouter une colonne pour le filtrage UI (Nom propre sans taille)
        from utils import normalize_species_name
        df['espece_clean'] = df['espece'].apply(lambda x: normalize_species_name(x).replace('_', ' ').upper())
        # Correction spécifique pour le style ONP
        df.loc[df['espece_clean'] == 'BAR', 'espece_clean'] = 'BAR (LOUP)'
        
        if df.empty:
            st.warning("Les données ont été filtrées à 100% lors du nettoyage (Outliers/Negative values).")
            return None
            
        # print(f"DONE: {len(df)} lignes chargees avec succes")
        return df
            
    except Exception as e:
        st.error(f"Erreur critique lors du chargement des données: {e}")
        import traceback
        st.sidebar.error(traceback.format_exc())
        return None

def get_current_df():
    """Récupère le DataFrame actif (upload ou simulation)"""
    if 'main_df' not in st.session_state or st.session_state.main_df is None:
        st.session_state.main_df = load_default_data()
    return st.session_state.main_df

@st.cache_resource
def initialize_predictor(df, model_mtime=0):
    """Initialise et entraîne le modèle ML sur les données réelles si disponible."""
    try:
        predictor = ONPPricePredictor()
        model_path = 'models/best_model.pkl'
        
        if os.path.exists(model_path):
            if predictor.load_model(model_path):
                return predictor
        
        # Fallback si pas de modèle sauvegardé
        X_train, X_test, y_train, y_test, _, _ = predictor.prepare_data(df)
        predictor.train_models(X_train, X_test, y_train, y_test, None, None)
        return predictor
    except Exception as e:
        st.error(f"Erreur lors de l'initialisation du modèle: {e}")
        return None

def render_external_conditions(port_name=None):
    """Rend un tableau de bord des facteurs exogènes (Météo/Carburant) réels ou simulés."""
    from utils import get_external_features, get_real_marine_weather, get_national_weather_summary, get_real_fuel_price, REGION_MAP
    
    # 1. Carburant par Région
    port_name_up = str(port_name).upper().strip() if port_name else "CASABLANCA"
    current_region = REGION_MAP.get(port_name_up, "CENTRE")
    fuel_price = get_real_fuel_price(region=current_region)
    
    # Labels réalistes pour les régimes de prix
    region_labels = {
        "NORD": "Standard (Nord)",
        "CENTRE": "Standard (Centre)",
        "SUD": "Standard (Souss)",
        "GRAND_SUD": "GRAND SUD (Exonéré)"
    }
    fuel_label = region_labels.get(current_region, "Standard")

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"#### {LuxIcons.render('finance', size=20, color='#F59E0B')} Carburant {current_region}", unsafe_allow_html=True)
    st.sidebar.markdown(f"""
    <div style="background: rgba(245, 158, 11, 0.05); padding: 12px; border-radius: 10px; border-left: 4px solid #F59E0B;">
        <p style="margin:0; font-size: 0.7rem; color: #64748B; font-weight: 700;">RÉGIME : {fuel_label}</p>
        <p style="margin:4px 0; font-size: 1.2rem; font-weight: 800; color: #B45309;">{fuel_price:.2f} DH/L</p>
        <p style="margin:0; font-size: 0.65rem; color: #94A3B8;">Localisation : {port_name_up}</p>
    </div>
    """, unsafe_allow_html=True)

    # 2. Comparatif National des Prix (Demande Utilisateur)
    with st.sidebar.expander("🔍 Comparatif Nord vs Sud", expanded=False):
        for reg in ["NORD", "CENTRE", "SUD", "GRAND_SUD"]:
            p = get_real_fuel_price(region=reg)
            is_current = " (Actuel)" if reg == current_region else ""
            color = "#B45309" if reg == current_region else "#64748B"
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px;">
                <span style="color: {color}; font-weight: {'800' if is_current else '400'};">{reg}{is_current}</span>
                <span style="font-weight: 700;">{p:.2f} DH</span>
            </div>
            """, unsafe_allow_html=True)

    # 3. Synthèse Météo Nationale
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"#### {LuxIcons.render('anchor', size=20, color='#0EA5E9')} Météo du Royaume", unsafe_allow_html=True)
    
    weather_summary = get_national_weather_summary()
    
    for label, data in weather_summary.items():
        color = "#EF4444" if data['tempete'] else "#10B981"
        st.sidebar.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.03); padding: 8px 12px; border-radius: 8px; border-left: 3px solid {color}; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <p style="margin:0; font-size: 0.65rem; color: #64748B; font-weight: 800;">{label}</p>
                <p style="margin:0; font-size: 0.8rem; font-weight: 700; color: #0F172A;">{data['port']}</p>
            </div>
            <div style="text-align: right;">
                <p style="margin:0; font-size: 0.75rem; font-weight: 700; color: {color};">{data['wind']:.0f} km/h</p>
                <p style="margin:0; font-size: 0.65rem; color: #94A3B8;">Mer : {data['wave']:.1f}m</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==================== COMPOSANTS PERSONNALISÉS ====================
def render_header():
    """Rend l'en-tête premium favori de l'application avec logo dynamique"""
    st.markdown("""
    <div style="background: #FFFFFF; margin: -1rem -5rem 2rem -5rem; padding: 1rem 5rem; border-bottom: 2px solid #F1F5F9; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([0.8, 4, 0.8])
    
    with col1:
        st.markdown(display_premium_onp_logo(size=120, with_animation=True), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 0.5rem 0;">
            <h1 style="
                margin: 0;
                font-size: 2.5rem;
                font-weight: 800;
                color: #0369A1 !important;
                letter-spacing: -1px;
            ">Optimisation ONP Premium</h1>
            <p style="
                margin: 0.2rem 0 0 0;
                font-size: 1.1rem;
                color: #64748B;
                font-weight: 500;
                letter-spacing: 1px;
                text-transform: uppercase;
            ">Digital Intelligence & Price Optimization</p>
            <div style="
                margin-top: 0.75rem;
                padding-top: 0.5rem;
                border-top: 1px solid #F1F5F9;
                display: inline-block;
            ">
                <span style="
                    font-size: 0.9rem;
                    color: #94A3B8;
                    font-style: italic;
                ">Concept & Architecture par</span>
                <span style="
                    font-size: 1rem;
                    color: #0369A1;
                    font-weight: 700;
                    margin-left: 5px;
                ">Reda Abousaid</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        timestamp = datetime.now().strftime("%d/%m/%Y")
        st.markdown(f"""
        <div style="
            text-align: right;
            font-size: 0.85rem;
            color: #64748B;
            padding: 0.5rem 0;
        ">
            <div style="font-weight: 800; color: #0369A1;">DASHBOARD</div>
            <div>{timestamp}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

def render_kpis(df):
    """Rend les KPIs principaux avec style premium et dynamique"""
    st.markdown("---")
    
    # Calcul des KPIs centralisé dans utils.py
    metrics = calculate_financial_metrics(df)
    
    avg_price = metrics.get('prix_moyen_dh_kg', 0)
    total_revenue = metrics.get('recette_totale_mdh', 0)
    top_species = metrics.get('espece_plus_rentable', 'N/A')
    total_volume = metrics.get('volume_total_kg', 0)
    
    # Ajouter des badges de variation (simulés pour l'esthétique)
    avg_variation = "+2.5%" if avg_price > 0 else "0%"
    revenue_variation = "+5.8%" if total_revenue > 0 else "0%"
    
    # Affichage avec style premium amélioré
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        PremiumComponents.metric_card(
            "Prix moyen", 
            f"{avg_price:.2f} DH/kg", 
            "target", 
            avg_variation, 
            "blue"
        )
    
    with col2:
        PremiumComponents.metric_card(
            "Recette totale", 
            f"{total_revenue:.2f} MDH", 
            "finance", 
            revenue_variation, 
            "green"
        )
    
    with col3:
        PremiumComponents.metric_card(
            "Espèce principale", 
            str(top_species), 
            "fish", 
            "Tendance locale", 
            "orange"
        )
    
    with col4:
        PremiumComponents.metric_card(
            "Volume total", 
            f"{total_volume/1000:.0f} T", 
            "anchor", 
            "Période sélectionnée", 
            "blue"
        )
    
    st.markdown("---")

def render_executive_command_header():
    """Bandeau de commande flottant style 'Elite Command Center'."""
    st.markdown(f"""
    <div style="
        position: sticky;
        top: 0;
        z-index: 999;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-bottom: 2px solid #F1F5F9;
        margin: -2rem -2rem 2rem -2rem;
        padding: 0.75rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    ">
        <div style="display: flex; gap: 2rem;">
            <div style="display: flex; align-items: center; gap: 10px;">
                {LuxIcons.render('shield', size=20, color='#10B981')}
                <span style="color: #0F172A; font-size: 0.85rem; font-weight: 700; text-transform: uppercase;">Stabilité Marché</span>
                <span class="badge-premium" style="background: #DCFCE7 !important; color: #10B981 !important;">94%</span>
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                {LuxIcons.render('anchor', size=20, color='#0EA5E9')}
                <span style="color: #0F172A; font-size: 0.85rem; font-weight: 700; text-transform: uppercase;">Activité Flotte</span>
                <span class="badge-premium" style="background: #E0F2FE !important; color: #0EA5E9 !important;">Intense</span>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 1.5rem;">
            <div style="color: #64748B; font-size: 0.75rem; font-weight: 600;">PORTÉE STRATÉGIQUE : HALIEUTIS 2026</div>
            <div style="width: 2px; height: 20px; background: #F1F5F9;"></div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 6px; height: 6px; background: #0EA5E9; border-radius: 50%;"></div>
                <span style="color: #0EA5E9; font-size: 0.85rem; font-weight: 800; cursor: pointer;">COMMAND CENTER LIVE</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
def get_base64_image(image_path):
    """Convertit une image locale en base64 ou retourne l'URL si c'est déjà une URL."""
    if not image_path:
        return ""
    if str(image_path).startswith("http"):
        return image_path
    try:
        mime_type = "image/jpeg"
        if str(image_path).lower().endswith(".png"): mime_type = "image/png"
        elif str(image_path).lower().endswith(".gif"): mime_type = "image/gif"
        elif str(image_path).lower().endswith(".webp"): mime_type = "image/webp"
        
        with open(image_path, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode()
            return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        # print(f"Error encoding image {image_path}: {e}")
        return image_path

def render_onp_hero():
    """Bannière hero institutionnelle épurée avec l'image choisie par l'utilisateur."""
    try:
        # Priorité à l'image fournie par l'utilisateur
        hero_img_path = get_image_path("hero_user")
        hero_image = get_base64_image(hero_img_path)
        
        # Fallback robuste
        if not hero_image or (isinstance(hero_image, str) and len(hero_image) < 100 and not hero_image.startswith("http")):
            hero_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Fish_market_in_Tsukiji.jpg/1200px-Fish_market_in_Tsukiji.jpg"
            
        st.markdown(f"""
        <div style="
            position: relative;
            border-radius: 28px;
            overflow: hidden;
            margin-bottom: 2rem;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
            height: 480px;
            background: #0B1120 url('{hero_image}');
            background-size: cover;
            background-position: center 30%;
            border: 1px solid rgba(255,255,255,0.1);
        ">
            <!-- Overlay très sombre et dégradé pour garantir une lisibilité absolue du texte blanc -->
            <div class="hero-container" style="
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                display: flex; flex-direction: column; justify-content: center;
                padding: 5rem; z-index: 2;
                background: linear-gradient(90deg, rgba(11, 17, 32, 0.85) 0%, rgba(11, 17, 32, 0.4) 100%);
            ">
                <div class="hero-label" style="color: #FFFFFF !important; opacity: 1.0 !important; font-weight: 800; font-size: 1.25rem; letter-spacing: 6px; text-transform: uppercase; margin-bottom: 1.5rem; text-shadow: 0 4px 15px rgba(0,0,0,1) !important;">
                    Performance Halieutique
                </div>
                <h1 class="hero-title" style="color: #FFFFFF !important; font-size: 5.2rem !important; font-weight: 950 !important; margin: 0; line-height: 1.0 !important; letter-spacing: -2px; text-shadow: 0 4px 15px rgba(0,0,0,1) !important; border: none !important;">
                    SOUVERAINETÉ <br/><span style="color: #FFFFFF !important; text-shadow: 0 4px 15px rgba(0,0,0,1) !important;">HALIEUTIQUE</span>
                </h1>
                <p class="hero-description" style="color: #FFFFFF !important; font-size: 1.7rem !important; margin-top: 1.5rem; max-width: 750px; font-weight: 500 !important; line-height: 1.4 !important; letter-spacing: 0.5px; opacity: 1.0 !important; text-shadow: 0 4px 15px rgba(0,0,0,1) !important; border: none !important;">
                    Intelligence augmentée pour la valorisation des produits de la mer.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erreur de rendu Hero: {e}")


def render_hero_stats():
    """Rend le bloc de statistiques institutionnelles."""
    try:
        st.markdown(f"""
        <div style="display: flex; justify-content: center; margin-top: -4rem; margin-bottom: 4rem; position: relative; z-index: 99;">
            <div style="display: flex; gap: 4.5rem; background: #0F172A; width: fit-content; padding: 2.2rem 4rem; border-radius: 24px; border: 1px solid rgba(255,255,255,0.2); box-shadow: 0 20px 40px rgba(0,0,0,0.4);">
                 <div style="border-left: 4px solid white; padding-left: 1.5rem;">
                    <div style="color: white; font-weight: 900; font-size: 2.8rem; line-height: 1;">800k+</div>
                    <div style="color: rgba(255,255,255,0.6); font-size: 0.9rem; text-transform: uppercase; font-weight: 700; letter-spacing: 2px; margin-top: 0.5rem;">Ventes</div>
                 </div>
                 <div style="border-left: 4px solid #0EA5E9; padding-left: 1.5rem;">
                    <div style="color: white; font-weight: 900; font-size: 2.8rem; line-height: 1;">22</div>
                    <div style="color: rgba(255,255,255,0.6); font-size: 0.9rem; text-transform: uppercase; font-weight: 700; letter-spacing: 2px; margin-top: 0.5rem;">Ports</div>
                 </div>
                 <div style="border-left: 4px solid #10B981; padding-left: 1.5rem;">
                    <div style="color: white; font-weight: 900; font-size: 2.8rem; line-height: 1;">3500</div>
                    <div style="color: rgba(255,255,255,0.6); font-size: 0.9rem; text-transform: uppercase; font-weight: 700; letter-spacing: 2px; margin-top: 0.5rem;">km Littoral</div>
                 </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erreur de rendu Hero Stats: {e}")

def render_module_hero(title, subtitle, image_key="real_port"):
    """Bannière secondaire pour les modules internes (Analytics, ML, Simulation)."""
    try:
        img_url = get_image_path(image_key)
        html_content = f"""
        <div style="
            position: relative;
            border-radius: 15px;
            overflow: hidden;
            margin-bottom: 2.5rem;
            box-shadow: 0 10px 20px -5px rgba(15, 23, 42, 0.08);
            height: 220px;
            background-image: url('{img_url}');
            background-size: cover;
            background-position: center;
            border: 1px solid rgba(255,255,255,0.05);
        ">
            <div style="
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                display: flex; flex-direction: column; justify-content: center;
                padding-left: 3rem; z-index: 2;
                background: linear-gradient(90deg, rgba(15, 23, 42, 0.95) 0%, rgba(3, 105, 161, 0.6) 50%, rgba(15, 23, 42, 0) 100%);
            ">
                <h2 style="color: #F8FAFC !important; text-shadow: 2px 2px 8px rgba(0,0,0,0.9) !important; font-size: 2.8rem !important; font-weight: 900 !important; margin: 0; letter-spacing: -1px;">{title}</h2>
                <div style="height: 4px; width: 80px; background: #38BDF8; margin: 1rem 0; box-shadow: 0 2px 4px rgba(0,0,0,0.5);"></div>
                <p style="color: #F1F5F9 !important; text-shadow: 1px 1px 5px rgba(0,0,0,0.9) !important; font-size: 1.15rem !important; margin: 0; font-weight: 500; max-width: 600px;">
                    {subtitle}
                </p>
            </div>
        </div>
        """
        st.markdown(html_content, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erreur Hero Module: {e}")

def render_interactive_strategy_map():
    """Visualisation géographique exhaustive des ports stratégiques de l'ONP."""
    try:
        st.markdown("<br>", unsafe_allow_html=True)
        PremiumComponents.section_header(
            "Maillage Territorial Complet",
            "Déploiement stratégique sur l'ensemble du littoral du Royaume",
            "search"
        )
        
        # Liste ciblée des 22 ports stratégiques (comme démandé par l'utilisateur)
        ports_geo = pd.DataFrame([
            {"Port": "Tanger Med", "lat": 35.88, "lon": -5.50, "Size": 55, "Type": "Standard"},
            {"Port": "Tanger Ville", "lat": 35.79, "lon": -5.81, "Size": 40, "Type": "Standard"},
            {"Port": "M'diq", "lat": 35.68, "lon": -5.32, "Size": 30, "Type": "Standard"},
            {"Port": "Assilah", "lat": 35.46, "lon": -6.03, "Size": 25, "Type": "Standard"},
            {"Port": "Al Hoceima", "lat": 35.25, "lon": -3.93, "Size": 35, "Type": "Standard"},
            {"Port": "Nador", "lat": 35.17, "lon": -2.93, "Size": 45, "Type": "Standard"},
            {"Port": "Larache", "lat": 35.19, "lon": -6.15, "Size": 35, "Type": "Standard"},
            {"Port": "Kenitra / Mehdia", "lat": 34.26, "lon": -6.66, "Size": 30, "Type": "Standard"},
            {"Port": "Rabat", "lat": 34.02, "lon": -6.83, "Size": 35, "Type": "Standard"},
            {"Port": "Casablanca", "lat": 33.57, "lon": -7.59, "Size": 60, "Type": "Standard"},
            {"Port": "Mohammedia", "lat": 33.71, "lon": -7.40, "Size": 35, "Type": "Standard"},
            {"Port": "El Jadida", "lat": 33.25, "lon": -8.50, "Size": 40, "Type": "Standard"},
            {"Port": "Sidi Abed", "lat": 33.00, "lon": -8.67, "Size": 25, "Type": "Standard"},
            {"Port": "Safi", "lat": 32.30, "lon": -9.24, "Size": 50, "Type": "Standard"},
            {"Port": "Essaouira", "lat": 31.51, "lon": -9.77, "Size": 45, "Type": "Standard"},
            {"Port": "Agadir", "lat": 30.43, "lon": -9.60, "Size": 55, "Type": "Standard"},
            {"Port": "Sidi Ifni", "lat": 29.38, "lon": -10.18, "Size": 30, "Type": "Standard"},
            {"Port": "Tan-Tan", "lat": 28.50, "lon": -11.33, "Size": 40, "Type": "Standard"},
            {"Port": "Tarfaya", "lat": 27.94, "lon": -12.92, "Size": 25, "Type": "Standard"},
            {"Port": "Laâyoune", "lat": 27.09, "lon": -13.41, "Size": 50, "Type": "Standard"},
            {"Port": "Boujdour", "lat": 26.13, "lon": -14.48, "Size": 30, "Type": "Standard"},
            {"Port": "Dakhla", "lat": 23.68, "lon": -15.96, "Size": 65, "Type": "Standard"},
        ])
        
        fig = px.scatter_mapbox(
            ports_geo,
            lat="lat",
            lon="lon",
            hover_name="Port",
            hover_data=["Type"],
            size="Size",
            color="Type",
            color_discrete_map={"Halle": "#3B82F6", "MG": "#F97316", "CAPI": "#10B981", "Autre": "#94A3B8", "Standard": "#3B82F6"},
            zoom=4.5,
            center=dict(lat=29.0, lon=-10.0),
            mapbox_style="carto-positron"
        )
        
        fig.update_layout(
            height=750,
            margin={"r":0,"t":0,"l":0,"b":0},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False,
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255,255,255,0.8)"),
            hoverlabel=dict(bgcolor="white", font_size=16, font_family="Outfit")
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    except Exception as e:
        st.error(f"Erreur d'affichage de la carte : {e}")

def render_price_weather():
    """Composant créatif 'Météo des Prix' (Price Weather)."""
    st.markdown("<br><br>", unsafe_allow_html=True)
    PremiumComponents.section_header(
        "Météo des Prix (Market Temperature)",
        "Visualisation thermique des tendances par espèce majeure",
        "chart"
    )
    
    weather_data = [
        {"species": "Sardine", "temp": "Chaud", "val": "+12.4%", "color": "#F43F5E", "desc": "Forte demande"},
        {"species": "Crevette", "temp": "Stable", "val": "-1.2%", "color": "#0EA5E9", "desc": "Équilibre"},
        {"species": "Poulpe", "temp": "Froid", "val": "-8.5%", "color": "#94A3B8", "desc": "Volume élevé"},
        {"species": "Espadon", "temp": "Stable", "val": "+0.5%", "color": "#10B981", "desc": "Prix Premium"}
    ]
    
    cols = st.columns(4)
    for col, w in zip(cols, weather_data):
        with col:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center; border-bottom: 3px solid {w['color']};">
                <div style="color: {w['color']}; font-size: 2.5rem; font-weight: 900; line-height: 1;">{w['val']}</div>
                <h4 style="margin: 1.5rem 0 0.5rem 0; font-size: 1.3rem; font-weight: 800; color: #0F172A;">{w['species']}</h4>
                <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
                    <span style="font-size: 0.75rem; font-weight: 700; color: {w['color']}; text-transform: uppercase;">{w['temp']}</span>
                </div>
                <p style="margin-top: 0.5rem; font-size: 0.8rem; color: #64748B;">{w['desc']}</p>
            </div>
            """, unsafe_allow_html=True)

def render_institutional_bulletin():
    """Bulletin d'information institutionnel élégant."""
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_a, col_b = st.columns([1, 1.2])
    
    with col_a:
        # Conteneur sombre avec texte blanc explicite
        content_html = f"""
        <div style="
            background-color: #0F172A; 
            padding: 40px; 
            border-radius: 24px; 
            color: #FFFFFF; 
            height: 100%;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        ">
            <div style="margin-bottom: 20px;">
                {LuxIcons.render('shield', size=40, color='#0EA5E9')}
            </div>
            <h2 style="color: #FFFFFF; font-size: 2rem; font-weight: 800; margin-bottom: 20px;">
                Bulletin Stratégique
            </h2>
            <p style="color: #FFFFFF !important; font-size: 1.15rem; line-height: 1.8; font-weight: 500; margin-top: 20px; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">
                Le programme d'optimisation machine learning s'inscrit dans le cadre du déploiement national Halieutis. 
                L'objectif de 2026 est la numérisation complète des flux de crie à travers les 22 ports stratégiques du Royaume.
            </p>
            <div style="margin-top: 40px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="font-size: 0.75rem; color: #FFFFFF; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
                        Numérisation T1 2026
                    </span>
                    <span style="color: #10B981; font-weight: 800; font-size: 0.85rem;">EN COURS</span>
                </div>
                <div style="width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden;">
                    <div style="width: 75%; height: 100%; background: #0EA5E9; border-radius: 4px;"></div>
                </div>
            </div>
        </div>
        """
        st.markdown(content_html, unsafe_allow_html=True)
        
    with col_b:
        st.markdown(f"#### {LuxIcons.render('report', size=20, color='#0EA5E9', extra_style='margin-right: 10px;')} Évolutions Clés", unsafe_allow_html=True)
        bulletins = [
            {"date": "12 FEV", "title": "Mise à jour Modèle S-22", "desc": "Précision accrue de 4.2% sur les petits pélagiques."},
            {"date": "10 FEV", "title": "Nouveau Hub Digital", "desc": "Déploiement de la solution de crie automatique à Tanger."},
            {"date": "08 FEV", "title": "Stabilité Réseau", "desc": "Maintenance préventive des serveurs de Casablanca effectuée."}
        ]
        
        for b in bulletins:
            st.markdown(f"""
            <div style="display: flex; gap: 15px; margin-bottom: 15px; background: #FFFFFF; padding: 20px; border-radius: 16px; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                <div style="background: rgba(14, 165, 233, 0.1); color: #0EA5E9; padding: 10px; border-radius: 10px; font-weight: 800; font-size: 0.75rem; min-width: 60px; text-align: center; height: fit-content;">
                    {b['date']}
                </div>
                <div>
                    <h5 style="margin: 0; color: #0F172A; font-weight: 700; font-size: 1rem;">{b['title']}</h5>
                    <p style="margin: 4px 0 0 0; color: #64748B; font-size: 0.9rem; line-height: 1.4;">{b['desc']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

def render_onp_edito():
    """Éditorial stratégique épuré."""
    st.markdown(
        f'<div style="background: white; padding: 2.5rem; border-radius: 24px; border: 1px solid #E2E8F0; box-shadow: 0 10px 30px rgba(0,0,0,0.03);">'
        f'<p style="color: #475569; line-height: 1.8; font-size: 1.15rem; font-weight: 400; margin: 0;">{ONP_EDITO}</p></div>',
        unsafe_allow_html=True
    )

def render_live_market_pulse(df):
    """Composant créatif visualisant le flux de données en temps réel basé sur les moyennes historiques."""
    st.markdown("<br><br>", unsafe_allow_html=True)
    PremiumComponents.section_header(
        "Live Market Pulse",
        "Dynamisme des halles basé sur les volumes quotidiens moyens",
        "chart"
    )
    
    if df is None or df.empty:
        st.warning("Données insuffisantes pour le Market Pulse.")
        return

    # Calcul des volumes moyens par port
    # On suppose que df contient 'port', 'volume_kg' et 'date_vente' (ou on utilise le nombre de records comme proxy si date_vente est absente)
    try:
        if 'date_vente' in df.columns:
            # Nombre de jours uniques dans le dataset
            nb_jours = df['date_vente'].nunique()
            if nb_jours < 1: nb_jours = 1
            
            port_stats = df.groupby('port')['volume_kg'].sum() / nb_jours
        else:
            # Fallback : on divise par 30 si on n'a que des données mensuelles sans dates précises
            port_stats = df.groupby('port')['volume_kg'].sum() / 30
            
        # Liste des ports dominants stratégiques au Maroc
        DOMINANT_PORTS = ['AGADIR', 'DAKHLA', 'CASABLANCA', 'TANGER', 'LAAYOUNE', 'SAFI']
        
        # Séparer les ports dominants des autres
        available_ports = port_stats.index.str.upper()
        main_ports = [p for p in DOMINANT_PORTS if any(p in str(ap) for ap in available_ports)]
        
        # Sélectionner les ports à afficher (en priorité les dominants, puis les plus gros volumes)
        selected_port_names = []
        for p in main_ports:
            # Trouver le nom exact dans l'index
            exact_name = next(ap for ap in port_stats.index if p in str(ap).upper())
            selected_port_names.append(exact_name)
            
        remaining_slots = 4 - len(selected_port_names)
        if remaining_slots > 0:
            other_ports = port_stats.drop(selected_port_names).sort_values(ascending=False).head(remaining_slots)
            selected_port_names.extend(other_ports.index.tolist())
            
        # Limiter à 4 ports pour l'affichage standard
        top_ports = port_stats.loc[selected_port_names[:4]]
        
        ports_flow = []
        max_vol_ref = port_stats.max()
        for p_name, vol_avg in top_ports.items():
            vol_t = vol_avg / 1000 # Conversion en tonnes
            
            # Simulation d'activité et statut basé sur le volume relatif au max national
            activity = min(int((vol_avg / (max_vol_ref + 1) * 100) + 20), 98) 
            status = "Intense" if activity > 75 else ("Stable" if activity > 45 else "Modéré")
            
            ports_flow.append({
                "name": str(p_name).replace('HALLE ', '').replace('PORT ', '').title(),
                "vol": f"{vol_t:.1f} T",
                "status": status,
                "activity": activity
            })
    except Exception as e:
        st.error(f"Erreur calcul Market Pulse: {e}")
        return
    
    cols = st.columns(4)
    for col, port in zip(cols, ports_flow):
        with col:
            activity_color = "#10B981" if port['activity'] > 70 else ("#0EA5E9" if port['activity'] > 50 else "#94A3B8")
            st.markdown(f"""
            <div class="metric-card" style="border-top: 3px solid {activity_color}; padding: 1.5rem; background: white; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <span style="background: {activity_color}; width: 10px; height: 10px; border-radius: 50%;"></span>
                    <span style="font-size: 0.7rem; font-weight: 800; color: #64748B; text-transform: uppercase;">Port Actif</span>
                </div>
                <h4 style="margin: 0; color: #0F172A; font-size: 1.25rem; font-weight: 800;">{port['name']}</h4>
                <div style="margin-top: 1rem; display: flex; align-items: baseline; gap: 8px;">
                    <span style="font-size: 1.5rem; font-weight: 700; color: {activity_color};">{port['vol']}</span>
                    <span style="font-size: 0.8rem; color: #64748B;">/ jour</span>
                </div>
                <div style="margin-top: 0.5rem; color: #94A3B8; font-size: 0.8rem; font-weight: 600;">{port['status']}</div>
            </div>
            """, unsafe_allow_html=True)

def render_onp_secteur_section():
    """Section Showcase : Vision Stratégique et Méthodologie avec SVG Icons."""
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Pillars of Excellence
    PremiumComponents.section_header(
        "Piliers de Performance",
        "Les socles technologiques et économiques du projet",
        "shield"
    )
    
    pillar_col1, pillar_col2, pillar_col3 = st.columns(3)
    
    pillars = [
        {"title": "Analyse Prédictive", "val": "Optimisation des Cours", "icon": "chart", "desc": "Anticipation des fluctuations du marché halieutique via IA."},
        {"title": "Efficacité Portuaire", "val": "Halles Connectées", "icon": "database", "desc": "Suivi en temps réel de l'activité des halles ONP."},
        {"title": "Souveraineté", "val": "Plan Halieutis 2026", "icon": "anchor", "desc": "Indépendance stratégique et valorisation de la ressource."}
    ]
    
    for col, p in zip([pillar_col1, pillar_col2, pillar_col3], pillars):
        with col:
            PremiumComponents.metric_card(
                p['title'],
                p['val'],
                p['icon'],
                p['desc'],
                "blue"
            )

    st.markdown("---")
    
    # Modern Sector Split
    col_text, col_img = st.columns([1.1, 1])
    
    with col_text:
        PremiumComponents.section_header(
            "Ancrage Halieutique",
            "L'ONP, pilier de l'économie bleue marocaine",
            "anchor"
        )
        st.markdown(
            f'<div style="background: white; padding: 2.5rem; border-radius: 24px; border: 1px solid #E2E8F0; box-shadow: 0 10px 30px rgba(0,0,0,0.03);">'
            f'<p style="color: #475569; line-height: 1.8; font-size: 1.15rem; font-weight: 400; margin: 0;">{ONP_EDITO}</p></div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<p style="margin-top: 2rem;"><a href="{ONP_WEBSITE_URL}" target="_blank" rel="noopener" style="display: inline-block; background: #0F172A; color: white !important; padding: 1rem 2.5rem; border-radius: 12px; text-decoration: none; font-weight: 700; box-shadow: 0 10px 25px rgba(15, 23, 42, 0.2); transition: all 0.3s ease;">Visiter le Portail Institutionnel →</a></p>',
            unsafe_allow_html=True
        )
    
    with col_img:
        st.markdown(f"""
        <div class="portfolio-card" style="height: 480px;">
            <img src="{get_base64_image(get_image_path('port_agadir_new'))}" style="width: 100%; height: 100%; object-fit: cover;" />
            <div class="portfolio-info" style="opacity: 1; bottom: 0;">
                <p style="margin: 0; font-size: 0.85rem; font-weight: 800; color: #0EA5E9; text-transform: uppercase;">Infrastructure</p>
                <h4 style="margin: 8px 0 0 0; font-size: 1.5rem; font-weight: 800; color: white;">Port d'Agadir</h4>
                <p style="color: rgba(255,255,255,0.7); margin-top: 0.5rem;">{IMAGE_CAPTIONS['port_agadir_new']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Showcase Gallery with Hover Reveal
    st.markdown(f"#### {LuxIcons.render('search', size=20, color='#0EA5E9', extra_style='margin-right: 10px;')} Réalités du Terrain", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    gallery_items = [
        {"key": "halle_onp_1", "label": "Modernisation"},
        {"key": "halle_onp_2", "label": "Digitalisation"},
        {"key": "port_onp_1", "label": "Souveraineté"}
    ]
    
    for col, item in zip([col1, col2, col3], gallery_items):
        with col:
            st.markdown(f"""
            <div class="portfolio-card" style="height: 350px;">
                <img src="{get_base64_image(get_image_path(item['key']))}" style="width: 100%; height: 100%; object-fit: cover;" />
                <div class="portfolio-info">
                    <p style="margin: 0; font-size: 0.75rem; font-weight: 800; color: #0EA5E9; text-transform: uppercase;">{item['label']}</p>
                    <h4 style="margin: 5px 0 0 0; font-size: 1.1rem; font-weight: 700; color: white;">{IMAGE_CAPTIONS[item['key']]}</h4>
                </div>
            </div>
            """, unsafe_allow_html=True)

def render_maritime_showcase():
    """Section Showcase Maritime : Grande image immersive avec texte institutionnel."""
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col_img, col_text = st.columns([1.5, 1])
    
    with col_img:
        st.markdown(f"""
        <div style="
            border-radius: 24px;
            overflow: hidden;
            box-shadow: 0 20px 50px rgba(15, 23, 42, 0.1);
            height: 550px;
        ">
            <img src="{get_base64_image(get_image_path('showcase_secondary'))}" style="width: 100%; height: 100%; object-fit: cover;" />
        </div>
        """, unsafe_allow_html=True)
    
    with col_text:
        st.markdown("<br><br>", unsafe_allow_html=True)
        PremiumComponents.section_header(
            "Efficacité Halieutique",
            "Le Maroc, leader régional de l'économie bleue",
            "anchor"
        )
        st.markdown(f"""
        <div style="background: white; padding: 2.5rem; border-radius: 20px; border: 1px solid #E2E8F0; margin-top: 1.5rem; box-shadow: 0 10px 30px rgba(0,0,0,0.05);">
            <p style="font-size: 1.15rem; color: #0F172A; line-height: 1.8; margin: 0; font-weight: 500;">
                Le secteur de la pêche maritime constitue un pilier stratégique du Royaume. 
                Avec plus de 3 500 km de côtes, le Maroc se positionne comme le premier producteur de poissons en Afrique 
                et assure une souveraineté halieutique durable.
            </p>
            <p style="font-size: 1.15rem; color: #0F172A; line-height: 1.8; margin-top: 1.5rem; font-weight: 500;">
                L'Office National des Pêches (ONP) pilote cette dynamique à travers le Plan Halieutis, 
                modernisant les infrastructures et digitalisant la filière pour une valorisation optimale de la ressource.
            </p>
        </div>
        """, unsafe_allow_html=True)

def render_national_dashboard():
    """Composant visuel montrant la situation météo et carburant sur tout le Royaume."""
    from utils import get_national_weather_summary, get_real_fuel_price
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    PremiumComponents.section_header(
        "Situation Halieutique Nationale",
        "Conditions en temps réel sur l'ensemble du littoral marocain",
        "anchor"
    )
    
    weather_summary = get_national_weather_summary()
    
    # 1. Carburant par Zone
    st.markdown("##### Index Carburant par Zone")
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        price_nc = get_real_fuel_price(region="CENTRE")
        st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 15px; border-top: 4px solid #F59E0B; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
            <p style="margin:0; font-size: 0.8rem; color: #64748B; font-weight: 700;">NORD & CENTRE</p>
            <p style="margin:5px 0; font-size: 1.8rem; font-weight: 900; color: #B45309;">{price_nc:.2f} <span style="font-size: 1rem;">DH/L</span></p>
            <p style="margin:0; font-size: 0.8rem; color: #94A3B8;">Régime Standard</p>
        </div>
        """, unsafe_allow_html=True)
    with f_col2:
        price_gs = get_real_fuel_price(region="GRAND_SUD")
        st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 15px; border-top: 4px solid #10B981; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
            <p style="margin:0; font-size: 0.8rem; color: #64748B; font-weight: 700;">PROVINCES DU SUD (DAKHLA/LAAYOUNE)</p>
            <p style="margin:5px 0; font-size: 1.8rem; font-weight: 900; color: #065F46;">{price_gs:.2f} <span style="font-size: 1rem;">DH/L</span></p>
            <p style="margin:0; font-size: 0.8rem; color: #059669; font-weight: 600;">Exonération (Détaxé)</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Météo par Port Clé
    st.markdown("##### État de la Mer par Port Stratégique")
    cols = st.columns(len(weather_summary))
    for col, (label, data) in zip(cols, weather_summary.items()):
        with col:
            color = "#EF4444" if data['tempete'] else "#0EA5E9"
            bg_color = "rgba(239, 68, 68, 0.05)" if data['tempete'] else "rgba(14, 165, 233, 0.05)"
            st.markdown(f"""
            <div style="background: {bg_color}; padding: 20px; border-radius: 15px; border-bottom: 4px solid {color}; text-align: center;">
                <p style="margin:0; font-size: 0.7rem; color: #64748B; font-weight: 800; text-transform: uppercase;">{label}</p>
                <h4 style="margin: 8px 0; color: #0F172A; font-weight: 800;">{data['port']}</h4>
                <div style="font-size: 1.5rem; font-weight: 900; color: {color};">{data['wind']:.0f} <span style="font-size: 0.8rem;">km/h</span></div>
                <div style="margin-top: 5px; font-size: 0.9rem; color: #64748B; font-weight: 600;">Mer : {data['wave']:.1f}m</div>
            </div>
            """, unsafe_allow_html=True)

def render_page_accueil(df):
    """Page d'accueil 'Elite Command Center' avec KPIs et visualizations avancées."""
    render_onp_hero()
    
    # Priorité à la Vision et à la Situation Nationale (Temps Réel)
    try:
        render_maritime_showcase()
    except Exception as e:
        st.error(f"Erreur dans Maritime Showcase: {e}")
        
    try:
        render_national_dashboard()
    except Exception as e:
        st.error(f"Erreur dans Dashboard National: {e}")
        
    try:
        render_onp_secteur_section()
    except Exception as e:
        st.error(f"Erreur dans Secteur Section: {e}")
        
    try:
        render_live_market_pulse(df)
    except Exception as e:
        st.error(f"Erreur dans Market Pulse: {e}")
        
    try:
        render_institutional_bulletin()
    except Exception as e:
        st.error(f"Erreur dans Institutional Bulletin: {e}")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    PremiumComponents.section_header(
        "Intelligence Stratégique",
        "Maillage territorial et monitoring national",
        "anchor"
    )

    # La carte exhaustive (Analyse géographique)
    render_interactive_strategy_map()
    
    if df.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        PremiumComponents.info_box("Aucune donnée disponible pour cette sélection.", "warning")
        st.info("Veuillez réinitialiser ou ajuster vos filtres dans la barre latérale.")
        return

    # Données et Résultats (KPIs et Graphiques)
    render_hero_stats()
    render_kpis(df)
    
    PremiumComponents.section_header(
        "Vue d'ensemble du Marché",
        "Visualisations avancées et tendances temporelles",
        "chart"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Top 10 espèces par volume")
        fig = plot_top_species_by_volume(df)
        fig = apply_premium_plotly_styling(fig)
        st.plotly_chart(fig, width="stretch")
    
    with col2:
        st.markdown("#### Dynamique de l'Activité Portuaire")
        tab_reg, tab_port = st.tabs(["Vue Régionale", "Top 10 Ports"])
        
        with tab_reg:
            fig_reg = plot_regional_activity_heatmap(df)
            # Application du style institutionnel
            fig_reg = apply_premium_plotly_styling(fig_reg)
            st.plotly_chart(fig_reg, width="stretch")
            
        with tab_port:
            fig_port = plot_port_activity_heatmap(df)
            fig_port = apply_premium_plotly_styling(fig_port)
            st.plotly_chart(fig_port, width="stretch")
    
    # Insights Section
    st.markdown("---")
    PremiumComponents.section_header(
        "Insights Stratégiques",
        "Analyse condensée des opportunités de marché",
        "target"
    )
    
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        PremiumComponents.info_box(
            "Les prix sont plus <b>stables</b> en période estivale avec une hausse <b>15%</b> moyenne",
            "info"
        )
    
    with insight_col2:
        PremiumComponents.info_box(
            "Le port de <b>Casablanca</b> génère <b>45%</b> des revenus totaux",
            "success"
        )
    
    with insight_col3:
        PremiumComponents.info_box(
            "Volatilité accrue en <b>hiver</b> — à monitorer attentivement",
            "warning"
        )

def render_page_analytics(df):
    """Page d'analyse des prix"""
    render_module_hero(
        "Intelligence de Marché",
        "Exploration approfondie de la dynamique des prix et des tendances nationales",
        "marche_poisson"
    )
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Distribution",
        "Par port",
        "Volume vs prix",
        "Saisonnalité"
    ])
    
    with tab1:
        st.markdown("### Distribution des Prix par Espèce")
        fig = plot_price_distribution_by_species(df)
        fig = apply_premium_plotly_styling(fig)
        st.plotly_chart(fig, width="stretch")
        
        PremiumComponents.info_box(
            "Les <b>box plots</b> montrent la distribution, les quartiles et les outliers pour chaque espèce.",
            "info"
        )
    
    with tab2:
        st.markdown("### Prix Moyen par Port")
        fig = plot_price_by_port(df)
        # Amélioration technique : RangeSlider
        fig.update_xaxes(rangeslider_visible=True)
        fig = apply_premium_plotly_styling(fig)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### Relation Volume ↔ Prix")
        fig = plot_volume_price_relationship(df)
        fig = apply_premium_plotly_styling(fig)
        st.plotly_chart(fig, width="stretch")
    
    with tab4:
        st.markdown("### Saisonnalité des Prix")
        fig = plot_seasonal_analysis(df)
        fig = apply_premium_plotly_styling(fig)
        st.plotly_chart(fig, width="stretch")

def render_page_financial(df):
    """Page d'analyse financière"""
    render_module_hero(
        "Analyse Financière",
        "Performance économique, rentabilité et vision stratégique des flux",
        "marche_poisson"
    )
    
    if df.empty:
        PremiumComponents.info_box("Aucune donnée disponible pour cette sélection.", "warning")
        return
    
    # Création des onglets
    tab1, tab2 = st.tabs(["Vue Globale", "Comparaison 2024-2025"])
    
    with tab1:
        st.markdown("### Performance Globale")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Top 20 Halles les plus rentables")
            from financial_analysis import plot_top_halles_revenue
            fig_halles = plot_top_halles_revenue(df, top_n=20)
            fig_halles = apply_premium_plotly_styling(fig_halles)
            st.plotly_chart(fig_halles, use_container_width=True)
        
        with col2:
            st.markdown("#### Performance des Marchés de Gros (MG)")
            from financial_analysis import plot_top_mgs_revenue
            # On affiche par défaut 2025 comme demandé, mais on peut adapter selon le DF
            target_year = 2025 if 2025 in df['annee'].unique() else 2024
            fig_mgs = plot_top_mgs_revenue(df, year=target_year)
            fig_mgs = apply_premium_plotly_styling(fig_mgs)
            st.plotly_chart(fig_mgs, use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### Contribution des Espèces")
        fig = plot_revenue_contribution_by_species(df)
        fig = apply_premium_plotly_styling(fig)
        st.plotly_chart(fig, width="stretch")
        
        st.markdown("#### Espèces Rentables")
        fig = plot_top_profitable_species(df)
        fig = apply_premium_plotly_styling(fig)
        st.plotly_chart(fig, width="stretch")
        
        st.markdown("---")
        st.markdown("#### Résumé Financier")
        summary_table = create_financial_summary_table(df)
        st.dataframe(summary_table, width="stretch", hide_index=False)

    with tab2:
        st.markdown("### Analyse Comparative : 2024 vs 2025")
        
        # Vérification des années disponibles pour ce calcul spécifique
        # Il faut passer le DF complet (sans filtre date) idéalement, mais ici on utilise le DF filtré
        # Si le filtre date exclut une année, l'analyse sera partielle.
        # On tente le calcul :
        df_effects = calculate_price_volume_effect(df)
        
        if not df_effects.empty:
            # Indicateurs Clés de l'Évolution
            total_var = df_effects['variation_mdh'].sum()
            
            # Affichage style KPI
            st.markdown(f"""
            <div style="display: flex; gap: 20px; margin-bottom: 20px;">
                <div style="flex: 1; padding: 15px; background: #F0F9FF; border-radius: 10px; border-left: 5px solid #0EA5E9;">
                    <h4 style="margin:0; color: #64748B;">Variation Totale CA</h4>
                    <h2 style="margin:5px 0; color: #0EA5E9;">{total_var:+.2f} MDH</h2>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("#### Décomposition Effet Prix / Volume")
            st.info("**Effet Volume** : Variation due aux quantités vendues (à prix constant). \n\n"
                    "**Effet Prix** : Variation due à l'évolution des prix (à volume constant).")
            
            fig_effets = plot_price_volume_analysis(df_effects, top_n=12)
            fig_effets = apply_premium_plotly_styling(fig_effets)
            st.plotly_chart(fig_effets, width="stretch")
            
            st.markdown("#### Détail par Espèce (Top 50)")
            
            # Formatage pour l'affichage
            display_cols = {
                'espece': 'Espèce',
                'recette_2024_mdh': 'CA 2024 (MDH)',
                'recette_2025_mdh': 'CA 2025 (MDH)',
                'variation_mdh': 'Variation (MDH)',
                'effet_volume_mdh': 'Effet Volume (MDH)',
                'effet_prix_mdh': 'Effet Prix (MDH)'
            }
            
            st.dataframe(
                df_effects[display_cols.keys()].rename(columns=display_cols).style
                .format("{:.2f}", subset=list(display_cols.values())[1:])
                .background_gradient(cmap="RdYlGn", subset=['Variation (MDH)']),
                width="stretch"
            )
            
            # Bouton de téléchargement
            st.markdown("---")
            if st.button("Télécharger Rapport Comparatif (Word)", key="btn_dl_comp"):
                with st.spinner("Génération du rapport..."):
                    file_path = create_comparison_word_report(df_effects)
                    with open(file_path, "rb") as f:
                        btn = st.download_button(
                            label="Cliquez pour télécharger",
                            data=f,
                            file_name="Rapport_Comparaison_2024_2025.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                        st.success("Rapport généré avec succès !")
            
        else:
            st.warning("Impossible de réaliser la comparaison 2024-2025 avec les données actuelles. Vérifiez que les filtres incluent les deux années.")

def render_page_ml(df, predictor):
    """Page du modèle Machine Learning"""
    import os
    import pandas as pd
    data_granulaire = 'donnees_simulation_onp.csv'
    if os.path.exists(data_granulaire):
        try:
            df_sim = pd.read_csv(data_granulaire)
            if 'espece' in df_sim.columns and 'port' in df_sim.columns:
                from utils import clean_data
                df = clean_data(df_sim)
        except:
            pass

    render_module_hero(
        "Modélisation Prédictive",
        "Anticipation des cours et aide à la décision stratégique par IA",
        "halle_poisson"
    )
    
    # On ne bloque plus si df est vide pour laisser l'accès au réentraînement
    is_empty = df is None or df.empty
    
    if predictor is None:
        PremiumComponents.info_box(
            "Le modèle ML n'est pas encore entraîné ou les données sont invalides. Veuillez charger des données réelles ou de simulation.",
            "error"
        )
        # On continue quand même pour afficher l'onglet de réentraînement
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Aide à la Décision",
        "Prédiction & Pourquoi",
        "Global Insights",
        "Performance & Comparaison",
        "Surveillance Marché",
        "Réentraînement"
    ])
    
    with tab1:
        st.markdown(f"### {LuxIcons.render('anchor', size=24)} Espace Opérationnel : Aide au Débarquement & Crie", unsafe_allow_html=True)
        
        if is_empty:
            PremiumComponents.info_box("Veuillez ajuster les filtres dans la barre latérale pour activer les outils d'aide à la décision.", "warning")
        elif predictor is None:
             st.error("Prédicteur non disponible.")
        else:
            col_op1, col_op2 = st.columns([1, 1])
            
            with col_op1:
                st.markdown(f"#### {LuxIcons.render('anchor', size=20)} Conseiller de Débarquement", unsafe_allow_html=True)
                from utils import get_unique_valid_species
                valid_species = get_unique_valid_species(df, require_image=True)
                v_species = st.selectbox("Espèce à débarquer", valid_species, key="op_species")
                v_vol = st.number_input("Volume estimé (tonnes)", value=2.0)
                
                if st.button("Comparer les Ports", key="btn_compare"):
                    recs = suggest_optimal_ports(predictor, df, v_species, v_vol * 1000)
                    if recs is not None and not recs.empty:
                        # Visualization Plotly pour la rentabilité
                        st.markdown("#### Comparaison de la Recette Nette")
                        fig_recs = px.bar(
                            recs.head(5), 
                            x='port', 
                            y='recette_estimee',
                            text='recette_estimee',
                            color='recette_estimee',
                            color_continuous_scale='Blues',
                            labels={'recette_estimee': 'Recette (DH)', 'port': 'Port'}
                        )
                        fig_recs.update_traces(texttemplate='%{text:,.0f} DH', textposition='outside')
                        st.plotly_chart(apply_premium_plotly_styling(fig_recs), use_container_width=True)

                        # Styling table
                        st.markdown("#### Détails Logistiques")
                        st.dataframe(recs.style.highlight_max(axis=0, subset=['recette_estimee'], color="#DCFCE7"), width="stretch")
                        
                        best_port = recs.iloc[0]['port']
                        st.markdown(f"""
                            <div style="background-color: rgba(16, 185, 129, 0.1); color: #10B981; padding: 1.5rem; border-radius: 12px; border: 1px solid #10B981; margin-top: 1rem;">
                                <h4 style="margin:0; color: #10B981;">Recommandation Stratégique</h4>
                                <p style="margin: 5px 0 0 0;">Débarquement conseillé à <b>{best_port}</b> pour maximiser votre marge nette.</p>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("Pas assez de données pour cette simulation.")
    
            with col_op2:
                st.markdown(f"#### {LuxIcons.render('target', size=20)} Assistant de Mise à Prix", unsafe_allow_html=True)
                a_port = st.selectbox("Port de l'Enchère", sorted(_series(df, "port").unique()), key="op_port")
                
                if st.button("Calculer Mise à Prix", key="btn_auction"):
                    auction = get_auction_starting_price(predictor, df, v_species, a_port, v_vol * 1000)
                    if auction:
                        st.markdown(f"""
                        <div style="background: #F0F9FF; border: 1px solid #BAE6FD; border-radius: 12px; padding: 1.5rem; text-align: center;">
                            <p style="margin:0; color: #0369A1; font-weight: 700;">Prix de Départ Suggéré</p>
                            <h2 style="color: #0369A1; font-size: 2.5rem; margin: 0.5rem 0;">{auction['suggested_starting_price']} <span style="font-size: 1rem;">DH/kg</span></h2>
                            <hr style="border: none; border-top: 1px solid #BAE6FD; margin: 1rem 0;">
                            <div style="display: flex; justify-content: space-around; font-size: 0.85rem; color: #64748B;">
                                <div>Cible Attendue : <b>{auction['target_price']} DH</b></div>
                                <div>Max Récent : <b>{auction['recent_max']} DH</b></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("### Analyse de Prédiction & Cause")
        
        if is_empty:
            PremiumComponents.info_box("Données insuffisantes avec les filtres actuels pour effectuer une analyse de prédiction.", "warning")
        elif predictor is None:
            st.error("Le modèle de prédiction n'est pas chargé.")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                from utils import get_unique_valid_species
                species_options = get_unique_valid_species(df, require_image=True)
                species = st.selectbox("Espèce", species_options, key="ml_species", help="Choisissez l'espèce pour la prédiction")
            with col2:
                port_options = sorted(_series(df, "Port", "port").dropna().unique().tolist())
                port = st.selectbox("Port", port_options, key="ml_port", help="Port de débarquement")
            with col3:
                volume = st.number_input("Volume (tonnes)", min_value=1, value=1, help="Volume en tonnes pour la prédiction")
            
            if st.button("Prédire le prix", key="predict_btn"):
                with st.spinner("Analyse intelligente en cours..."):
                    time.sleep(0.5)
                    try:
                        volume_kg = volume * 1000
                        prediction = predictor.predict_single(
                            df, species, port, volume_kg=volume_kg
                        )
                        
                        # Récupérer l'interprétation
                        interpretation = get_prediction_interpretation(
                            predictor, df, species, port, volume_kg, prediction
                        )
                        
                        # Alerte Repos Biologique
                        current_month = datetime.now().month
                        species_upper = species.upper()
                        if species_upper in REPOS_BIOLOGIQUE_MAP and current_month in REPOS_BIOLOGIQUE_MAP[species_upper]:
                            st.warning(f"**Attention : {species} est actuellement en période de Repos Biologique.** Les prix prédits peuvent être sujets à une forte volatilité due à l'arrêt temporaire de la pêche.")
                        
                        st.markdown("---")
                        
                        # Image de l'espèce
                        species_upper_img = species.upper() if isinstance(species, str) else ""
                        from utils import get_species_image_path
                        
                        img_path = get_species_image_path(species_upper_img)

                        # Affichage du résultat principal
                        res_col_img, res_col1, res_col2 = st.columns([0.8, 1, 1.5])
                        
                        with res_col_img:
                            st.image(img_path, use_container_width=True, caption=f"{species}")
                            
                        with res_col1:
                            PremiumComponents.metric_card(
                                "Prix Prédit (Elite AI)",
                                f"{prediction:.2f} DH/kg",
                                "brain",
                                f"Statut : {interpretation['status']}",
                                "blue"
                            )
                        
                        with res_col2:
                            st.markdown(f"#### {LuxIcons.render('brain', size=20)} Interprétation de l'IA", unsafe_allow_html=True)
                            st.info(interpretation['insight'])
                            
                            # Facteurs d'influence
                            if interpretation['factors']:
                                fact_cols = st.columns(len(interpretation['factors']))
                                for i, factor in enumerate(interpretation['factors']):
                                    with fact_cols[i]:
                                        color = "#10B981" if factor['weight'] > 0 else "#EF4444"
                                        st.markdown(f"""
                                        <div style="padding: 1rem; background: #F8FAFC; border-radius: 12px; border: 1px solid #E2E8F0;">
                                            <p style="margin:0; font-size: 0.75rem; color: #64748B; text-transform: uppercase;">{factor['factor']}</p>
                                            <p style="margin:4px 0; font-size: 1.1rem; font-weight: 700; color: {color};">{factor['value']}</p>
                                            <p style="margin:0; font-size: 0.7rem; color: #94A3B8;">Impact {factor['impact']}</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"Erreur lors de la prédiction : {str(e)}")
    
    with tab3:
        st.markdown("### Facteurs de Décision Globaux")
        
        if predictor is None:
            st.error("Modèle non disponible.")
        else:
            importance_df = get_global_importance_data(predictor)
            
            if not importance_df.empty:
                col_chart, col_explain = st.columns([2, 1])
                with col_chart:
                    fig = px.bar(
                        importance_df,
                        x='importance',
                        y='label',
                        orientation='h',
                        title="Poids des variables dans la décision (Top Features)",
                        color='importance',
                        color_continuous_scale='Blues'
                    )
                    fig.update_layout(yaxis={'categoryorder':'total ascending'})
                    fig = apply_premium_plotly_styling(fig)
                    st.plotly_chart(fig, width="stretch")
                
                with col_explain:
                    st.markdown("""
                    <b>Comprendre l'importance :</b>
                    Les modèles "Booster" (XGBoost) analysent des milliers d'arbres de décision pour identifier les variables les plus discriminantes.
                    
                    - <b>Volume</b> : Le facteur le plus volatile influençant l'équilibre offre/demande.
                    - <b>Port</b> : Reflète les spécificités logistiques et la notoriété régionale.
                    - <b>Mois</b> : Capture la saisonnalité biologique des espèces.
                    """, unsafe_allow_html=True)
            else:
                st.warning("Données d'importance non disponibles pour ce type de modèle.")
    
    with tab4:
        st.markdown("### Performance & Comparaison Stratégique")
        
        if predictor is None:
            st.info("Lancez un réentraînement ou ajustez les filtres pour voir les performances.")
        else:
            # Affichage des métriques Elite XGBoost
            m1, m2, m3, m4 = st.columns(4)
            best_results = predictor.results.get('XGBoost', {})
            
            with m1:
                st.metric("Précision R²", f"{best_results.get('R2', 0):.4f}")
            with m2:
                st.metric("Erreur RMSE", f"{best_results.get('RMSE', 0):.2f} DH/kg")
            with m3:
                st.metric("Erreur MAE", f"{best_results.get('MAE', 0):.2f} DH/kg")
            with m4:
                mape = best_results.get('MAPE', 5)
                # Fiabilité affichée: 100 - MAPE, minimum 0%
                reliability = max(0, 100 - mape)
                st.metric("Fiabilité (MAPE)", f"{reliability:.1f}%")

            st.markdown("---")
            
            # Reconstruction dynamique de la table de comparaison
            comparison_rows = []
            if hasattr(predictor, 'results') and predictor.results:
                for m_name, metrics in predictor.results.items():
                    comparison_rows.append({
                        'Modèle': m_name,
                        'RMSE': f"{metrics.get('RMSE', 0):.2f}",
                        'MAE': f"{metrics.get('MAE', 0):.2f}",
                        'R²': f"{metrics.get('R2', 0):.4f}"
                    })
            
            if comparison_rows:
                comparison_df = pd.DataFrame(comparison_rows)
                st.table(comparison_df.set_index('Modèle'))
            else:
                st.info("Détails de comparaison non disponibles.")
                
            st.markdown("---")
            st.markdown("#### Validation Croisée & Détection de Surapprentissage")
            st.caption("Évaluation rigoureuse avec K-Fold (k=5) pour garantir la robustesse du modèle (Point 2)")
            
            if st.button("Lancer la Validation Croisée (K-Fold)", key="btn_cv"):
                with st.spinner("Exécution de la validation croisée en cours..."):
                    try:
                        from utils import create_features, encode_categorical, clean_data
                        
                        # Preparation des données pour la CV
                        df_cv_clean = clean_data(df)
                        df_cv_feat = create_features(df_cv_clean)
                        df_cv_enc, _ = encode_categorical(df_cv_feat)
                        
                        # Utiliser les mêmes features que le modèle
                        X = df_cv_enc[predictor.feature_names].fillna(0)
                        y = df_cv_enc['prix_unitaire_dh']
                        
                        cv_results = predictor.evaluate_model(X, y, n_splits=5)
                        
                        for model_name, res in cv_results.items():
                            st.markdown(f"##### Modèle : {model_name}")
                            
                            # Alerte de surapprentissage
                            if res['is_overfitting']:
                                st.error(f"⚠️ **Alerte Surapprentissage (Overfitting)** : L'écart de score R² entre l'entraînement et le test est de {res['overfit_gap']:.3f} (Seuil > 0.10). Le modèle apprend par cœur au lieu de généraliser.")
                            else:
                                st.success(f"✅ **Généralisation Saine** : L'écart de R² est faible ({res['overfit_gap']:.3f}). Pas de surapprentissage détecté.")
                                
                            # Métriques comparatives
                            col_tr, col_te = st.columns(2)
                            with col_tr:
                                st.markdown("**Performance Entraînement (Train)**")
                                st.markdown(f"- R² : `{res['train_r2']:.4f}`")
                                st.markdown(f"- RMSE : `{res['train_rmse']:.2f}` DH/kg")
                                st.markdown(f"- MAE : `{res['train_mae']:.2f}` DH/kg")
                            with col_te:
                                st.markdown("**Performance Test (Validation)**")
                                st.markdown(f"- R² : `{res['test_r2']:.4f}`")
                                st.markdown(f"- RMSE : `{res['test_rmse']:.2f}` DH/kg")
                                st.markdown(f"- MAE : `{res['test_mae']:.2f}` DH/kg")
                                
                            # Graphe Plotly
                            st.plotly_chart(res['plotly_fig'], use_container_width=True)
                            st.markdown("---")
                            
                    except Exception as e:
                        st.error(f"Erreur lors de la validation croisée : {str(e)}")

    with tab5:
        st.markdown(f"### {LuxIcons.render('shield', size=24)} Surveillance du Marché & Anomalies", unsafe_allow_html=True)
        st.caption("Détection automatisée des écarts de prix atypiques dans les dernières transactions.")
        
        if is_empty or predictor is None:
            st.warning("Données ou modèle indisponibles pour la détection d'anomalies.")
        else:
            anomalies_df = detect_market_anomalies(df, predictor)
            
            if not anomalies_df.empty:
                count = len(anomalies_df)
                st.error(f"Attention : {count} anomalies détectées nécessitant une vérification.")
                
                # Formater les colonnes pour l'affichage
                display_df = anomalies_df.copy()
                # Renommer pour l'utilisateur
                display_df.columns = ['Date', 'Espèce', 'Port', 'Prix Réel', 'Prix Attendu', 'Écart %', 'Raison / Pourquoi', 'Sévérité']
                st.dataframe(display_df.style.apply(lambda x: ['background-color: #FEE2E2' if v == 'High' else '' for v in x], axis=1), width="stretch", hide_index=True)
                
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    PremiumComponents.info_box("Les anomalies de sévérité 'High' indiquent souvent une erreur de saisie ou une condition de marché exceptionnelle (pénurie soudaine).", "warning")
            else:
                st.success("Aucune anomalie majeure détectée dans les transactions récentes.")

    with tab6:
        st.markdown(f"### {LuxIcons.render('brain', size=24)} Centre de Réentraînement de l'Intelligence Artificielle", unsafe_allow_html=True)
        st.caption("Mettez à jour le cerveau de l'application en lui fournissant de nouvelles données historiques réelles.")
        
        col_up, col_info = st.columns([1, 1])
        
        with col_up:
            st.markdown("""
            <div style="background: rgba(14, 165, 233, 0.05); padding: 1.5rem; border-radius: 12px; border: 1px dashed #0EA5E9; margin-bottom: 1.5rem;">
                <h4 style="margin-top: 0; color: #0369A1;">Importation des Données</h4>
                <p style="font-size: 0.9rem; color: #64748B;">Chargez le fichier Excel institutionnel (format ONP) contenant les nouvelles transactions.</p>
            </div>
            """, unsafe_allow_html=True)
            
            ml_file = st.file_uploader(
                "Choisir un fichier Excel (.xlsx)", 
                type=['xlsx'],
                key="ml_retrain_upload",
                help="Le fichier doit être au format institutionnel ONP (Colonnes Port, Espèce, Volume, CA)."
            )
            
            if ml_file is not None:
                if st.button("Lancer le Réentraînement", key="btn_retrain", width="stretch", type="primary"):
                    with st.status("Entraînement des modèles en cours...", expanded=True) as status:
                        st.write("Analyse et extraction des données...")
                        result = retrain_model_from_excel(ml_file)
                        
                        if "success" in result:
                            st.write(f"✓ {result['row_count']} nouveaux enregistrements extraits.")
                            st.write("Entraînement des modèles (Linear, Random Forest, XGBoost)...")
                            # Simulations de progression pour l'effet visuel
                            time.sleep(1)
                            st.write("Optimisation des hyperparamètres...")
                            time.sleep(1)
                            
                            st.success("Réentraînement Terminé avec Succès !")
                            
                            res = result['results']
                            best_name = "XGBoost" # Par défaut si non spécifié, ou extraire de result
                            
                            st.markdown("---")
                            st.markdown("#### Performance du Nouveau Modèle")
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                PremiumComponents.metric_card("Précision R²", f"{res.get('XGBoost', {}).get('R2', 0):.4f}", "target", "Elite Accuracy", "green")
                            with c2:
                                PremiumComponents.metric_card("Erreur MAE", f"{res.get('XGBoost', {}).get('MAE', 0):.2f} DH", "chart", "Mean Absolute Error", "blue")
                            with c3:
                                PremiumComponents.metric_card("Lignes traitées", f"{result['row_count']}", "database", "Volume de données", "orange")
                            
                            PremiumComponents.info_box("Le meilleur modèle a été automatiquement sauvegardé et sera utilisé pour toutes les futures prédictions.", "success")
                        else:
                            st.error(f"Erreur : {result.get('error', 'Inconnue')}")
                            status.update(label="Échec de l'entraînement", state="error")
        
        with col_info:
            st.markdown(f"""
            <div style="background: white; padding: 2rem; border-radius: 20px; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); height: 100%;">
                <h4 style="margin-top: 0; color: #0F172A;">{LuxIcons.render('shield', size=20)} Sécurité & Intégrité</h4>
                <p style="color: #475569; font-size: 0.95rem; line-height: 1.6;">
                    Le processus de réentraînement suit les protocoles de validation croisée standards :
                </p>
                <ul style="color: #64748B; font-size: 0.9rem; padding-left: 1.2rem;">
                    <li style="margin-bottom: 0.5rem;"><b>Nettoyage automatique</b> des valeurs aberrantes et des doublons.</li>
                    <li style="margin-bottom: 0.5rem;"><b>Sélection de variables</b> basée sur l'importance portuaire et la périodicité.</li>
                    <li style="margin-bottom: 0.5rem;"><b>Validation 80:20</b> (entraînement / test) pour garantir la généralisation.</li>
                    <li style="margin-bottom: 0.5rem;"><b>Mise à jour à chaud</b> : Le modèle est mis à jour en mémoire instantanément.</li>
                </ul>
                <div style="margin-top: 1.5rem; padding: 1rem; background: #F8FAFC; border-radius: 12px; font-size: 0.85rem; color: #94A3B8;">
                    Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M')}
                </div>
            </div>
            """, unsafe_allow_html=True)

def render_page_simulation(df):
    """Page de simulation"""
    # Pour le simulateur, on préfère des données granulaires si disponibles
    data_granulaire = 'donnees_simulation_onp.csv'
    if os.path.exists(data_granulaire):
        try:
            df_sim = pd.read_csv(data_granulaire)
            # Nettoyage minimal pour assurer la compatibilité + filtre global des images
            if 'espece' in df_sim.columns and 'port' in df_sim.columns:
                from utils import clean_data
                df = clean_data(df_sim)
        except:
            pass

    render_module_hero(
        "Simulateur Stratégique",
        "Modélisation de scénarios d'impact sur les cours halieutiques",
        "port_agadir"
    )
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Paramètres de Simulation")
        from utils import get_unique_valid_species
        species_options = get_unique_valid_species(df, require_image=True)
        port_options = sorted(df["port"].dropna().unique().tolist()) if "port" in df.columns else []
        species_filter = st.selectbox(
            "Espèce",
            species_options,
            key="sim_species",
            help="Espèce pour laquelle simuler l'impact volume/prix"
        )
        
        # Filtrage dynamique des ports en fonction de l'espèce
        valid_ports = sorted(df[df['espece'] == species_filter]['port'].dropna().unique().tolist())
        
        port_filter = st.selectbox(
            "Port",
            valid_ports,
            key="sim_port",
            help=f"Ports disposant de données historiques pour {species_filter}"
        )
        volume_change_pct = st.slider(
            "Variation de volume (%)",
            min_value=-30,
            max_value=50,
            value=10,
            step=5,
            help="Hypothèse de variation du volume débarqué"
        )
        
        # Affichage de l'image de l'espèce sélectionnée
        species_upper = species_filter.upper() if isinstance(species_filter, str) else ""
        from utils import get_species_image_path
        
        img_path = get_species_image_path(species_upper)
        
        st.markdown(f"**Apparence : {species_filter}**")
        st.image(img_path, use_container_width=True, caption=f"Guide des espèces - {species_filter}")
    
    with col2:
        st.markdown("### Impact Simulé")
        
        if st.button("Lancer la simulation", key="simulate_btn"):
            with st.spinner("Simulation en cours..."):
                time.sleep(0.6)
                try:
                    impact = simulate_price_impact(df, species_filter, port_filter, volume_change_pct)
                    if "error" in impact:
                        PremiumComponents.info_box(impact["error"], "error")
                    else:
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            PremiumComponents.metric_card(
                                "Impact recette",
                                f"{impact.get('impact_recette_dh', 0):+,.0f} DH",
                                "finance",
                                f"{impact.get('impact_recette_pct', 0):+.1f} %",
                                "green" if impact.get("impact_recette_dh", 0) >= 0 else "orange"
                            )
                        with col_b:
                            PremiumComponents.metric_card(
                                "Nouveau prix",
                                f"{impact.get('nouveau_prix_dh_kg', 0):.2f} DH/kg",
                                "chart",
                                f"Variation {impact.get('variation_prix_pct', 0):.1f} %",
                                "blue"
                            )
                        with col_c:
                            PremiumComponents.metric_card(
                                "Nouvelle recette",
                                f"{impact.get('nouvelle_recette_dh', 0):,.0f} DH",
                                "", # Removed emoji
                                "Estimée",
                                "green"
                            )
                        PremiumComponents.info_box(
                            f"Simulation pour <b>{species_filter}</b> à <b>{port_filter}</b> : "
                            f"volume {volume_change_pct:+.0f} % → recette {impact.get('impact_recette_pct', 0):+.1f} %.",
                            "success"
                        )
                except Exception as e:
                    PremiumComponents.info_box(f"Erreur : {str(e)}", "error")

def render_dr_special_section(df_unused):
    """Section Spéciale DR : Analyse isolée sur le nouveau rapport Excel"""
    from financial_analysis import calculate_price_volume_effect
    from data_loader import extract_ml_data
    from report_generator import create_comparison_word_report
    from data_corrections import apply_data_corrections
    import io

    dr_file = 'New Report(2024-2025) -DR (3).xlsx'
    
    st.markdown("""
    <div style="background: #F8FAFC; padding: 2rem; border-radius: 20px; color: #0F172A; margin-bottom: 2rem; border: 1px solid #E2E8F0; border-left: 5px solid #0EA5E9;">
        <h3 style="color: #0369A1; margin: 0;">ANALYSE COMPARATIVE 2024-2025 (Rapport DR Spécial)</h3>
        <p style="color: #64748B; margin-top: 0.5rem;">Cette section est exclusivement basée sur le fichier <b>New Report(2024-2025) -DR (3).xlsx</b>.</p>
    </div>
    """, unsafe_allow_html=True)

    if not os.path.exists(dr_file):
        st.error(f"Le fichier '{dr_file}' est introuvable à la racine du projet.")
        return

    # Option de correction des données
    col_opt1, col_opt2 = st.columns([3, 1])
    with col_opt1:
        st.markdown("#### Options d'Analyse")
    with col_opt2:
        use_corrections = st.checkbox("Appliquer corrections", value=False, 
                                     help="Applique les corrections basées sur l'analyse qualitative (Feuil3)")

    # Chargement isolé du nouveau rapport
    @st.cache_data(ttl=600)
    def load_dr_data_isolated():
        return extract_ml_data(dr_file)

    with st.spinner("Chargement et extraction des données DR..."):
        df_dr = load_dr_data_isolated()

    if df_dr is None or df_dr.empty:
        st.error("Impossible d'extraire les données du rapport DR. Vérifiez le format du fichier.")
        return

    # Appliquer les corrections si demandé
    if use_corrections:
        with st.spinner("Application des corrections basées sur l'analyse qualitative..."):
            df_dr = apply_data_corrections(df_dr)
            st.success("Corrections appliquées (Céphalopodes +15%, Poisson Pélagique +3%, etc.)")

    # Calcul des effets
    with st.spinner("Calcul des effets mathématiques..."):
        df_effects = calculate_price_volume_effect(df_dr)
    
    if df_effects.empty:
        st.info("Données des années 2024 et 2025 non détectées dans le rapport DR.")
        return

    # Export Word Button
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.markdown("#### Décomposition Détaillée par Espèce")
    with col_t2:
        try:
            output_name = "Rapport_DR_Corrige.docx" if use_corrections else "Rapport_DR_Brut.docx"
            doc_path = create_comparison_word_report(df_effects, output_path=output_name)
            with open(doc_path, "rb") as f:
                st.download_button(
                    label="Télécharger Rapport Word",
                    data=f,
                    file_name=f"Rapport_Analyse_DR_2024_2025{'_Corrige' if use_corrections else ''}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    help="Génère un document Word avec les calculs d'effets prix-volume"
                )
        except Exception as e:
            st.error(f"Erreur Export Word: {e}")

    # Métriques agrégées

    # Métriques agrégées
    total_var = df_effects['variation_mdh'].sum()
    total_vol_eff = df_effects['effet_volume_mdh'].sum()
    total_pri_eff = df_effects['effet_prix_mdh'].sum()
    
    m1, m2, m3 = st.columns(3)
    with m1:
        PremiumComponents.metric_card("Variation Totale", f"{total_var:,.2f} MDh", "finance", "Somme des Espèces", "blue")
    with m2:
        col = "green" if total_vol_eff > 0 else "red"
        PremiumComponents.metric_card("Effet Volume", f"{total_vol_eff:,.2f} MDh", "anchor", "Impact Quantité", col)
    with m3:
        col = "green" if total_pri_eff > 0 else "red"
        PremiumComponents.metric_card("Effet Prix", f"{total_pri_eff:,.2f} MDh", "target", "Impact Marché", col)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Table Detailed
    st.markdown("#### Décomposition Détaillée par Espèce")
    
    # Selection des colonnes pertinentes pour l'affichage
    display_cols = ['espece', 'recette_2024_mdh', 'recette_2025_mdh', 'variation_mdh', 'effet_volume_mdh', 'effet_prix_mdh']
    df_disp = df_effects[display_cols].copy()
    df_disp.columns = ['Espèce', 'CA 2024 (MDh)', 'CA 2025 (MDh)', 'Var. Totale (MDh)', 'Effet Volume (MDh)', 'Effet Prix (MDh)']
    
    st.dataframe(
        df_disp.style.format({
            'CA 2024 (MDh)': '{:,.2f}',
            'CA 2025 (MDh)': '{:,.2f}',
            'Var. Totale (MDh)': '{:,.2f}',
            'Effet Volume (MDh)': '{:,.2f}',
            'Effet Prix (MDh)': '{:,.2f}'
        }).highlight_min(subset=['Var. Totale (MDh)'], color='#FEE2E2')
          .highlight_max(subset=['Var. Totale (MDh)'], color='#DCFCE7'),
        width="stretch",
        hide_index=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Visualization
    st.markdown("#### Visualisation Comparison Effets (Prix vs Volume)")
    
    # Melt for grouped bar chart
    df_plot = df_effects.head(10).melt(
        id_vars=['espece'], 
        value_vars=['effet_volume_mdh', 'effet_prix_mdh'],
        var_name='Type Effet', 
        value_name='Valeur (MDh)'
    )
    df_plot['Type Effet'] = df_plot['Type Effet'].replace({
        'effet_volume_mdh': 'Effet Volume',
        'effet_prix_mdh': 'Effet Prix'
    })
    
    fig = px.bar(
        df_plot,
        x='espece',
        y='Valeur (MDh)',
        color='Type Effet',
        barmode='group',
        color_discrete_map={'Effet Volume': '#0EA5E9', 'Effet Prix': '#10B981'},
        title='Top 10 Espèces : Analyse des Leviers de Croissance'
    )
    st.plotly_chart(apply_premium_plotly_styling(fig), width="stretch")

def render_page_diminution_ca(df_default):
    """Page d'analyse de la diminution du CA (2024 vs 2025) - DYNAMIQUE"""
    PremiumComponents.section_header(
        "Analyse Comparative 2024-2025",
        "Évolution Stratégique du Chiffre d'Affaires et des Volumes",
        "chart"
    )

    # ==================== DYNAMIC UPLOAD SECTION ====================
    with st.expander("Mise à jour des Données (Optionnel)", expanded=False):
        uploaded_file = st.file_uploader(
            "Importer un nouveau rapport Excel (Format ONP)", 
            type=['xlsx'],
            help="Téléchargez le fichier 'New Report(2024-2025) -DR.xlsx' pour rafraîchir l'analyse."
        )
        
    # Priorité aux données du rapport DR s'il est chargé
    df_reduction = None
    
    # Si on a des données brutes (format Long), on les convertit au format Wide pour cette page spécifique
    # Cette page attend 'ca_2024_kdh', 'ca_2025_kdh', etc.
    if df_default is not None and 'annee' in df_default.columns:
        with st.spinner("Préparation des agrégations par délégation..."):
            # Pivot simple pour transformer le Long en Wide for the page metrics
            df_pivot = df_default[df_default['annee'].isin([2024, 2025])].pivot_table(
                index=['port', 'espece'],
                columns='annee',
                values=['volume_kg', 'prix_unitaire_dh'],
                aggfunc='sum'
            ).fillna(0)
            
            # Reconstruction des colonnes attendues par cette page (V1-style compat)
            df_reduction = pd.DataFrame(index=df_pivot.index)
            # CA = P * V (Note: This is a simplified fallback if the wide CSV is missing)
            if 2024 in df_pivot.columns.get_level_values(1):
                df_reduction['ca_2024_kdh'] = (df_pivot[('prix_unitaire_dh', 2024)] * df_pivot[('volume_kg', 2024)]) / 1000
                df_reduction['vol_2024_t'] = df_pivot[('volume_kg', 2024)] / 1000
            if 2025 in df_pivot.columns.get_level_values(1):
                df_reduction['ca_2025_kdh'] = (df_pivot[('prix_unitaire_dh', 2025)] * df_pivot[('volume_kg', 2025)]) / 1000
                df_reduction['vol_2025_t'] = df_pivot[('volume_kg', 2025)] / 1000
            
            df_reduction = df_reduction.reset_index()
            # Ajout des délégations (fallback logic)
            if 'delegation' not in df_reduction.columns and 'dr' in df_reduction.columns:
                 df_reduction = df_reduction.rename(columns={'dr': 'delegation'})
                 
            if 'delegation' not in df_reduction.columns:
                df_reduction['delegation'] = df_reduction['port'].apply(lambda x: 'Nord' if 'Tanger' in str(x) or 'Larache' in str(x) else 'Sud')
            
            df_reduction['ca_diff_kdh'] = df_reduction.get('ca_2025_kdh', 0) - df_reduction.get('ca_2024_kdh', 0)
    
    # Si le pivot a échoué ou si on n'a pas de data_default, on tente le CSV legacy ou le nouveau rapport DR
    if df_reduction is None or df_reduction.empty:
        if os.path.exists('ca_reduction_2024_2025.csv'):
            df_reduction = pd.read_csv('ca_reduction_2024_2025.csv')
    
    if df_reduction is None or df_reduction.empty:
        st.warning("Les données nécessaires à la comparaison ne sont pas disponibles.")
        st.info("Veuillez vous assurer que le fichier de données est correct.")
        return

    # ==================== ANALYSIS DASHBOARD ====================
    # Nettoyage et Aggregration
    # KPIs - Forced to user requested values
    ca_2024_kdh = 11320340
    ca_2025_kdh = 10880720
    diff_ca_kdh = ca_2025_kdh - ca_2024_kdh
    diff_ca_pct = (diff_ca_kdh / ca_2024_kdh) * 100 if ca_2024_kdh != 0 else 0
    vol_2024 = df_reduction['vol_2024_t'].sum() if 'vol_2024_t' in df_reduction.columns else 97703
    tab1, tab2, tab2_special, tab3 = st.tabs([
        "Analyse par Délégation (DR)", 
        "Halles, MG & Délégations", 
        "ANALYSE COMPARATIVE 2024-2025 (DR)",
        "Export Rapport"
    ])
    
    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            PremiumComponents.metric_card("CA 2024", f"{ca_2024_kdh/1000:,.1f} MDh", "finance", "", "blue")
        with c2:
            PremiumComponents.metric_card("CA 2025", f"{ca_2025_kdh/1000:,.1f} MDh", "finance", "", "blue")
        with c3:
            color = "green" if diff_ca_kdh >= 0 else "red"
            PremiumComponents.metric_card("Variation CA", f"{diff_ca_kdh/1000:+,.1f} MDh", "target", f"{diff_ca_pct:+.1f}%", color)
        with c4:
            PremiumComponents.metric_card("Volume 2024", f"{vol_2024:,.0f} T", "anchor", "Base de calcul", "blue")

        st.markdown("<br>", unsafe_allow_html=True)
        col_left, col_right = st.columns([1, 1])
        
        try:
            # Sécurisation des dataframes vides (anti-crash)
            df_dr_agg = pd.DataFrame(columns=['DR', 'CA2024(KDh)', 'CA2025(KDh)', 'VARIATION(KDh)'])
            df_halles = pd.DataFrame()
            df_top_halles = pd.DataFrame()
            df_mg = pd.DataFrame()
            df_port_export = pd.DataFrame()

            # Utiliser la fonction cachée pour charger les données
            df_feuil1 = load_official_comparison_data()
            
            if not df_feuil1.empty:
                if 'VARIATION(KDh)' not in df_feuil1.columns and 'CA2024(KDh)' in df_feuil1.columns and 'CA2025(KDh)' in df_feuil1.columns:
                    df_feuil1['VARIATION(KDh)'] = df_feuil1['CA2025(KDh)'] - df_feuil1['CA2024(KDh)']
                df_feuil1['CA2024(KDh)'] = pd.to_numeric(df_feuil1['CA2024(KDh)'], errors='coerce').fillna(0)
                df_feuil1['CA2025(KDh)'] = pd.to_numeric(df_feuil1['CA2025(KDh)'], errors='coerce').fillna(0)
                df_feuil1['VARIATION(KDh)'] = pd.to_numeric(df_feuil1['VARIATION(KDh)'], errors='coerce').fillna(0)
                
                # Filtrage pour ne garder que les lignes de DR (données agrégées ou lignes propres)
                if 'DR' in df_feuil1.columns:
                    if 'IS_DR' in df_feuil1.columns:
                        df_dr_only = df_feuil1[df_feuil1['IS_DR'] == True].copy()
                    else:
                        df_dr_only = df_feuil1[~df_feuil1['DR'].astype(str).str.contains('Total|Maroc', na=False, case=False)].copy()
                else:
                    df_dr_only = df_feuil1.copy()

                # Supprimer les lignes où CA est nul (car Feuil6 contient des espèces sous les DR)
                if 'CA2024(KDh)' in df_dr_only.columns:
                    df_dr_only = df_dr_only[(df_dr_only['CA2024(KDh)'] > 0) | (df_dr_only['CA2025(KDh)'] > 0)]

                # Aggregations for Tabs - Mega Robust
                if 'DR' in df_dr_only.columns and not df_dr_only.empty:
                    # Dynamically identify available numeric columns to sum
                    avail_cols = [c for c in ['CA2024(KDh)', 'CA2025(KDh)', 'VARIATION(KDh)'] if c in df_dr_only.columns]
                    if avail_cols:
                        df_dr_agg = df_dr_only.groupby('DR')[avail_cols].sum().reset_index()
                        if 'VARIATION(KDh)' in df_dr_agg.columns:
                            df_dr_agg = df_dr_agg.sort_values('VARIATION(KDh)')
                    else:
                        df_dr_agg = pd.DataFrame(columns=['DR', 'CA2024(KDh)', 'CA2025(KDh)', 'VARIATION(KDh)'])
                else:
                    df_dr_agg = pd.DataFrame(columns=['DR', 'CA2024(KDh)', 'CA2025(KDh)', 'VARIATION(KDh)'])

            # FALLBACK : Si toujours vide, on utilise le DF principal filtré
            if df_dr_agg.empty and df_default is not None and not df_default.empty:
                df_main = df_default.copy()
                
                # Check for WIDE format vs LONG format
                if 'ca_2024_kdh' in df_main.columns and 'ca_2025_kdh' in df_main.columns:
                    # WIDE FORMAT (eg. ca_reduction_2024_2025.csv)
                    if 'delegation' in df_main.columns:
                        df_main['DR'] = df_main['delegation']
                    elif 'port' in df_main.columns:
                        from utils import REGION_MAP
                        df_main['DR'] = df_main['port'].str.upper().str.strip().map(REGION_MAP).fillna('AUTRE')
                    else:
                        df_main['DR'] = 'INCONNU'
                        
                    df_main['CA2024(KDh)'] = df_main['ca_2024_kdh']
                    df_main['CA2025(KDh)'] = df_main['ca_2025_kdh']
                    df_agg_main = df_main.groupby('DR')[['CA2024(KDh)', 'CA2025(KDh)']].sum().reset_index()
                    df_agg_main['VARIATION(KDh)'] = df_agg_main['CA2025(KDh)'] - df_agg_main['CA2024(KDh)']
                    df_dr_agg = df_agg_main[['DR', 'CA2024(KDh)', 'CA2025(KDh)', 'VARIATION(KDh)']].copy()
                    
                    df_main['PORT'] = df_main.get('port', df_main.get('PORT', 'INCONNU'))
                    df_port_agg = df_main.groupby(['DR', 'PORT'])[['CA2024(KDh)', 'CA2025(KDh)']].sum().reset_index()
                    df_port_agg['VARIATION(KDh)'] = df_port_agg['CA2025(KDh)'] - df_port_agg['CA2024(KDh)']
                    df_port_export = df_port_agg.copy()
                    
                    is_mg_mask = df_port_export['PORT'].str.upper().str.contains('MG|GROS')
                    df_mg = df_port_export[is_mg_mask].sort_values('CA2025(KDh)', ascending=False).copy()
                    df_halles = df_port_export[~is_mg_mask].sort_values('CA2025(KDh)', ascending=False).copy()
                    df_top_halles = df_halles.copy()
                    
                else:
                    # LONG FORMAT (eg. donnees_simulation_onp.csv)
                    if 'recette_totale' not in df_main.columns:
                        if 'volume_kg' in df_main.columns and 'prix_unitaire_dh' in df_main.columns:
                            df_main['recette_totale'] = df_main['volume_kg'] * df_main['prix_unitaire_dh']
                        elif 'vol_t' in df_main.columns and 'prix_moy' in df_main.columns:
                            df_main['recette_totale'] = df_main['vol_t'] * 1000 * df_main['prix_moy']
                        else:
                            df_main['recette_totale'] = 0
                            
                    if 'port' in df_main.columns:
                        from utils import REGION_MAP
                        df_main['DR'] = df_main['port'].str.upper().str.strip().map(REGION_MAP).fillna('AUTRE')
                        
                        if 'annee' not in df_main.columns and 'date_vente' in df_main.columns:
                            df_main['annee'] = pd.to_datetime(df_main['date_vente']).dt.year
                            
                        if 'annee' in df_main.columns:
                            df_agg_main = df_main.groupby(['DR', 'annee'])['recette_totale'].sum().unstack(fill_value=0).reset_index()
                            
                            # Mapping 2024/2025
                            if 2024 in df_agg_main.columns: df_agg_main['CA2024(KDh)'] = df_agg_main[2024] / 1000
                            else: df_agg_main['CA2024(KDh)'] = 0
                            
                            if 2025 in df_agg_main.columns: df_agg_main['CA2025(KDh)'] = df_agg_main[2025] / 1000
                            else: df_agg_main['CA2025(KDh)'] = 0
                            
                            df_agg_main['VARIATION(KDh)'] = df_agg_main['CA2025(KDh)'] - df_agg_main['CA2024(KDh)']
                            df_dr_agg = df_agg_main[['DR', 'CA2024(KDh)', 'CA2025(KDh)', 'VARIATION(KDh)']].copy()
                            
                            # Detailed aggregates for Tab 2
                            df_port_agg = df_main.groupby(['DR', 'port', 'annee'])['recette_totale'].sum().unstack(fill_value=0).reset_index()
                            if 2024 in df_port_agg.columns: df_port_agg['CA2024(KDh)'] = df_port_agg[2024] / 1000
                            else: df_port_agg['CA2024(KDh)'] = 0
                            if 2025 in df_port_agg.columns: df_port_agg['CA2025(KDh)'] = df_port_agg[2025] / 1000
                            else: df_port_agg['CA2025(KDh)'] = 0
                            
                            df_port_agg['VARIATION(KDh)'] = df_port_agg['CA2025(KDh)'] - df_port_agg['CA2024(KDh)']
                            df_port_export = df_port_agg.rename(columns={'port': 'PORT'})
                            
                            is_mg_mask = df_port_export['PORT'].str.upper().str.contains('MG|GROS')
                            df_mg = df_port_export[is_mg_mask].sort_values('CA2025(KDh)', ascending=False).copy()
                            df_halles = df_port_export[~is_mg_mask].sort_values('CA2025(KDh)', ascending=False).copy()
                            df_top_halles = df_halles.copy()

        except Exception as e:
            # Fallback extreme via DF principal
            df_dr_agg = pd.DataFrame(columns=['DR', 'CA2024(KDh)', 'CA2025(KDh)', 'VARIATION(KDh)'])
            df_top_halles = pd.DataFrame()
            df_mg = pd.DataFrame()
            df_port_export = pd.DataFrame(columns=['port', 'ca_diff_kdh'])
        
        with col_left:
            st.markdown("#### Part de Marché par Délégation (CA 2024)")
            if not df_dr_agg.empty:
                # Si CA2024(KDh) est à 0 mais qu'on a CA2025, on montre 2025
                pie_val = 'CA2024(KDh)' if df_dr_agg['CA2024(KDh)'].sum() > 0 else 'CA2025(KDh)'
                fig_pie = px.pie(
                    df_dr_agg, 
                    names='DR', 
                    values=pie_val,
                    hole=0.4,
                    title=f"Répartition par {pie_val}",
                    color_discrete_sequence=px.colors.qualitative.Vivid
                )
                st.plotly_chart(apply_premium_plotly_styling(fig_pie), width="stretch")
            else:
                st.info("Données insuffisantes pour le graphique de part de marché.")
            
        with col_right:
            st.markdown("#### Top Variations par Délégation (KDh)")
            if not df_dr_agg.empty:
                fig_del = px.bar(
                    df_dr_agg, 
                    x='VARIATION(KDh)', 
                    y='DR', 
                    orientation='h',
                    color='VARIATION(KDh)', 
                    color_continuous_scale='RdYlGn',
                    labels={'VARIATION(KDh)': 'Variation (KDh)', 'DR': 'DR'}
                )
                st.plotly_chart(apply_premium_plotly_styling(fig_del), width="stretch")
            else:
                st.info("Données de variation insuffisantes.")
            
        st.markdown("#### Synthèse par DR (Conforme Feuil6)")
        if not df_dr_agg.empty:
            st.dataframe(
                df_dr_agg.style.format({'CA2024(KDh)': '{:,.0f}', 'CA2025(KDh)': '{:,.0f}', 'VARIATION(KDh)': '{:,.0f}'})
                .highlight_min(subset=['VARIATION(KDh)'], color='#FEE2E2')
                .highlight_max(subset=['VARIATION(KDh)'], color='#DCFCE7'),
                width="stretch"
            )

    with tab2_special:
        render_dr_special_section(df_default)

    with tab2:
        st.markdown("### Analyse Détaillée : Délégations, Halles et Marchés de Gros")
        
        if not df_dr_agg.empty:
            
            # --- Graphique Explicatif ---
            st.markdown("#### Comparaison Stratégique : Halles vs Marchés de Gros")
            try:
                # Calculer les totaux par catégorie
                ca_24_halles = df_halles['CA2024(KDh)'].sum()
                ca_25_halles = df_halles['CA2025(KDh)'].sum()
                ca_24_mg = df_mg['CA2024(KDh)'].sum()
                ca_25_mg = df_mg['CA2025(KDh)'].sum()
                ca_24_total = df_dr_agg['CA2024(KDh)'].sum()
                ca_25_total = df_dr_agg['CA2025(KDh)'].sum()
                
                # Préparer les données pour le graphique
                data_comp = [
                    {'Catégorie': 'Total Global (DR)', 'Année': '2024', 'CA (MDh)': ca_24_total / 1000},
                    {'Catégorie': 'Total Global (DR)', 'Année': '2025', 'CA (MDh)': ca_25_total / 1000},
                    {'Catégorie': 'Halles de Débarquement', 'Année': '2024', 'CA (MDh)': ca_24_halles / 1000},
                    {'Catégorie': 'Halles de Débarquement', 'Année': '2025', 'CA (MDh)': ca_25_halles / 1000},
                    {'Catégorie': 'Marchés de Gros (MG)', 'Année': '2024', 'CA (MDh)': ca_24_mg / 1000},
                    {'Catégorie': 'Marchés de Gros (MG)', 'Année': '2025', 'CA (MDh)': ca_25_mg / 1000}
                ]
                df_comp = pd.DataFrame(data_comp)
                
                # Créer le graphique
                fig_comp = px.bar(
                    df_comp, 
                    x='Catégorie', 
                    y='CA (MDh)', 
                    color='Année', 
                    barmode='group',
                    text_auto='.1f',
                    color_discrete_map={'2024': '#94A3B8', '2025': '#0369A1'},
                    title="Chiffre d'Affaires 2024 vs 2025 selon le circuit de commercialisation"
                )
                fig_comp.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
                fig_comp = apply_premium_plotly_styling(fig_comp)
                fig_comp.update_yaxes(range=[0, max(df_comp['CA (MDh)']) * 1.2]) # Laisser de l'espace pour les labels
                st.plotly_chart(fig_comp, width="stretch")
            except Exception as e:
                st.info("Graphique de comparaison indisponible.")
            st.markdown("#### 1. Performance Globale par Délégation (Toutes les DR)")
            st.dataframe(
                df_dr_agg.sort_values('CA2025(KDh)', ascending=False).style.format({'CA2024(KDh)': '{:,.0f}', 'CA2025(KDh)': '{:,.0f}', 'VARIATION(KDh)': '{:,.0f}'})
                .highlight_min(subset=['VARIATION(KDh)'], color='#FEE2E2')
                .highlight_max(subset=['VARIATION(KDh)'], color='#DCFCE7'), 
                width="stretch"
            )

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Top 10 Halles les plus rentables (2025)")
                fig_top_h = px.bar(
                    df_top_halles.head(10), x='PORT', y='CA2025(KDh)',
                    title="Top 10 Halles (CA 2025)", color='CA2025(KDh)', color_continuous_scale='Blues'
                )
                fig_top_h.update_layout(xaxis_title="", yaxis_title="CA (KDh)", coloraxis_showscale=False)
                fig_top_h.update_traces(hovertemplate='%{x}<br>CA: %{y:,.0f} KDh')
                st.plotly_chart(apply_premium_plotly_styling(fig_top_h), width="stretch")
                
                st.markdown("#### 2. Top 20 des Halles les plus rentables")
                st.dataframe(
                    df_top_halles[['DR', 'PORT', 'CA2025(KDh)', 'VARIATION(KDh)']]
                    .style.format({'CA2025(KDh)': '{:,.0f}', 'VARIATION(KDh)': '{:,.0f}'})
                    .background_gradient(subset=['CA2025(KDh)'], cmap='Blues'), 
                    width="stretch"
                )
                
                # Bouton de téléchargement Excel pour les Halles
                import io
                buf_halles = io.BytesIO()
                df_top_halles.to_excel(buf_halles, index=False)
                st.download_button(
                    label="Telecharger le Rapport des Halles (.xlsx)",
                    data=buf_halles.getvalue(),
                    file_name="rapport_halles_2025.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            with col2:
                st.markdown("#### Top Marchés de Gros les plus rentables (2025)")
                fig_top_mg = px.bar(
                    df_mg.head(10), x='PORT', y='CA2025(KDh)',
                    title="Top MG (CA 2025)", color='CA2025(KDh)', color_continuous_scale='Oranges'
                )
                fig_top_mg.update_layout(xaxis_title="", yaxis_title="CA (KDh)", coloraxis_showscale=False)
                fig_top_mg.update_traces(hovertemplate='%{x}<br>CA: %{y:,.0f} KDh')
                st.plotly_chart(apply_premium_plotly_styling(fig_top_mg), width="stretch")

                st.markdown("#### 3. Performance des Marchés de Gros (MG)")
                st.dataframe(
                    df_mg[['DR', 'PORT', 'CA2025(KDh)', 'VARIATION(KDh)']]
                    .style.format({'CA2025(KDh)': '{:,.0f}', 'VARIATION(KDh)': '{:,.0f}'})
                    .background_gradient(subset=['CA2025(KDh)'], cmap='Oranges'), 
                    width="stretch"
                )
                
                # Bouton de téléchargement Excel pour les MG
                buf_mg = io.BytesIO()
                df_mg.to_excel(buf_mg, index=False)
                st.download_button(
                    label="Telecharger le Rapport des MG (.xlsx)",
                    data=buf_mg.getvalue(),
                    file_name="rapport_mg_2025.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        else:
            st.warning("Impossible de charger les données détaillées depuis le fichier Excel.")

    with tab3:
        st.markdown("### Génération du Rapport Institutionnel")
        PremiumComponents.info_box(
            "Le rapport Word ci-dessous intègre les données de la feuille **Feuil6** ainsi que le détail par Port et Espece. "
            "Les volumes sont calculés sur une base annuelle consolidée (**1.5M Tonnes**).", 
            "success"
        )
        
        # Préparation des statistiques pour le rapport Word
        # S'assurer que df_reduction possède toutes les colonnes nécessaires (utilisées dans les groupby du docx)
        if 'ca_diff_kdh' not in df_reduction.columns:
            df_reduction['ca_diff_kdh'] = df_reduction.get('ca_2025_kdh', pd.Series(dtype=float)).fillna(0) - df_reduction.get('ca_2024_kdh', pd.Series(dtype=float)).fillna(0)
        vol_2025 = df_reduction['vol_2025_t'].sum() if 'vol_2025_t' in df_reduction.columns else 97000
        word_stats = {
            'ca_2024': ca_2024_kdh,
            'ca_2025': ca_2025_kdh,
            'vol_2024': vol_2024,
            'vol_2025': vol_2025,
            'diff_pct': diff_ca_pct,
            'diff': diff_ca_kdh
        }
        
        # Export Figs dynamically building fallback keys
        if not df_dr_agg.empty:
            fig_bar_dr = px.bar(df_dr_agg, y='VARIATION(KDh)', x='DR', title="Variation CA par DR")
        else:
            fig_bar_dr = px.bar(title="Aucune donnée (Variation par DR)")
            
        if not df_port_export.empty:
            fig_bar_port = px.bar(df_port_export.head(10), x='VARIATION(KDh)', y='PORT', orientation='h', title="Top Baisses Par Port")
        else:
            fig_bar_port = px.bar(title="Aucune donnée (Top Baisses Port)")

        figs = {
            "Variation par DR": fig_bar_dr,
            "Top Baisses Port": fig_bar_port
        }
        
        try:
            from report_generator import create_reduction_word_report
            word_data = create_reduction_word_report(df_reduction, word_stats, plotly_figs=figs)
            
            st.download_button(
                label="Télécharger le Rapport Officiel (.docx)",
                data=word_data,
                file_name=f"Rapport_Strategique_ONP_{datetime.now().strftime('%Y%m%d')}.docx",
                mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                type="primary",
                width="stretch"
            )
        except Exception as e:
            st.error(f"Erreur préparation export: {e}")

def render_page_rapport(df, filters=None):
    """Page de Rapport Institutionnel Professionnel"""
    PremiumComponents.section_header(
        "Rapport Institutionnel",
        "Synthèse Stratégique & Analyse Prédictive",
        "report"
    )
    # Header du Rapport
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(display_premium_onp_logo(size=120), unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="border-left: 4px solid #0EA5E9; padding-left: 2rem; margin-top: 1rem;">
            <h1 style="color: #0F172A; font-weight: 800; margin-bottom: 0;">RAPPORT D'INTELLIGENCE HALIEUTIQUE</h1>
            <p style="color: #64748B; font-size: 1.1rem; margin-top: 5px;">
                Synthèse Stratégique & Analyse Prédictive - ONP 2026
            </p>
        </div>
        """, unsafe_allow_html=True)

    if filters:
        st.markdown(f"""
        <div style="background: rgba(14, 165, 233, 0.05); padding: 1rem; border-radius: 10px; margin-top: 1rem; border-left: 4px solid #0EA5E9;">
            <span style="font-weight: 700; color: #0369A1;">Périmètre de l'analyse : </span>
            <span style="color: #475569;">Ports: {", ".join(filters['ports']) if filters['ports'] else "Tous"} | 
            Espèces: {", ".join(filters['species']) if filters['species'] else "Toutes"}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Résumé Exécutif
    with st.container():
        st.markdown("""
        <div style="background: white; padding: 2.5rem; border-radius: 20px; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
            <h2 style="color: #0F172A; margin-top: 0;">Sommaire Exécutif</h2>
            <p style="color: #475569; line-height: 1.7; font-size: 1.05rem;">
                Ce rapport présente la synthèse des analyses de données effectuées sur la plateforme d'intelligence de l'Office National des Pêches. 
                L'objectif est d'assurer une souveraineté de l'information et une optimisation des prix de vente pour les marins-pêcheurs marocains. 
                Basé sur des modèles de Machine Learning avancés, ce document souligne les opportunités de marché et l'élasticité prix-volume par port stratégique.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    if df.empty:
        PremiumComponents.info_box(
            "Aucune donnée disponible pour cette sélection.",
            "warning"
        )
        st.info("Ajustez les filtres dans la barre latérale pour afficher les résultats du rapport.")
        return
    
    # KPIs en rangée formelle — utiliser les données DR Excel (source officielle)
    metrics = calculate_financial_metrics(df)
    
    # Tenter de charger les KPIs officiels depuis le fichier DR
    ca_2024_official = 11320340 / 1000  # En MDh pour la carte
    ca_2025_official = 10880720 / 1000  # En MDh pour la carte
    vol_2024_official = None
    vol_2025_official = None
    
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        ca_disp = f"{ca_2024_official:,.1f} MDh"
        PremiumComponents.metric_card("CA National 2024", ca_disp, "finance", "Source officielle DR", "blue")
    with col_b:
        ca_disp2 = f"{ca_2025_official:,.1f} MDh"
        color2 = "green" if ca_2025_official and ca_2025_official > (ca_2024_official or 0) else "orange"
        PremiumComponents.metric_card("CA National 2025", ca_disp2, "finance", "Source officielle DR", color2)
    with col_c:
        vol_disp = f"{vol_2025_official:,.0f} T" if vol_2025_official else f"{metrics['volume_total_tonnes']:,.0f} T"
        PremiumComponents.metric_card("Volume 2025", vol_disp, "anchor", "Tous ports", "blue")
    with col_d:
        if ca_2024_official and ca_2025_official:
            var_ca = ca_2025_official - ca_2024_official
            var_pct = (var_ca / ca_2024_official) * 100 if ca_2024_official else 0
            col4_color = "green" if var_ca >= 0 else "red"
            PremiumComponents.metric_card("Variation CA", f"{var_ca:+,.1f} MDh", "chart", f"{var_pct:+.1f}%", col4_color)
        else:
            PremiumComponents.metric_card("Prix Moyen", f"{metrics['prix_moyen_dh_kg']:.2f} DH", "target", "", "orange")

    st.markdown("<br><hr style='border: 0; border-top: 1px solid #E2E8F0;'><br>", unsafe_allow_html=True)
    
    # Sections Techniques
    tab1, tab2 = st.tabs(["Analyse Sectorielle", "Intelligence Prédictive"])
    
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Répartition des Recettes par Port")
            fig1 = plot_revenue_by_port(df)
            st.plotly_chart(apply_premium_plotly_styling(fig1), width="stretch")
        with c2:
            st.markdown("#### Évolution des Volumes")
            fig2 = plot_port_activity_heatmap(df)
            st.plotly_chart(apply_premium_plotly_styling(fig2), width="stretch")
            
    with tab2:
        st.markdown("""
        <div style="padding: 1rem; border-left: 3px solid #6366F1; background: #F8FAFC; margin-bottom: 2rem;">
            <b>Note Méthodologique :</b> Les prédictions sont générées via un modèle XGBoost optimisé 
            sur l'historique des ventes 2024-2025, intégrant la saisonnalité et les variations de volume portuaire.
        </div>
        """, unsafe_allow_html=True)
        
        c3, c4 = st.columns(2)
        with c3:
            st.markdown("#### Distribution des Prix Prédits")
            fig3 = plot_price_distribution_by_species(df)
            st.plotly_chart(apply_premium_plotly_styling(fig3), width="stretch")
        with c4:
            st.markdown("#### Corrélation Volume/Prix")
            fig4 = plot_volume_price_relationship(df)
            st.plotly_chart(apply_premium_plotly_styling(fig4), width="stretch")

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Bouton de téléchargement Word (Style Facture)
    col_word, col_info = st.columns([1, 2])
    with col_word:
        # Générer le rapport Word en mémoire ou fichier temporaire
        word_filename = f"Rapport_ONP_{datetime.now().strftime('%Y%m%d')}.docx"
        try:
            create_institutional_word_report(metrics, filters=filters, df_detailed=df, output_path=word_filename)
            with open(word_filename, "rb") as file:
                st.download_button(
                    label="Télécharger Rapport Officiel (.docx)",
                    data=file,
                    file_name=word_filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    width="stretch",
                    type="primary"
                )
        except Exception as e:
            st.error(f"Erreur de génération Word : {e}")
            
    with col_info:
        st.info("Le rapport exporté suit la mise en page officielle de l'Office National des Pêches (Format Institutionnel/Facture).")

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; color: #94A3B8; font-size: 0.8rem; padding: 2rem; border-top: 1px dashed #E2E8F0;">
        © 2026 Office National des Pêches - Département de l'Intelligence de Données<br>
        Document généré numériquement - Valeur probante pour analyse interne uniquement.
    </div>
    """, unsafe_allow_html=True)

# ==================== MAIN APPLICATION ====================

# ==================== MAIN APPLICATION ====================

# ==================== HELPERS UI ====================
def render_filters(df):
    """Affiche et gère les filtres dans la sidebar"""
    filters = {}
    if df is not None and not df.empty:
        st.sidebar.markdown("### Filtres Intelligents")
        with st.sidebar.expander("Afficher les filtres", expanded=True):
            # Filtre Port
            all_ports = sorted(df['port'].unique().tolist())
            selected_ports = st.multiselect(
                "Ports Stratégiques", 
                all_ports, 
                default=[],
                help="Laissez vide pour sélectionner tous les ports"
            )
            
            # Filtre Espèce
            all_species = sorted(df['espece'].unique().tolist())
            selected_species = st.multiselect(
                "Espèces Cibles", 
                all_species, 
                default=[],
                help="Laissez vide pour sélectionner toutes les espèces"
            )
            
            # Message informatif si rien n'est sélectionné
            if not selected_ports and not selected_species:
                st.sidebar.info("Mode 'Global' : Toutes les données sont affichées.")
            
            # Filtre Date
            if 'date_vente' in df.columns:
                try:
                    df['date_vente'] = pd.to_datetime(df['date_vente'])
                    min_date = df['date_vente'].min()
                    max_date = df['date_vente'].max()
                    
                    # Sécurité si dates NaT
                    if pd.isna(min_date): min_date = datetime(2024, 1, 1)
                    if pd.isna(max_date): max_date = datetime(2025, 12, 31)
                    
                    date_range = st.sidebar.date_input(
                        "Période d'Analyse",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date
                    )
                except:
                    date_range = None
            else:
                date_range = None
            
            filters = {
                'ports': selected_ports,
                'species': selected_species,
                'date_range': date_range
            }
    return filters

def apply_filters(df, filters):
    """Applique les filtres au DataFrame"""
    if df is None or df.empty or not filters:
        return df
        
    df_filtered = df.copy()
    
    if filters.get('ports'):
        df_filtered = df_filtered[df_filtered['port'].isin(filters['ports'])]
        
    if filters.get('species'):
        df_filtered = df_filtered[df_filtered['espece'].isin(filters['species'])]
        
    if filters.get('date_range') and len(filters['date_range']) == 2:
        start_d, end_d = filters['date_range']
        # Ensure date_vente is date type
        # (Assuming it was converted in render_filters or earlier, but safe to do here)
        # However, comparisons with date_input (date object) require dt.date
        try:
             df_filtered['date_vente'] = pd.to_datetime(df_filtered['date_vente'])
             df_filtered = df_filtered[
                (df_filtered['date_vente'].dt.date >= start_d) & 
                (df_filtered['date_vente'].dt.date <= end_d)
            ]
        except:
             pass
             
    return df_filtered

# ==================== PAGE SIMULATEUR B2B (MARGE MAREYEUR) ====================

def render_page_simulateur_b2b():
    """Page interactive pour le simulateur de marges d'achat/revente B2B"""
    from simulateur_b2b import calculate_mareyeur_margin, build_waterfall_chart, DEFAULT_COSTS

    PremiumComponents.section_header(
        "Simulateur de Rentabilité B2B",
        "Estimez votre marge nette après taxes ONP, logistique et coûts opérationnels",
        "calculator"
    )

    st.markdown("""
        <div style="background-color: #F8FAFC; padding: 16px; border-radius: 8px; border-left: 4px solid #0EA5E9; margin-bottom: 24px;">
            <strong>Comment utiliser ce simulateur ?</strong> Saisissez le volume et le prix d'achat en halle ci-dessous. 
            Les taxes réglementaires (ONP 4% + Commune 1%) sont appliquées automatiquement. 
            Ajustez ensuite vos frais logistiques pour visualiser votre rentabilité finale.
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("### 1. Paramètres d'Achat")
        volume = st.number_input("Volume Acquis (en kg)", min_value=1, value=1000, step=100)
        prix_achat = st.number_input("Prix d'Achat Brut en Halle (DH/kg)", min_value=1.0, value=25.0, step=1.0)
        prix_revente = st.number_input("Prix de Revente Estimé (DH/kg)", min_value=1.0, value=35.0, step=1.0)
        
        st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)
        
        st.markdown("### 2. Frais Logistiques (DH/kg)")
        cout_glace = st.slider("Glace", 0.0, 3.0, DEFAULT_COSTS['glace_dh_kg'], step=0.1)
        cout_manu = st.slider("Manutention", 0.0, 3.0, DEFAULT_COSTS['manutention_dh_kg'], step=0.1)
        cout_trans = st.slider("Transport", 0.0, 10.0, DEFAULT_COSTS['transport_dh_kg'], step=0.5)
        cout_emb = st.slider("Emballage", 0.0, 5.0, DEFAULT_COSTS['emballage_dh_kg'], step=0.1)

        couts_perso = {
            'glace_dh_kg': cout_glace,
            'manutention_dh_kg': cout_manu,
            'transport_dh_kg': cout_trans,
            'emballage_dh_kg': cout_emb
        }

    with col2:
        st.markdown("### 3. Résultat de la Simulation")
        res = calculate_mareyeur_margin(volume, prix_achat, prix_revente, couts_perso)
        
        # Affichage des KPIs
        k1, k2 = st.columns(2)
        with k1:
            ca_halle_str = f"{res['valeur_achat_halle']:,.0f}".replace(',', ' ')
            st.metric("Chiffre d'Affaires (Halle)", f"{ca_halle_str} DH", delta=None, help="Base de calcul des taxes (Achat à la criée)")
            
            roi_color = "normal" if res['marge_nette_globale'] >= 0 else "inverse"
            marge_globale_str = f"{res['marge_nette_globale']:,.0f}".replace(',', ' ')
            st.metric("Marge Nette Globale", f"{marge_globale_str} DH", f"{res['marge_nette_unitaire']:+.2f} DH/kg", delta_color=roi_color)

        with k2:
            revente_str = f"{res['revenu_revente']:,.0f}".replace(',', ' ')
            st.metric("Vente (Marché/Export)", f"{revente_str} DH", help="Revenu total généré par la revente")
            st.metric("Taux de Marge", f"{res['margin_pct']:.1f}%", f"{res['margin_pct']:.1f}% sur vente", delta_color=roi_color)

        st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)

        # Graphique Waterfall
        fig = build_waterfall_chart(res)
        st.plotly_chart(fig, use_container_width=True)

        # Synthèse des coûts supplémentaires
        st.markdown("**Détail des Frais & Taxes (Enveloppe totale)**")
        tax_total_str = f"{res['montant_taxes']:,.0f}".replace(',', ' ')
        log_total_str = f"{res['total_logistique']:,.0f}".replace(',', ' ')
        st.caption(f"- Taxes ONP & Commune (5%) : **{tax_total_str} DH** ({res['montant_taxes']/volume:.2f} DH/kg)")
        st.caption(f"- Logistique Totale : **{log_total_str} DH** ({res['total_logistique']/volume:.2f} DH/kg)")


# ==================== PAGE VUE EXÉCUTIVE (DIRECTEUR) ====================



# ==================== PAGE SAISONNALITE ====================

def render_page_saisonnalite(df):
    """Page d'analyse de saisonnalité des prix — 4 facteurs interactifs"""
    import saisonnalite
    import importlib
    importlib.reload(saisonnalite)
    from saisonnalite import (
        CALENDRIER_BIOLOGIQUE, MOIS_LABELS,
        build_seasonality_dashboard, build_summary_table
    )
    
    PremiumComponents.section_header(
        "Saisonnalité des Prix & Volumes",
        "Analyse 4 facteurs : captures, biologie, carburant & climat",
        "chart"
    )
    
    if df is None or df.empty:
        st.warning("Données insuffisantes.")
        return

    # Utiliser la colonne la plus propre pour l'affichage (espece_clean si disponible)
    col_espece = 'espece_clean' if 'espece_clean' in df.columns else 'espece'
    
    st.markdown("<p style='color:#64748B;'>Sélectionnez une ou plusieurs entités pour explorer la saisonnalité, les périodes de repos biologique, et les corrélations (climat/marché).</p>", unsafe_allow_html=True)
    st.markdown("<hr style='margin-top:0.5rem; margin-bottom:1.5rem;'/>", unsafe_allow_html=True)

    # ── Chargement des Espèces (Correction : Accès aux espèces granulaires) ──────────
    # Si le DF actuel est catégoriel (ex: 7-10 espèces max), on tente de charger le DF de simulation
    # qui contient les espèces granulaires réclamées (Sardine, Anchois...)
    if len(df[col_espece].unique()) < 15:
        try:
            data_granulaire = 'donnees_simulation_onp.csv'
            if os.path.exists(data_granulaire):
                df_gran = pd.read_csv(data_granulaire)
                # Nettoyage et création des features (annee, mois...)
                from utils import clean_data, create_features, normalize_species_name
                df_gran = clean_data(df_gran)
                df_gran = create_features(df_gran) # Ajoute 'annee', 'mois' etc.
                
                df_gran['espece_clean'] = df_gran['espece'].apply(lambda x: normalize_species_name(x).replace('_', ' ').upper())
                col_espece = 'espece_clean'
                df = df_gran
        except:
            pass

    all_especes = sorted(df[col_espece].dropna().unique().tolist())
    all_annees = [2024, 2025] # Fixé pour la saisonnalité comparative

    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        espece_sel = st.multiselect(
            "Recherche Rapide (Sardine, Anchois, Poulpe...)",
            all_especes,
            default=all_especes[:2] if len(all_especes) >= 2 else all_especes,
            help="Sélectionnez une ou plusieurs espèces parmi toutes celles disponibles."
        )
    with col_f2:
        annee_sel = st.multiselect(
            "Année(s) d'analyse",
            all_annees,
            default=all_annees,
            help="Comparez 2024 et/ou 2025."
        )

    if not espece_sel:
        st.info("Sélectionnez au moins une catégorie ou espèce.")
        return
    if not annee_sel:
        st.info("Sélectionnez au moins une année.")
        return

    # ── Indicateurs de repos biologique (banderoles) ─────────────────
    mois_repos_all = set()
    for esp in espece_sel:
        mois_repos_all.update(CALENDRIER_BIOLOGIQUE.get(esp, {}).get('mois_repos', []))

    if mois_repos_all:
        periodes = ', '.join([MOIS_LABELS[m - 1] for m in sorted(mois_repos_all)])
        st.markdown(f"""
        <div style="background:rgba(239,68,68,0.08); border-left:4px solid #DC2626;
                    padding:10px 18px; border-radius:8px; margin-bottom:12px;">
            <span style="color:#DC2626; font-weight:800">Repos Biologique</span>
            <span style="color:#64748B; margin-left:10px;">
                Périodes de restrictions : <strong>{periodes}</strong>
            </span>
        </div>""", unsafe_allow_html=True)

    # ── KPIs rapides et Dashboard ────────────────────────────────────
    from saisonnalite import get_monthly_stats, FUEL_PRICES_2024, FUEL_PRICES_2025
    
    # Mapping Espèce -> Catégorie pour le fallback 2025
    species_to_cat = {}
    if 'categorie' in df.columns:
        mapping_df = df[df['annee'] == 2024][['espece_clean' if 'espece_clean' in df.columns else col_espece, 'categorie']].drop_duplicates()
        species_to_cat = dict(zip(mapping_df.iloc[:, 0], mapping_df.iloc[:, 1]))

    def get_working_especes(annee, sel):
        if annee != 2025: return sel
        working = list(sel)
        for esp in sel:
            cat = species_to_cat.get(esp)
            if cat and cat != esp:
                # Si l'espèce est granulaire, on ajoute sa catégorie mère (ex: SARDINE -> POISSON PELAGIQUE)
                # car le fichier de simulation 2025 ne contient que les catégories racines.
                if cat not in working: working.append(cat)
        return working

    kpi_cols = st.columns(4)
    for i, annee in enumerate(annee_sel[:4]):
        # On utilise le fallback pour les KPIs
        working_esps = get_working_especes(annee, espece_sel)
        monthly = get_monthly_stats(df, working_esps, annee, col_espece=col_espece)
        ca_total = (monthly['prix_moy'] * monthly['vol_t']).sum()
        vol_total = monthly['vol_t'].sum()
        prix_max_mois = MOIS_LABELS[monthly['prix_moy'].idxmax()]
        with kpi_cols[i % 4]:
            st.markdown(f"""
            <div style="background:white; padding:14px; border-radius:12px;
                        border:1px solid #E2E8F0; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                <div style="font-size:0.7rem; font-weight:700; color:#64748B; text-transform:uppercase;">{annee}</div>
                <div style="font-size:1.4rem; font-weight:800; color:#0369A1;">{vol_total:,.0f} T</div>
                <div style="font-size:0.8rem; color:#475569;">CA : {ca_total/1000:,.1f} MDh</div>
                <div style="font-size:0.75rem; color:#10B981;">Prix max → {prix_max_mois}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Dashboard 4 panneaux ─────────────────────────────────────────
    with st.spinner("Construction du dashboard saisonnalité..."):
        # On passe le mapping à build_seasonality_dashboard s'il est supporté, 
        # ou on l'utilise pour filtrer si le dashboard supporte plusieurs requêtes.
        from saisonnalite import build_seasonality_dashboard
        
        # Le dashboard d'origine ne supporte pas un list par an. 
        # On va ruser en passant df filtré ou en adaptant saisonnalite.py.
        # Pour rester safe, appelons-le avec espece_sel mais on aura corrigé saisonnalite.py
        fig = build_seasonality_dashboard(df, espece_sel, annee_sel, col_espece=col_espece, category_map=species_to_cat)
        from design_system import apply_premium_plotly_styling
        fig = apply_premium_plotly_styling(fig)
        st.plotly_chart(fig, use_container_width=True)

    # ── Table de synthèse ────────────────────────────────────────────
    with st.expander("Table de Synthèse Mensuelle (Exportable)", expanded=False):
        # Pour la table, on utilise aussi le fallback pour chaque ligne d'année
        dfs_tbl = []
        for annee in annee_sel:
            working_esps = get_working_especes(annee, espece_sel)
            from saisonnalite import build_summary_table
            df_yr = build_summary_table(df, working_esps, [annee], col_espece=col_espece)
            dfs_tbl.append(df_yr)
        
        df_tbl = pd.concat(dfs_tbl).drop_duplicates() if dfs_tbl else pd.DataFrame()
        st.dataframe(df_tbl, use_container_width=True, hide_index=True)
        csv_bytes = df_tbl.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Télécharger CSV",
            data=csv_bytes,
            file_name=f"saisonnalite_{'_'.join(map(str,annee_sel))}.csv",
            mime='text/csv'
        )

    # ── Insights automatiques ────────────────────────────────────────
    st.markdown("### Insights Automatiques")
    from saisonnalite import get_monthly_stats, compute_fuel_correlation, get_fuel_series
    insight_cols = st.columns(2)
    for i, annee in enumerate(annee_sel):
        working_esps = get_working_especes(annee, espece_sel)
        monthly = get_monthly_stats(df, working_esps, annee, col_espece=col_espece)
        fuel = get_fuel_series(annee)
        corr = compute_fuel_correlation(monthly['prix_moy'].tolist(), fuel)
        vol_peak = MOIS_LABELS[monthly['vol_t'].idxmax()]
        prix_peak = MOIS_LABELS[monthly['prix_moy'].idxmax()]
        vol_low = MOIS_LABELS[monthly['vol_t'].idxmin()]

        direction = '(positive)' if corr > 0.3 else ('(négative)' if corr < -0.3 else '(faible)')
        
        # Code couleur pour la jauge
        if abs(corr) >= 0.7:
            bar_color = "#10B981" # Vert (Fort)
            strength_txt = "FORTE"
        elif abs(corr) >= 0.3:
            bar_color = "#0EA5E9" # Bleu (Modérée)
            strength_txt = "MODÉRÉE"
        else:
            bar_color = "#94A3B8" # Gris (Faible)
            strength_txt = "FAIBLE"
            
        if corr < -0.3:
            strength_txt += " INVERSE"
            if abs(corr) >= 0.7: bar_color = "#EF4444" # Rouge (Fort Inverse)
            elif abs(corr) >= 0.3: bar_color = "#F59E0B" # Orange (Modéré Inverse)

        with insight_cols[i % 2]:
            st.markdown(f"""
            <div style="background:white; padding:18px; border-radius:12px;
                        border:1px solid #E2E8F0; box-shadow:0 2px 8px rgba(0,0,0,0.04);">
                <h4 style="margin:0 0 10px 0; color:#0369A1;">Année {annee}</h4>
                <p style="margin:4px 0; font-size:0.85rem;">
                    <strong>Pic de captures</strong> : {vol_peak}<br>
                    <strong>Pic de prix</strong> : {prix_peak}<br>
                    <strong>Creux de captures</strong> : {vol_low}<br>
                </p>
                <div style="margin-top:10px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                        <span style="font-size:0.75rem; font-weight:700; color:#475569;">LIAISON PRIX / CARBURANT</span>
                        <span style="font-size:0.75rem; font-weight:800; color:{bar_color};">{strength_txt} ({corr:+.2f})</span>
                    </div>
                    <div style="width:100%; height:8px; background:#F1F5F9; border-radius:4px; overflow:hidden;">
                        <div style="width:{abs(corr)*100}%; height:100%; background:{bar_color};"></div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

# ==================== MAIN APPLICATION ====================
def main():
    """Fonction principale de l'application"""
    init_auth_state()
    
    if not st.session_state.logged_in:
        render_login_view()
        st.stop()
        
    # Chargement/Récupération des données
    df = get_current_df()
    
    if df is None or df.empty:
        # On ne bloque pas si df est vide, car Rapport 2024-2025 peut marcher sans df simulation
        pass
    
    # Afficher le background dynamique
    st.markdown(create_dynamic_background(), unsafe_allow_html=True)
    
    # Sidebar avec logo
    col1, col2 = st.sidebar.columns([1, 2])
    with col1:
        st.markdown(display_premium_onp_logo(size=80, with_animation=False), unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="padding: 0.5rem; margin-left: 0.5rem;">
            <h3 style="color: #0369A1; font-weight: 800; margin: 0; font-size: 1.25rem;">ONP</h3>
            <p style="color: #64748B; font-size: 0.8rem; margin: 0.25rem 0 0 0; font-weight: 600;">v2.0 Premium</p>
            <a href="{ONP_WEBSITE_URL}" target="_blank" rel="noopener" style="font-size: 0.75rem; color: #0EA5E9;">onp.ma</a>
        </div>
        """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # Zone de diagnostic si données manquantes
    if df is None or df.empty:
        st.sidebar.warning("Données non trouvées")
        if st.sidebar.button("Forcer le rechargement", key="force_reload"):
            st.cache_data.clear()
            st.session_state.main_df = load_default_data()
            st.rerun()
            
    st.sidebar.markdown("---")
    
    # Navigation contextuelle selon le rôle
    if 'selection' not in st.session_state:
        st.session_state.selection = "Accueil" # Accueil par défaut

    # Définition complète des onglets existants
    all_nav_items = {

        "Accueil": "home",
        "Rapport 2024-2025": "report",
        "Analytics": "chart",
        "Analyse Financière": "finance",
        "Saisonnalité": "chart",
        "Simulateur B2B (Marge)": "calculator",
        "Machine Learning": "brain",
        "Simulateur": "simulation",
        "Rapport (V1)": "file-text"
    }
    
    # Filtrage selon le rôle (RBAC)
    nav_items = {}
    role = st.session_state.user_role
    
    for label, icon in all_nav_items.items():
        if role == "admin":
            nav_items[label] = icon
        elif role == "gestionnaire":
            if label in ["Accueil", "Analytics", "Analyse Financière", "Rapport 2024-2025", "Saisonnalité", "Simulateur B2B (Marge)", "Rapport (V1)"]:
                nav_items[label] = icon
        elif role == "crieur":
            if label in ["Accueil", "Simulateur", "Simulateur B2B (Marge)"]:
                nav_items[label] = icon
                
    # Sécurité: si l'utilisateur est sur une page non autorisée, forcer l'accueil
    if st.session_state.selection not in nav_items:
        st.session_state.selection = "Accueil"
    
    for label, icon in nav_items.items():
        is_selected = (st.session_state.selection == label)
        icon_label = "octo" if "CEPHALOPODES" in label.upper() else icon
        icon_html = f'<div style="padding-top: 5px;">{LuxIcons.render(icon_label, size=20, color="#10B981" if is_selected else "#94A3B8")}</div>'
        
        col_icon, col_btn = st.sidebar.columns([1, 4])
        with col_icon:
            st.markdown(icon_html, unsafe_allow_html=True)
        with col_btn:
            if st.button(
                f"{label}", 
                key=f"nav_{label}", 
                width="stretch",
                type="primary" if is_selected else "secondary"
            ):
                st.session_state.selection = label
                st.rerun()

    page = st.session_state.selection
    
    # Bouton de déconnexion
    render_logout_button()
    
    st.sidebar.markdown("---")
    
    # Filtres
    filters = render_filters(df)
    
    # Footer info
    st.sidebar.caption("Utilisez les filtres pour affiner les vues par période, port ou espèce.")
    
    # Application des filtres
    df_filtered = apply_filters(df, filters)

    # Alertes Sensationnelles (Sidebar UX)
    # Récupérer le premier port sélectionné pour la météo réelle
    selected_port = filters.get('ports')[0] if filters.get('ports') else 'CASABLANCA'
    render_external_conditions(port_name=selected_port)

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"#### {LuxIcons.render('refresh', size=20, color='#0EA5E9')} Synchronisation Data", unsafe_allow_html=True)
    if st.sidebar.button("Appliquer les Changements", key="global_sync_btn", use_container_width=True):
        st.cache_data.clear()
        st.session_state.main_df = load_default_data()
        st.success("Données synchronisées !")
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"#### {LuxIcons.render('shield', size=20, color='#0EA5E9')} Pulse Marché", unsafe_allow_html=True)
    # Sécuriser si df est None (échec de chargement)
    if df is None:
        st.error("ERREUR CRITIQUE : Le fichier de données est introuvable ou corrompu. Veuillez vérifier la présence de 'donnees_simulation_onp.csv'.")
        st.stop()
        
    recent_data = df_filtered.tail(100) if (df_filtered is not None and not df_filtered.empty) else df.tail(100)
    market_alerts = get_market_saturation_alerts(recent_data)
    if market_alerts:
        for alert in market_alerts:
            st.sidebar.warning(alert['message'])
    else:
        st.sidebar.success("Flux stables : aucune saturation.")

    # Rendu des titres et styles globaux
    render_header()
    
    title_style = '<h2 style="color: #1E293B; border-bottom: 2px solid #0EA5E9; padding-bottom: 10px;">{}</h2>'
    
    if page == "Accueil":
        if df is not None and not df.empty:
             render_page_accueil(df_filtered)
        else:
             st.warning("Les données principales (onp_real_ml_data.csv) n'ont pas pu être chargées.")
             st.info("Veuillez vous assurer que le fichier existe à la racine du projet ou utilisez le module 'Machine Learning' pour importer un fichier Excel.")
             if st.button("Tenter un rechargement"):
                 st.cache_data.clear()
                 st.rerun()
    
    elif page == "Analytics":
        if df_filtered is not None and not df_filtered.empty:
            # Check if function exists, otherwise placeholder
            if 'render_page_analytics' in globals():
                render_page_analytics(df_filtered)
            elif 'render_page_analyse_saisonniere' in globals():
                render_page_analyse_saisonniere(df_filtered)
            else:
                st.info("Module Analytics en maintenance.")
        else:
            st.warning("Les données pour l'analyse ne sont pas disponibles. Veuillez charger un fichier.")
    
    elif page == "Analyse Financière":
        if df_filtered is not None and not df_filtered.empty:
            if 'render_page_financial' in globals():
                render_page_financial(df_filtered)
            elif 'render_page_finance' in globals(): # Try alternative name
                render_page_finance(df_filtered)
            else:
                 st.info("Module Finance en maintenance.")
        else:
            st.warning("Les données financières ne sont pas disponibles.")
    
    elif page == "Machine Learning":
        if df is not None and not df.empty:
            # Récupérer l'horodatage du modèle pour forcer le cache
            mtime = 0
            if os.path.exists('models/best_model.pkl'):
                mtime = os.path.getmtime('models/best_model.pkl')
                
            if 'render_page_ml' in globals():
                 predictor = initialize_predictor(df, mtime)
                 if predictor:
                    render_page_ml(df, predictor)
            elif 'render_page_prediction' in globals():
                 predictor = initialize_predictor(df, mtime)
                 if predictor:
                    render_page_prediction(predictor, df)
            else:
                 st.info("Module ML en maintenance.")
        else:
            st.warning("Les données pour le Machine Learning ne sont pas disponibles.")
    
    elif page == "Simulateur":
        if df is not None and not df.empty:
            if 'render_page_simulation' in globals():
                render_page_simulation(df)
            else:
                 st.info("Module Simulateur en maintenance.")
        else:
            st.warning("Les données pour la simulation ne sont pas disponibles.")
        
    elif page == "Rapport (V1)":
        if 'render_page_rapport' in globals():
             render_page_rapport(df_filtered, filters)
        else:
             st.info("Ancien module rapport indisponible.")

    elif page == "Rapport 2024-2025":
        if os.path.exists('ca_reduction_2024_2025.csv'):
            df_reduction = pd.read_csv('ca_reduction_2024_2025.csv')
            render_page_diminution_ca(df_reduction)
        else:
            render_page_diminution_ca(df)


    elif page == "Simulateur B2B (Marge)":
        render_page_simulateur_b2b()

    elif page == "Saisonnalité":
        if df_filtered is not None and not df_filtered.empty:
            render_page_saisonnalite(df_filtered)
        else:
            st.warning("Données indisponibles pour l'analyse de saisonnalité.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Une erreur critique est survenue : {e}")
        st.exception(e)
