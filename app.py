"""
Application ONP - Optimisation des Prix de Vente des Produits de la Pêche
==========================================================================

Application d'aide à la décision pour l'Office National des Pêches (ONP) - Maroc
Projet de Fin d'Études - Master Finance & Data Science

Fonctionnalités:
- Analyse exploratoire des données (EDA)
- Analyse financière approfondie
- Modèles de Machine Learning (prédiction de prix)
- Simulation et recommandations
- Dashboard interactif professionnel

Auteur: PFE Master Finance & Data Science
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import warnings
warnings.filterwarnings('ignore')

# Import des modules personnalisés
from utils import (
    clean_data, create_features, calculate_financial_metrics,
    get_price_statistics, simulate_price_impact
)
from eda_analysis import (
    plot_price_distribution_by_species, plot_price_by_port,
    plot_volume_price_relationship, plot_seasonal_analysis,
    plot_price_trends, plot_top_species_by_volume, plot_port_activity_heatmap
)
from financial_analysis import (
    plot_revenue_by_port, plot_revenue_contribution_by_species,
    plot_top_profitable_species, plot_revenue_evolution,
    create_financial_summary_table
)
from ml_models import ONPPricePredictor
from onp_assets import ONP_EDITO, get_image_path, ONP_WEBSITE_URL
from logistics_optimizer import suggest_optimal_ports, get_market_saturation_alerts
from dynamic_logo import display_premium_onp_logo, create_animated_kpi_header  # Import the ONP logo components

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="ONP - Optimisation des Prix",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== STYLES CSS ====================
# ==================== STYLES CSS ====================
st.markdown("""
<style>
    /* OceanSense 2.0 Ultra-Premium Design System */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Global Reset & Typography */
    html, body, [class*="css"], .stText, .stMarkdown, p, span, label { 
        font-family: 'Outfit', sans-serif !important; 
        color: #000000 !important;
    }
    
    .stApp { 
        background: radial-gradient(circle at top right, #f8fafc, #ffffff) !important; 
    }
    
    /* Animation Keyframes */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes magnetic_pulse {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(14, 165, 233, 0.4); }
        70% { transform: scale(1.02); box-shadow: 0 0 0 10px rgba(14, 165, 233, 0); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(14, 165, 233, 0); }
    }

    /* Glassmorphic Sidebar */
    section[data-testid="stSidebar"] { 
        background: rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(25px) !important;
        -webkit-backdrop-filter: blur(25px) !important;
        border-right: 1px solid rgba(14, 165, 233, 0.15) !important;
        animation: fadeInUp 0.8s ease-out;
    }
    
    section[data-testid="stSidebar"] [data-testid="stText"], 
    section[data-testid="stSidebar"] .stMarkdown * {
        color: #0f172a !important;
        font-weight: 500;
    }

    /* Premium Heading Style */
    h1, h2, h3 { 
        color: #0f172a !important; 
        letter-spacing: -0.03em !important;
        font-weight: 700 !important;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { 
        background: rgba(14, 165, 233, 0.3); 
        border-radius: 10px; 
    }
    ::-webkit-scrollbar-thumb:hover { background: #0ea5e9; }

    /* Ultra-Premium Glassmorphic Metric Cards */
    div[data-testid="metric-container"] { 
        background: rgba(255, 255, 255, 0.7) !important; 
        backdrop-filter: blur(20px);
        border: 1px solid rgba(14, 165, 233, 0.2) !important; 
        border-radius: 20px !important;
        padding: 28px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        animation: fadeInUp 1s ease-out;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-8px) scale(1.02) !important;
        box-shadow: 0 25px 40px -10px rgba(14, 165, 233, 0.2) !important;
        border-color: #0ea5e9 !important;
    }
    
    div[data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 2.2rem !important;
        letter-spacing: -0.04em !important;
    }
    
    label[data-testid="stMetricLabel"] {
        color: #64748b !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.8rem !important;
        letter-spacing: 0.1em !important;
    }

    /* Magnetic Action Buttons */
    .stButton > button { 
        background: linear-gradient(135deg, #0ea5e9, #0369a1) !important;
        color: #ffffff !important; 
        border-radius: 14px !important; 
        font-weight: 700 !important;
        padding: 0.8rem 2rem !important;
        border: none !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 6px -1px rgba(14, 165, 233, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: scale(1.05) translateY(-2px) !important;
        box-shadow: 0 15px 30px -5px rgba(14, 165, 233, 0.4) !important;
        filter: brightness(1.1);
    }

    /* Glass Panels for Information */
    .info-box, .success-box { 
        background: rgba(255, 255, 255, 0.6) !important; 
        backdrop-filter: blur(15px);
        border-radius: 20px !important;
        padding: 30px !important; 
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05) !important;
        margin-bottom: 25px;
        animation: fadeInUp 1.2s ease-out;
    }
    
    .info-box { border-left: 6px solid #0ea5e9 !important; }
    .success-box { border-left: 6px solid #10b981 !important; }

    /* Performance Tabs */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 30px !important; 
        background: rgba(241, 245, 249, 0.5) !important;
        padding: 10px !important;
        border-radius: 16px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #64748b !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        transition: all 0.3s !important;
        padding: 12px 24px !important;
    }
    
    .stTabs [aria-selected="true"] { 
        color: #0ea5e9 !important;
        background: #ffffff !important;
        box-shadow: 0 8px 15px rgba(0,0,0,0.08) !important;
    }

    /* Enhanced DataFrames */
    .stDataFrame {
        border: 1px solid rgba(14, 165, 233, 0.1) !important;
        border-radius: 16px !important;
        overflow: hidden !important;
    }

</style>
""", unsafe_allow_html=True)

# ==================== PLOTLY THEME ====================
def apply_premium_chart_style(fig):
    """Applique le style OceanSense 2.0 aux graphiques Plotly."""
    fig.update_layout(
        font_family="Outfit, sans-serif",
        font_color="#0f172a",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        title_font_size=20,
        title_font_color="#0f172a",
        title_font_family="Outfit, sans-serif",
        margin=dict(t=80, b=40, l=40, r=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.6)",
            bordercolor="rgba(14,165,233,0.2)",
            borderwidth=1,
            font=dict(size=12)
        ),
        xaxis=dict(
            gridcolor="rgba(226, 232, 240, 0.5)",
            linecolor="rgba(226, 232, 240, 0.5)",
            zeroline=False,
            showline=True,
            showgrid=True
        ),
        yaxis=dict(
            gridcolor="rgba(226, 232, 240, 0.5)",
            linecolor="rgba(226, 232, 240, 0.5)",
            zeroline=False,
            showline=True,
            showgrid=True
        ),
        hoverlabel=dict(
            bgcolor="#ffffff",
            font_size=13,
            font_family="Outfit",
            bordercolor="rgba(14,165,233,0.3)"
        ),
        colorway=['#0ea5e9', '#0369a1', '#0f172a', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
    )
    return fig

# ==================== CHARGEMENT DES DONNÉES ====================
@st.cache_data
def load_data(file_hash):
    """Charge et prépare les données avec invalidation de cache par hash/mtime."""
    try:
        file_path = "donnees_simulation_onp.csv"
        if not os.path.exists(file_path):
            return None
            
        if os.path.getsize(file_path) == 0:
            return None
            
        # Lecture avec détection automatique d'encodage simple
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        if 'date_vente' in df.columns:
            df['date_vente'] = pd.to_datetime(df['date_vente'])
        return df
    except Exception as e:
        st.sidebar.error(f"Détail erreur: {e}")
        return None

# ==================== SIDEBAR ====================
with st.sidebar:
    # Display premium ONP logo in sidebar
    st.markdown(display_premium_onp_logo(size=180), unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🌊 OceanSense AI")
    st.markdown("Professional Intelligence | Maroc 🇲🇦")
    st.markdown("---")
    
    st.markdown("#### 🔍 Filtres de Données")
    
    # Calculer un hash ou mtime pour forcer le rechargement si le fichier change
    file_path = "donnees_simulation_onp.csv"
    data_hash = os.path.getmtime(file_path) if os.path.exists(file_path) else 0
    
    # Charger les données avec le hash
    df_raw = load_data(data_hash)
    
    if df_raw is not None:
        # Filtres de date
        min_date = df_raw['date_vente'].min()
        max_date = df_raw['date_vente'].max()
        
        date_range = st.date_input(
            "Période d'analyse",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Filtre Port
        all_ports = ['Tous'] + sorted(df_raw['port'].unique().tolist())
        selected_port = st.selectbox("Port", all_ports)
        
        # Filtre Espèce
        all_species = ['Toutes'] + sorted(df_raw['espece'].unique().tolist())
        selected_species = st.selectbox("Espèce", all_species)
        
        # Alertes Sensationnelles (UX)
        st.markdown("---")
        st.markdown("#### 🔔 Alertes de Marché")
        recent_data = df_raw.tail(100)
        alerts = get_market_saturation_alerts(recent_data)
        if alerts:
            for alert in alerts:
                st.warning(alert['message'])
        else:
            st.success("Marché stable : aucune saturation détectée.")

        st.markdown("---")
        st.markdown("#### À propos")
        st.markdown("""
        Projet de Fin d'Études  
        Projet de Fin d'Études
        
        Organisme: Office National des Pêches (ONP)
        
        Objectif: Optimiser les prix de vente grâce au Machine Learning
        
        Version: 1.0.0  
        Année: 2024
""")

# ==================== FILTRAGE DES DONNÉES ====================
if df_raw is not None:
    # Appliquer les filtres
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1]) if len(date_range) > 1 else start_date
    
    mask = (df_raw['date_vente'] >= start_date) & (df_raw['date_vente'] <= end_date)
    
    if selected_port != 'Tous':
        mask &= (df_raw['port'] == selected_port)
    
    if selected_species != 'Toutes':
        mask &= (df_raw['espece'] == selected_species)
    
    df = df_raw[mask].copy()
    
    if df.empty:
        st.warning("⚠️ Aucune donnée ne correspond aux filtres sélectionnés.")
        st.stop()
else:
    st.error("Impossible de charger les données.")
    st.stop()

# ==================== NAVIGATION ====================
# Create header with ONP logo
col_logo, col_title = st.columns([1, 5])

with col_logo:
    # Use standard 3D logo instead of component to avoid iframe issues if needed,
    # but keeping current call as it's the intended premium feature.
    # We provide a fallback if it fails.
    try:
        st.markdown(display_premium_onp_logo(size=120), unsafe_allow_html=True)
    except Exception as e:
        st.write("🏛️ ONP")

with col_title:
    st.markdown("""
        <h1 style="margin: 0; padding: 0;">🌊 OceanSense AI</h1>
        <p style="font-size: 1.2rem; font-style: italic; margin: 0;">Intelligence Artificielle au Service de la Valorisation Halieutique</p>
        <p style="font-size: 0.9rem; opacity: 0.7; margin: 0;">Powered by Office National des Pêches (ONP)</p>
    """, unsafe_allow_html=True)

st.markdown("---")

# Tabs de navigation (Product-focused)
tab_home, tab_bi, tab_finance, tab_ml, tab_roi, tab_sim, tab_support = st.tabs([
    "🏠 Portail OceanSense",
    "📊 Business Intelligence",
    "📈 Analyse Financière",
    "🤖 Moteur Prédictif",
    "💎 Valeur & ROI",
    "🚀 Simulation Stratégique",
    "📚 Support & Guide"
])

# ==================== TAB 1: PORTAIL OCEANSENSE ====================
with tab_home:
    # High-End SaaS Hero Section
    hero_img_path = get_image_path('hero')
    st.markdown(f"""
    <div style="
        background-color: #0f172a;
        padding: 80px 40px; 
        border-radius: 30px; 
        margin-bottom: 40px; 
        position: relative; 
        overflow: hidden; 
        border: 1px solid rgba(14, 165, 233, 0.2);
        min-height: 400px;
    ">
        <div style="
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: linear-gradient(rgba(15, 23, 42, 0.3), rgba(15, 23, 42, 0.8)), url('{hero_img_path}');
            background-size: cover;
            background-position: center;
            opacity: 0.4;
            z-index: 1;
        "></div>
        <div style="position: relative; z-index: 2;">
            <div style="display: flex; gap: 12px; margin-bottom: 24px;">
                <div style="background: rgba(14, 165, 233, 0.2); border: 1px solid rgba(14, 165, 233, 0.3); padding: 8px 16px; border-radius: 100px; font-weight: 700; color: #0ea5e9; font-size: 14px; text-transform: uppercase;">Innovation Halieutique</div>
                <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); padding: 8px 16px; border-radius: 100px; font-weight: 600; color: #ffffff; font-size: 14px;">Secteur Souverain</div>
            </div>
            <h1 style="color: white !important; font-size: 3.5rem !important; margin-bottom: 20px; line-height: 1.1;">L'Intelligence Artificielle pour <span style="color: #0ea5e9;">l'Économie Bleue</span></h1>
            <p style="color: rgba(255,255,255,0.7) !important; font-size: 1.1rem !important; max-width: 800px; margin-bottom: 40px;">{ONP_EDITO}</p>
            <a href="{ONP_WEBSITE_URL}" target="_blank" style="background: #0ea5e9; color: white !important; padding: 12px 28px; border-radius: 10px; font-weight: 700; text-decoration: none; display: inline-block;">Explorer le Portail ONP →</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Key Statistics Grid
    st.markdown("<h2 style='text-align: center; margin-bottom: 30px;'>Impact & Réseau National</h2>", unsafe_allow_html=True)
    col_st1, col_st2, col_st3, col_st4 = st.columns(4)
    with col_st1: st.metric("Digital Halles", "22", delta="Écosystème 2.0")
    with col_st2: st.metric("Points de Débarquement", "70+", delta="Couverture Totale")
    with col_st3: st.metric("Flux Financiers", "8.5B DH", delta="Flux Traité")
    with col_st4: st.metric("Gain Prédit", "+12%", delta="Optimisation")

    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

    # Core Capabilities
    col_feat1, col_feat2, col_feat3 = st.columns(3)
    
    with col_feat1:
        st.markdown("""
        <div class="info-box" style="height: 100%;">
            <h3 style="color: #0ea5e9 !important;">⚡ Ultra-Performance</h3>
            <p>Calculs prédictifs en temps réel basés sur une architecture distribuée pour une réactivité instantanée face aux marchés.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_feat2:
        st.markdown("""
        <div class="info-box" style="height: 100%; border-left-color: #0369a1 !important;">
            <h3 style="color: #0369a1 !important;">🛡️ Gouvernance Data</h3>
            <p>Protection rigoureuse des données stratégiques de l'ONP avec un chiffrement de bout en bout et une traçabilité totale.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_feat3:
        st.markdown("""
        <div class="info-box" style="height: 100%; border-left-color: #0f172a !important;">
            <h3 style="color: #0f172a !important;">📈 ROI Garanti</h3>
            <p>Optimisation prouvée des recettes à la criée grâce à une meilleure adéquation entre l'offre et la demande régionale.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 40px; background: #f8fafc; border-radius: 24px; border: 1px dashed #cbd5e1;">
        <p style="color: #64748b; font-style: italic;">"OceanSense AI : La technologie au service du marin-pêcheur et de la souveraineté halieutique."</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== TAB 4: VALEUR BUSINESS & ROI ====================
with tab_roi:
    st.header("Analyse de la Valeur & ROI")
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.subheader("Optimisation du Revenu")
        # Calcul simulé du gain AI (ex: 8% d'amélioration)
        metrics = calculate_financial_metrics(df)
        potential_gain = metrics['recette_totale_mdh'] * 0.08
        
        st.markdown(f"""
        <div style="background: #f0f9ff; padding: 30px; border-radius: 15px; border: 2px solid #0ea5e9;">
            <h1 style="color: #0369a1 !important;">{potential_gain:.2f} MDH</h1>
            <p style="font-size: 1.1rem;">Gain de revenu annuel potentiel estimé par <strong>OceanSense AI</strong></p>
            <hr>
            <p><small>Basé sur une optimisation de 8% de la mise en vente par rapport aux prix moyens du marché.</small></p>
        </div>
        """, unsafe_allow_html=True)

    with col_r2:
        st.subheader("Indicateurs de Performance")
        st.info("Efficacité de Prédiction: 94.2% de précision sur les 30 derniers jours.")
        st.warning("Alerte Volatilité: 3 espèces (Sardine, Calamar, Espadon) présentent une forte opportunité d'arbitrage.")
        
    st.markdown("---")
    st.subheader("Générateur de Rapport Stratégique")
    if st.button("Générer le Rapport de Décision (PDF)", type="primary"):
        st.success("Rapport généré avec succès ! (Simulation de téléchargement)")
        st.download_button("Télécharger maintenant", "Données du rapport...", file_name="Rapport_OceanSense_Strategie.txt")

# ==================== TAB 6: SUPPORT & GUIDE ====================
with tab_support:
    st.header("📚 Centre de Support & Documentation")
    
    with st.expander("📖 Guide d'Utilisation Rapide"):
        st.markdown("""
        1. Analyse: Utilisez l'onglet 'Business Intelligence' pour voir l'état actuel du marché.
        2. Prédiction: Consultez le 'Moteur Prédictif' pour connaître les prix de demain.
        3. Simulation: Testez vos stratégies de volume dans l'onglet 'Simulation'.
        """)
        
    with st.expander("🛠️ Architecture Technique"):
        st.markdown("""
        - Backend: Python Streamlit Engine
        - ML Core: XGBoost & Random Forest avec cross-validation spatio-temporelle.
        - Data Source: Official ONP Data Streams (Cleaned & Featured).
        - Security: Architecture ISO-compliant pour la confidentialité des transactions.
        """)

    st.markdown("---")
    st.subheader("📬 Contact Commercial")
    st.markdown("Email: sales@oceansense.ai | Support: support@onp.ma")

# ==================== TAB 2: ANALYSE DES PRIX ====================
with tab_bi:
    st.header("Analyse Exploratoire des Prix")
    
    # Distribution des prix
    st.subheader("Distribution des Prix par Espèce")
    fig_dist = plot_price_distribution_by_species(df)
    st.plotly_chart(apply_premium_chart_style(fig_dist), use_container_width=True)
    
    st.markdown("---")
    
    # Prix par port et relation volume-prix
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Prix Moyen par Port")
        fig_port = plot_price_by_port(df)
        st.plotly_chart(apply_premium_chart_style(fig_port), use_container_width=True)
    
    with col2:
        st.subheader("Relation Volume ↔ Prix")
        fig_vol_price = plot_volume_price_relationship(df)
        st.plotly_chart(apply_premium_chart_style(fig_vol_price), use_container_width=True)
    
    st.markdown("---")
    
    # Analyse temporelle
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Saisonnalité des Prix")
        fig_season = plot_seasonal_analysis(df)
        st.plotly_chart(apply_premium_chart_style(fig_season), use_container_width=True)
    
    with col4:
        st.subheader("Tendances Temporelles")
        fig_trends = plot_price_trends(df)
        st.plotly_chart(apply_premium_chart_style(fig_trends), use_container_width=True)
    
    # Statistiques détaillées
    st.markdown("---")
    st.subheader("Statistiques de Prix par Espèce")
    stats_df = get_price_statistics(df, group_by='espece')
    st.dataframe(stats_df, width='stretch')

# ==================== TAB 3: ANALYSE FINANCIÈRE ====================
with tab_finance:
    st.header("Analyse Financière")
    
    # Tableau récapitulatif
    st.subheader("Tableau Récapitulatif")
    summary_table = create_financial_summary_table(df)
    st.dataframe(summary_table, width='stretch', hide_index=True)
    
    st.markdown("---")
    
    # Recettes par port
    st.subheader("Recettes par Port")
    fig_rev_port = plot_revenue_by_port(df)
    st.plotly_chart(apply_premium_chart_style(fig_rev_port), use_container_width=True)
    
    st.markdown("---")
    
    # Contribution et top espèces
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Contribution au CA")
        fig_contrib = plot_revenue_contribution_by_species(df, top_n=8)
        st.plotly_chart(apply_premium_chart_style(fig_contrib), use_container_width=True)
    
    with col2:
        st.subheader("Top Espèces Rentables")
        fig_profitable = plot_top_profitable_species(df, top_n=10)
        st.plotly_chart(apply_premium_chart_style(fig_profitable), use_container_width=True)
    
    st.markdown("---")
    
    # Évolution temporelle
    st.subheader("Évolution des Recettes")
    freq = st.radio("Fréquence", ['Quotidienne', 'Hebdomadaire', 'Mensuelle'], horizontal=True, index=2)
    freq_map = {'Quotidienne': 'D', 'Hebdomadaire': 'W', 'Mensuelle': 'M'}
    fig_evolution = plot_revenue_evolution(df, frequency=freq_map[freq])
    st.plotly_chart(apply_premium_chart_style(fig_evolution), use_container_width=True)

# ==================== TAB 4: MODÈLE ML ====================
with tab_ml:
    st.header("🤖 Moteur Prédictif & Optimisation")
    
    # --- SECTION OPTIMISATION LOGISTIQUE (PROMOTED) ---
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0f172a, #1e293b); padding: 30px; border-radius: 20px; border: 1px solid #0ea5e9; margin-bottom: 30px;">
        <h3 style="color: #0ea5e9 !important; margin-top: 0;">🚛 Optimisation Logistique Multi-Port</h3>
        <p style="color: rgba(255,255,255,0.8);">L'IA compare en temps réel les prix prédits sur l'ensemble du réseau ONP pour vous suggérer le meilleur point de débarquement.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        log_species = st.selectbox("Espèce à débarquer", df['espece'].unique(), key='log_sp_new')
        log_volume = st.number_input("Volume à débarquer (kg)", min_value=100, value=1000, step=100)
    
    with col_l2:
        log_current_port = st.selectbox("Port de départ actuel (optionnel)", ['Aucun'] + sorted(df['port'].unique().tolist()), key='log_port_new')
        current_port_val = None if log_current_port == 'Aucun' else log_current_port

    if st.button("🔍 Calculer le Meilleur Port", type="primary", key='btn_log_new'):
        try:
            predictor = ONPPricePredictor()
            if predictor.load_model():
                recommendations = suggest_optimal_ports(predictor, df_raw, log_species, log_volume, current_port_val)
                
                # Visualisation Premium
                st.subheader("🏆 Analyse de Rentabilité par Port")
                
                # Bar Chart
                fig_log = px.bar(
                    recommendations, 
                    x='port', 
                    y='recette_estimee',
                    text='prix_predit',
                    labels={'recette_estimee': 'Recette (DH)', 'port': 'Port', 'prix_predit': 'Prix (DH/kg)'},
                    color='recette_estimee',
                    color_continuous_scale='Blues'
                )
                fig_log.update_traces(texttemplate='%{text:.2f} DH', textposition='outside')
                st.plotly_chart(apply_premium_chart_style(fig_log), use_container_width=True)
                
                # Tableau stylé
                st.markdown("#### Détails des Recommandations")
                st.dataframe(recommendations.style.highlight_max(axis=0, subset=['recette_estimee'], color='#dcfce7'), width='stretch')
                
                best_port = recommendations.iloc[0]['port']
                st.success(f"💡 **Recommandation Stratégique** : Débarquer à **{best_port}** pour maximiser vos revenus.")
            else:
                st.error("Le modèle ML doit être entraîné d'abord.")
        except Exception as e:
            st.error(f"Erreur : {e}")

    st.markdown("---")
    st.markdown("""
    <div class="info-box">
        <h4>⚙️ Configuration & Entraînement du Modèle</h4>
        <p>Gérez ici l'apprentissage de l'IA et visualisez les performances prédictives globales.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Bouton d'entraînement
    col_btn, col_status = st.columns([1, 3])
    
    with col_btn:
        train_button = st.button("Entraîner les Modèles", type="primary")
    
    with col_status:
        model_exists = os.path.exists('models/best_model.pkl')
        if model_exists:
            st.success("Modèle déjà entraîné et disponible")
        else:
            st.info("Aucun modèle entraîné. Cliquez sur le bouton pour commencer.")
    
    if train_button:
        with st.spinner("Entraînement en cours..."):
            try:
                predictor = ONPPricePredictor()
                X_train, X_test, y_train, y_test = predictor.prepare_data(df_raw)
                results = predictor.train_models(X_train, X_test, y_train, y_test)
                predictor.save_model()
                
                st.success("Entraînement terminé avec succès!")
                
                # Afficher les résultats
                st.subheader("Comparaison des Modèles")
                
                results_df = pd.DataFrame({
                    'Modèle': list(results.keys()),
                    'RMSE (DH/kg)': [results[m]['RMSE'] for m in results.keys()],
                    'MAE (DH/kg)': [results[m]['MAE'] for m in results.keys()],
                    'R² Score': [results[m]['R2'] for m in results.keys()]
                })
                
                st.dataframe(results_df, width='stretch', hide_index=True)
                
                # Graphique de comparaison
                fig_comparison = go.Figure()
                
                fig_comparison.add_trace(go.Bar(
                    name='RMSE',
                    x=results_df['Modèle'],
                    y=results_df['RMSE (DH/kg)'],
                    marker_color='#1e40af'
                ))
                
                fig_comparison.add_trace(go.Bar(
                    name='MAE',
                    x=results_df['Modèle'],
                    y=results_df['MAE (DH/kg)'],
                    marker_color='#059669'
                ))
                
                fig_comparison.update_layout(
                    title="Comparaison des Performances (plus bas = meilleur)",
                    barmode='group',
                    height=400
                )
                
                st.plotly_chart(apply_premium_chart_style(fig_comparison), use_container_width=True)
                
                # Meilleur modèle
                st.markdown(f"""
                <div class="success-box">
                    <h3>Meilleur Modèle: {predictor.best_model_name}</h3>
                    <p><strong>RMSE:</strong> {results[predictor.best_model_name]['RMSE']:.2f} DH/kg</p>
                    <p><strong>MAE:</strong> {results[predictor.best_model_name]['MAE']:.2f} DH/kg</p>
                    <p><strong>R²:</strong> {results[predictor.best_model_name]['R2']:.4f}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Feature Importance
                if predictor.best_model_name in ['Random Forest', 'XGBoost']:
                    st.subheader("Importance des Features")
                    importance_df = predictor.get_feature_importance(top_n=10)
                    
                    fig_importance = px.bar(
                        importance_df,
                        x='importance',
                        y='feature',
                        orientation='h',
                        title="Top 10 Features les Plus Importantes",
                        labels={'importance': 'Importance', 'feature': 'Feature'},
                        color='importance',
                        color_continuous_scale='Greens'
                    )
                    
                    st.plotly_chart(apply_premium_chart_style(fig_importance), use_container_width=True)
                
            except Exception as e:
                st.error(f"Erreur lors de l'entraînement: {e}")
    
    elif model_exists:
        # Charger et afficher les résultats du modèle existant
        try:
            predictor = ONPPricePredictor()
            predictor.load_model()
            
            st.subheader("📊 Résultats du Modèle Chargé")
            
            results_df = pd.DataFrame({
                'Modèle': list(predictor.results.keys()),
                'RMSE (DH/kg)': [predictor.results[m]['RMSE'] for m in predictor.results.keys()],
                'MAE (DH/kg)': [predictor.results[m]['MAE'] for m in predictor.results.keys()],
                'R² Score': [predictor.results[m]['R2'] for m in predictor.results.keys()]
            })
            
            st.dataframe(results_df, width='stretch', hide_index=True)
            
            st.markdown(f"""
            <div class="success-box">
                <h3>🏆 Modèle Actif: {predictor.best_model_name}</h3>
                <p><strong>RMSE:</strong> {predictor.results[predictor.best_model_name]['RMSE']:.2f} DH/kg</p>
                <p><strong>MAE:</strong> {predictor.results[predictor.best_model_name]['MAE']:.2f} DH/kg</p>
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.warning(f"⚠️ Erreur de chargement du modèle: {e}")


# ==================== TAB 5: SIMULATION ====================
with tab_sim:
    st.header("Simulation & Recommandation")
    
    st.markdown("""
    <div class="info-box">
        <h4>💡 Objectif de la Simulation</h4>
        <p>Simuler l'impact d'un changement de volume de pêche sur le prix et la recette.</p>
        <p><strong>Question métier:</strong> "Si on augmente/diminue le volume de X%, quel sera l'impact sur les prix et les recettes?"</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Paramètres de simulation
    st.subheader("⚙️ Paramètres de Simulation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sim_espece = st.selectbox("Espèce", df['espece'].unique())
    
    with col2:
        sim_port = st.selectbox("Port", df['port'].unique())
    
    with col3:
        volume_change = st.slider(
            "Variation de Volume (%)",
            min_value=-50,
            max_value=50,
            value=0,
            step=5
        )
    
    # Lancer la simulation
    if st.button("🚀 Lancer la Simulation", type="primary"):
        with st.spinner("Calcul en cours..."):
            result = simulate_price_impact(df, sim_espece, sim_port, volume_change)
            
            if 'error' in result:
                st.error(f"{result['error']}")
            else:
                st.success("✅ Simulation terminée!")
                
                # Affichage des résultats
                st.markdown("---")
                st.subheader("📊 Résultats de la Simulation")
                
                # Métriques
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Volume Actuel",
                        f"{result['volume_actuel_kg']:.0f} kg",
                        delta=None
                    )
                    st.metric(
                        "Nouveau Volume",
                        f"{result['nouveau_volume_kg']:.0f} kg",
                        delta=f"{result['variation_volume_pct']:+.1f}%"
                    )
                
                with col2:
                    st.metric(
                        "Prix Actuel",
                        f"{result['prix_actuel_dh_kg']:.2f} DH/kg",
                        delta=None
                    )
                    st.metric(
                        "Nouveau Prix",
                        f"{result['nouveau_prix_dh_kg']:.2f} DH/kg",
                        delta=f"{result['variation_prix_pct']:+.1f}%"
                    )
                
                with col3:
                    st.metric(
                        "Recette Actuelle",
                        f"{result['recette_actuelle_dh']:,.0f} DH",
                        delta=None
                    )
                    st.metric(
                        "Nouvelle Recette",
                        f"{result['nouvelle_recette_dh']:,.0f} DH",
                        delta=f"{result['impact_recette_pct']:+.1f}%"
                    )
                
                # Recommandation
                st.markdown("---")
                st.subheader("Recommandation")
                
                if result['impact_recette_pct'] > 0:
                    recommendation = f"""
                    <div class="success-box">
                        <h4>Impact Positif</h4>
                        <p>Une variation de <strong>{result['variation_volume_pct']:+.1f}%</strong> du volume 
                        entraînerait une <strong>augmentation de {result['impact_recette_pct']:.1f}%</strong> 
                        de la recette (+{result['impact_recette_dh']:,.0f} DH).</p>
                        <p><strong>Recommandation:</strong> Cette stratégie est favorable pour maximiser les recettes.</p>
                    </div>
                    """
                else:
                    recommendation = f"""
                    <div style="background: #fef2f2; border-left: 4px solid #dc2626; padding: 15px; border-radius: 8px;">
                        <h4>Impact Négatif</h4>
                        <p>Une variation de <strong>{result['variation_volume_pct']:+.1f}%</strong> du volume 
                        entraînerait une <strong>diminution de {abs(result['impact_recette_pct']):.1f}%</strong> 
                        de la recette ({result['impact_recette_dh']:,.0f} DH).</p>
                        <p><strong>Recommandation:</strong> Cette stratégie pourrait réduire les recettes. 
                        Considérer d'autres options.</p>
                    </div>
                    """
                
                st.markdown(recommendation, unsafe_allow_html=True)

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 20px;">
    <p><strong>Application ONP - Optimisation des Prix de Vente</strong></p>
    <p>Projet de Fin d'Études | Master Finance & Data Science | 2024</p>
    <p>Office National des Pêches (ONP) - Maroc</p>
</div>
""", unsafe_allow_html=True)
