"""
ONP Design System - Modern & Premium UI Components
==================================================

Système de design cohérent et professionnel avec:
- Glassmorphism design pattern
- Variables de couleur harmonieuses
- Animations fluides
- Composants réutilisables
- Accessibilité optimisée
"""

import streamlit as st
from typing import Optional, Dict, Any
import plotly.graph_objects as go
import plotly.express as px

# ==================== PALETTE DE COULEURS ====================
class ColorPalette:
    """Palette de couleurs Haute Couture - Thème "Halieutis Excellence" """
    
    # Couleurs Identitaires (Elite Ocean)
    PRIMARY_BLUE = "#0F172A"        # Deep Navy
    ACCENT_BLUE = "#0EA5E9"         # Bright Azure
    SOFT_BLUE = "#F0F9FF"           # Sky Tint
    
    # Surfaces & Matériaux
    GLASS_BG = "rgba(255, 255, 255, 0.72)"
    GLASS_BORDER = "rgba(255, 255, 255, 0.4)"
    CARD_SHADOW = "0 20px 40px -15px rgba(15, 23, 42, 0.12)"
    
    # Accents Stratégiques
    EMERALD = "#10B981"             # Thème Pêche Premium
    AMBER = "#F59E0B"               # Thème Alerte/Highlight
    ROSE = "#F43F5E"                # Thème Critique
    
    # Typographie
    TEXT_ELITE = "#0F172A"          # Deep Slate
    TEXT_SLATE = "#475569"          # Professional Grey
    TEXT_MUTED = "#94A3B8"          # Support Text
    WHITE = "#FFFFFF"

# ==================== STYLE CSS PREMIUM ====================
def inject_css_styles():
    """Injecte le CSS premium pour toute l'application"""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Poppins:wght@400;500;600&display=swap');
        
        /* ============= RESET GLOBAL ============= */
        * {
            box-sizing: border-box;
        }
        
        html, body, [class*="css"] {
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
            background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%) !important;
        }
        
        /* ============= ANIMATIONS REMOVED FOR INSTITUTIONAL STYLE ============= */
        
        /* ============= UTILS CLASSES ============= */
        .fade-in-up { opacity: 1; }
        .fade-in-down { opacity: 1; }
        .float-element { transform: none; }
        .glow-pulse-border { border-width: 1px !important; border-color: rgba(14, 165, 233, 0.2) !important; }
        
        /* ============= COMPOSANTS GLOBAUX ============= */
        .stApp {
            background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%) !important;
        }
        
        /* ============= SIDEBAR GLASSMORPHISM ============= */
        section[data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.95) !important;
            border-right: 1px solid rgba(14, 165, 233, 0.1) !important;
        }
        
        section[data-testid="stSidebar"] .stMarkdown, 
        section[data-testid="stSidebar"] [data-testid="stText"] {
            color: #0F172A !important;
        }
        
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #0369A1 !important;
            font-weight: 700 !important;
            text-shadow: 0 2px 8px rgba(3, 105, 161, 0.1) !important;
        }
        
        /* ============= TÍTULOS & HEADINGS ============= */
        h1 {
            color: #0F172A !important;
            font-size: 3.2rem !important;
            font-weight: 800 !important;
            letter-spacing: -0.04em !important;
            margin-bottom: 0.75rem !important;
            line-height: 1.1 !important;
            background: linear-gradient(135deg, #0F172A 0%, #0369A1 100%);
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            background-clip: text !important;
        }
        
        /* OVERRIDE FOR HERO SECTION */
        .hero-title {
            -webkit-text-fill-color: initial !important;
            background: none !important;
            color: inherit !important;
        }
        
        h2 {
            color: #1E293B !important;
            font-size: 2.2rem !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
            margin-top: 2rem !important;
            margin-bottom: 1rem !important;
            position: relative;
        }
        
        h2::after {
            content: '';
            display: block;
            width: 60px;
            height: 4px;
            background: #0EA5E9;
            border-radius: 2px;
            margin-top: 8px;
        }
        
        h3 {
            color: #334155 !important;
            font-size: 1.5rem !important;
            font-weight: 600 !important;
            letter-spacing: -0.01em !important;
            margin-top: 1.5rem !important;
        }
        
        /* ============= TEXTOS ============= */
        p, .stMarkdown, [class*="stText"], span {
            color: #475569 !important;
            line-height: 1.6 !important;
            font-weight: 400 !important;
        }
        
        /* ============= BOTONES ============= */
        .stButton > button {
            background: linear-gradient(135deg, #0369A1, #0EA5E9) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            letter-spacing: 0.5px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 10px 25px rgba(3, 105, 161, 0.2) !important;
            cursor: pointer !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 15px 35px rgba(3, 105, 161, 0.35) !important;
        }
        
        .stButton > button:active {
            transform: translateY(-1px) !important;
        }
        
        /* ============= INPUTS ============= */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stNumberInput > div > div > input {
            background: rgba(255, 255, 255, 0.8) !important;
            border: 1.5px solid rgba(14, 165, 233, 0.3) !important;
            border-radius: 10px !important;
            color: #0F172A !important;
            font-family: 'Outfit', sans-serif !important;
            font-size: 0.95rem !important;
            padding: 0.75rem 1rem !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus,
        .stNumberInput > div > div > input:focus {
            background: rgba(255, 255, 255, 0.95) !important;
            border-color: #0EA5E9 !important;
            box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1) !important;
            outline: none !important;
        }
        
        /* ============= TABS ============= */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
            border-bottom: 2px solid rgba(14, 165, 233, 0.2) !important;
            padding-bottom: 0 !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent !important;
            border-bottom: 3px solid transparent !important;
            padding: 0.75rem 1.5rem !important;
            color: #64748B !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        
        .stTabs [aria-selected="true"] {
            color: #0EA5E9 !important;
            border-bottom-color: #0EA5E9 !important;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            color: #0369A1 !important;
        }
        
        /* ============= GLASSMORPHISM PREMIUM ============= */
        .metric-card {
            background: rgba(255, 255, 255, 0.7) !important;
            backdrop-filter: blur(32px) !important;
            -webkit-backdrop-filter: blur(32px) !important;
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
            border-radius: 24px !important;
            padding: 1.75rem !important;
            box-shadow: 0 20px 40px -15px rgba(15, 23, 42, 0.08) !important;
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
        }
        
        .metric-card:hover {
            box-shadow: 0 30px 60px -12px rgba(15, 23, 42, 0.12) !important;
            background: rgba(255, 255, 255, 0.9) !important;
            border-color: rgba(14, 165, 233, 0.3) !important;
        }

        /* ============= CREATIVE HOME COMPONENTS ============= */
        .glow-text {
            color: white !important;
        }

        .badge-premium {
            background: rgba(14, 165, 233, 0.1) !important;
            border: 1px solid rgba(14, 165, 233, 0.2) !important;
            color: #0EA5E9 !important;
            padding: 4px 12px !important;
            border-radius: 100px !important;
            font-size: 0.75rem !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
        }

        .market-pulse-node {
            opacity: 1;
        }

        .portfolio-card {
            position: relative;
            border-radius: 24px;
            overflow: hidden;
            transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .portfolio-info {
            position: absolute;
            bottom: -100%;
            left: 0;
            right: 0;
            background: linear-gradient(0deg, rgba(15, 23, 42, 0.95) 0%, rgba(15, 23, 42, 0) 100%);
            padding: 2rem;
            transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
            opacity: 0;
        }

        .portfolio-card:hover .portfolio-info {
            bottom: 0;
            opacity: 1;
        }
        
        /* ============= LOADING STATE ÉLÉGANT ============= */
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Message de chargement personnalisé */
        .onp-loading-msg {
            background: rgba(255,255,255,0.7) !important;
            backdrop-filter: blur(12px) !important;
            border-radius: 14px !important;
            padding: 1rem 1.5rem !important;
            border: 1px solid rgba(14, 165, 233, 0.2) !important;
            color: #0369A1 !important;
            font-weight: 600 !important;
        }
        
        /* ============= MESSAGES SUCCÈS / ERREUR STYLISÉS ============= */
        .stAlert, [data-testid="stAlert"] {
            border-radius: 14px !important;
            border-left: 5px solid !important;
            padding: 1rem 1.5rem !important;
            font-weight: 500 !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06) !important;
        }
        
        .stAlert > div {
            color: #0F172A !important;
            line-height: 1.5 !important;
        }
        
        /* Success - contraste amélioré */
        [data-testid="stAlert"] div:has([data-baseweb="notification"]) {
            background: rgba(16, 185, 129, 0.12) !important;
            border-left-color: #059669 !important;
        }
        
        /* Error - plus visible */
        .stAlert [data-baseweb="notification"][kind="error"],
        div[data-testid="stAlert"]:has(.element-container div[style*="error"]) {
            background: rgba(239, 68, 68, 0.12) !important;
            border-left-color: #DC2626 !important;
        }
        
        /* ============= TOOLTIPS & AIDE CONTEXTUELLE ============= */
        [data-tooltip] {
            position: relative;
        }
        [data-tooltip]:hover::after {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%) translateY(-8px);
            background: #0F172A;
            color: #F8FAFC;
            padding: 0.5rem 0.75rem;
            border-radius: 10px;
            font-size: 0.8rem;
            font-weight: 500;
            white-space: nowrap;
            max-width: 280px;
            white-space: normal;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            z-index: 9999;
            animation: tooltipFade 0.2s ease;
        }
        @keyframes tooltipFade {
            from { opacity: 0; transform: translateX(-50%) translateY(-4px); }
            to { opacity: 1; transform: translateX(-50%) translateY(-8px); }
        }
        
        .onp-tooltip-wrap {
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
        }
        
        /* ============= DATA CONTAINERS ============= */
        .dataframe {
            border-radius: 12px !important;
            overflow: hidden !important;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08) !important;
        }
        
        .dataframe thead {
            background: linear-gradient(135deg, #0369A1, #0EA5E9) !important;
            color: white !important;
            font-weight: 600 !important;
        }
        
        .dataframe tbody tr:hover {
            background: rgba(14, 165, 233, 0.08) !important;
        }
        
        /* ============= PLOTLY CHARTS ============= */
        .plotly-graph-div {
            border-radius: 18px !important;
            overflow: hidden !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08), inset 0 1px 0 rgba(255,255,255,0.6) !important;
            background: rgba(255, 255, 255, 0.7) !important;
            backdrop-filter: blur(8px) !important;
            transition: box-shadow 0.3s ease !important;
        }
        .plotly-graph-div:hover {
            box-shadow: 0 12px 40px rgba(14, 165, 233, 0.12) !important;
        }
        
        /* ============= RESPONSIVE & ACCESSIBILITÉ ============= */
        @media (max-width: 768px) {
            .metric-card { padding: 1rem !important; }
            .stTabs [data-baseweb="tab"] { padding: 0.5rem 0.75rem !important; font-size: 0.9rem !important; }
        }
        
        @media (max-width: 640px) {
            h1 { font-size: 1.75rem !important; line-height: 1.2 !important; }
            h2 { font-size: 1.375rem !important; }
            h3 { font-size: 1rem !important; }
            .stButton > button { width: 100% !important; }
            section[data-testid="stSidebar"] { min-width: 200px !important; }
        }
        
        /* Contrastes améliorés (WCAG) */
        .stMarkdown p, .stMarkdown li { color: #334155 !important; }
        a { color: #0369A1 !important; text-decoration: underline; text-underline-offset: 2px; }
        a:hover { color: #0EA5E9 !important; }
        
        /* ============= SIDEBAR STYLING ============= */
        [data-testid="stSidebar"] button {
            background-color: transparent !important;
            border: none !important;
            color: #64748B !important;
            text-align: left !important;
            padding: 0.75rem 1rem !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
            width: 100% !important;
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
        }
        
        [data-testid="stSidebar"] button:hover {
            background-color: rgba(14, 165, 233, 0.05) !important;
            color: #0EA5E9 !important;
            transform: translateX(4px) !important;
        }
        
        [data-testid="stSidebar"] button[kind="primary"] {
            background-color: rgba(14, 165, 233, 0.1) !important;
            color: #0EA5E9 !important;
            font-weight: 700 !important;
            border-left: 3px solid #0EA5E9 !important;
            border-radius: 0 8px 8px 0 !important;
        }

        /* ============= CINEMATIC IMAGES ============= */
        .cinematic-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 1s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.5s ease !important;
        }
        
        .cinematic-container:hover .image-overlay-premium {
            background: linear-gradient(180deg, rgba(15, 23, 42, 0) 0%, rgba(15, 23, 42, 0.9) 100%) !important;
        }

        /* Espacement optimisé */
        .block-container { padding-top: 2rem !important; padding-bottom: 3rem !important; max-width: 1400px !important; }
        [data-testid="stVerticalBlock"] > div { gap: 0.75rem !important; }
    </style>
    """, unsafe_allow_html=True)

# ==================== COMPOSANTS RÉUTILISABLES ====================
class PremiumComponents:
    """Composants UI premium et réutilisables"""
    
    @staticmethod
    def metric_card(title: str, value: str, icon_name: str = "home", 
                   subtitle: Optional[str] = None, color: str = "blue"):
        """Carte métrique premium avec glassmorphism et icônes SVG"""
        color_map = {
            "blue": "#0EA5E9",
            "green": "#10B981",
            "orange": "#F59E0B",
            "red": "#EF4444"
        }
        
        main_color = color_map.get(color, color)
        icon_html = LuxIcons.render(icon_name, size=32, color=main_color)
        
        st.markdown(f"""
<div class="metric-card" style="border-left: 4px solid {main_color}">
<div style="display: flex; justify-content: space-between; align-items: start;">
<div>
<p style="color: #94A3B8; font-size: 0.875rem; margin: 0; text-transform: uppercase; letter-spacing: 0.5px;">{title}</p>
<h3 style="color: #0F172A; font-size: 2rem; margin: 0.5rem 0 0 0; font-weight: 800;">{value}</h3>
{f'<p style="color: #64748B; font-size: 0.875rem; margin: 0.25rem 0 0 0;">{subtitle}</p>' if subtitle else ''}
</div>
<div style="opacity: 0.8;">{icon_html}</div>
</div>
</div>
""", unsafe_allow_html=True)

    @staticmethod
    def section_header(title, subtitle="", icon_name=None, color="#0369A1"):
        """En-tête de section avec icône SVG stylisée."""
        icon_html = LuxIcons.render(icon_name, size=32, color=color, extra_style="margin-right: 15px;") if icon_name else ""
        st.markdown(f"""
            <div style="display: flex; align-items: center; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #E2E8F0;">
                {icon_html}
                <div>
                    <h2 style="margin: 0; color: #1E293B; font-size: 1.75rem; font-weight: 800; letter-spacing: -0.025em;">{title}</h2>
                    <p style="margin: 4px 0 0 0; color: #64748B; font-size: 1rem; font-weight: 500;">{subtitle}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def info_box(message: str, box_type: str = "info"):
        """Boîte d'information stylisée"""
        colors = {
            "success": ("#10B981", "#D1FAE5"),
            "warning": ("#F59E0B", "#FEF3C7"),
            "error": ("#EF4444", "#FEE2E2"),
            "info": ("#0EA5E9", "#E0F2FE")
        }
        
        border_color, bg_color = colors.get(box_type, colors["info"])
        
        st.markdown(f"""
        <div style="
            background: {bg_color};
            border-left: 4px solid {border_color};
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
            font-weight: 500;
            color: #0F172A;
        ">
            {message}
        </div>
        """, unsafe_allow_html=True)

class LuxIcons:
    """Librairie d'icônes SVG premium pour une interface institutionnelle."""
    
    @staticmethod
    def get(name, size=24, color="currentColor"):
        icons = {
            "home": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
            "chart": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>',
            "finance": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
            "brain": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 2t5 0a7.5 7.5 0 0 1 0 15n-5 0a7.5 7.5 0 0 1 0-15z"/><path d="M12 22v-5"/><path d="M9 22v-2"/><path d="M15 22v-2"/></svg>', 
            "simulation": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="10" y1="10" x2="14" y2="14"/><line x1="14" y1="10" x2="10" y2="14"/></svg>',
            "report": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
            "shield": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
            "database": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/><path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"/></svg>',
            "target": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
            "alert": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
            "search": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
            "anchor": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22V8"/><path d="M5 12H2a10 10 0 0 0 20 0h-3"/><circle cx="12" cy="5" r="3"/></svg>',
            "fish": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 16s9-15 20-4c-11 11-20-4-20-4Z"/><path d="M19.45 6.57 22 4"/><path d="M19.45 17.43 22 20"/><path d="M5 11a1 1 0 1 0 0 2 1 1 0 0 0 0-2Z"/></svg>',
            "file": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>'
        }
        return icons.get(name, icons["home"])

    @staticmethod
    def render(name, size=24, color="#0369A1", extra_style=""):
        return f'<span style="display: inline-flex; align-items: center; justify-content: center; vertical-align: middle; {extra_style}">{LuxIcons.get(name, size, color)}</span>'

# ==================== MODÈLES PLOTLY PERSONNALISÉS ====================
# Palette Halieutis Excellence (Deep Navy, Radiant Emerald, Amber Gold, Vivid Azure)
ONP_PLOTLY_COLORWAY = [
    "#0B1120", "#10B981", "#FFD700", "#0EA5E9", "#6366F1", "#F43F5E",
    "#8B5CF6", "#EC4899"
]

def create_premium_template() -> Dict[str, Any]:
    """Crée un template Plotly de niveau 'Rapport Financier Elite'."""
    return {
        "layout": {
            "plot_bgcolor": "rgba(255, 255, 255, 0)",
            "paper_bgcolor": "rgba(255, 255, 255, 0)",
            "geo": {
                "bgcolor": "#0F172A",
                "showocean": True,
                "oceancolor": "#0F172A",
                "showlakes": False,
                "showland": True,
                "landcolor": "#1E293B",
                "showcountries": True,
                "countrycolor": "#334155"
            },
            "font": {
                "family": "Outfit, -apple-system, sans-serif",
                "size": 13,
                "color": "#1E293B"
            },
            "hovermode": "x unified",
            "hoverlabel": {
                "bgcolor": "#0F172A",
                "font_size": 13,
                "font_family": "Inter, sans-serif",
                "font_color": "#F8FAFC",
                "namelength": -1,
                "bordercolor": "rgba(14, 165, 233, 0.5)",
            },
            "legend": {
                "bgcolor": "rgba(255, 255, 255, 0.8)",
                "bordercolor": "rgba(226, 232, 240, 0.5)",
                "borderwidth": 1,
                "font": {"size": 12, "color": "#475569"},
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.05,
                "xanchor": "right",
                "x": 1,
            },
            "margin": {"l": 50, "r": 20, "t": 80, "b": 50},
            "colorway": ONP_PLOTLY_COLORWAY,
            "separators": ", ",
        }
    }

def apply_premium_plotly_styling(fig: go.Figure) -> go.Figure:
    """Applique le style premium à une figure Plotly : template, axes, hover, légendes."""
    template = create_premium_template()
    
    fig.update_layout(
        **template["layout"],
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(226, 232, 240, 0.4)",
            zeroline=False,
            showline=True,
            linewidth=1.5,
            linecolor="#E2E8F0",
            tickfont=dict(size=11, color="#64748B", family="Outfit"),
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(226, 232, 240, 0.4)",
            zeroline=False,
            showline=True,
            linewidth=1.5,
            linecolor="#E2E8F0",
            tickfont=dict(size=11, color="#64748B", family="Outfit"),
        ),
        coloraxis_colorbar=dict(
            thickness=12,
            len=0.7,
            x=1.02,
            tickfont=dict(size=10, color="#64748B", family="Outfit"),
            borderwidth=0,
            title=dict(font=dict(size=12, color="#0F172A", family="Outfit"))
        ),
        # Effet "Elite" sur les polices globales
        title=dict(font=dict(size=18, family="Outfit", color="#0F172A")),
    )
    
    # Couleurs harmonieuses et hover effects "Halieutis"
    colors = ONP_PLOTLY_COLORWAY
    for i, trace in enumerate(fig.data):
        c = colors[i % len(colors)]
        try:
            # Bar chart specific
            if isinstance(trace, go.Bar):
                trace.marker.color = c
                trace.marker.line = dict(width=0)
                trace.hoverlabel = dict(font_size=14, font_family="Outfit")
            # Scatter/Line specific
            elif isinstance(trace, (go.Scatter, go.Line)):
                if trace.mode and 'lines' in trace.mode:
                    trace.line.color = c
                    trace.line.width = 3
                if trace.mode and 'markers' in trace.mode:
                    trace.marker.color = c
                    trace.marker.size = 8
            
            # Application globale du hover stylisé
            trace.hoverlabel = dict(
                bgcolor="#0F172A",
                font_size=13,
                font_family="Outfit",
                font_color="white"
            )
        except Exception:
            pass
    
    return fig

# ==================== LOADING STATES ============= 
class LoadingStates:
    """États de chargement élégants"""
    
    @staticmethod
    def with_spinner(message: str = "Chargement..."):
        """Context manager pour les états de chargement"""
        with st.spinner(message):
            pass
    
    @staticmethod
    def skeleton_loader(num_items: int = 3):
        """Affiche un skeleton loader pendant le chargement"""
        for _ in range(num_items):
            st.markdown("""
            <div style="
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: shimmer 1.5s infinite;
                height: 80px;
                border-radius: 12px;
                margin-bottom: 1rem;
            "></div>
            """, unsafe_allow_html=True)

# ==================== EXPORTACIÓN ============= 
__all__ = [
    "ColorPalette",
    "inject_css_styles",
    "PremiumComponents",
    "LuxIcons",
    "create_premium_template",
    "apply_premium_plotly_styling",
    "LoadingStates"
]
