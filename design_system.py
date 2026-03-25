"""
ONP Design System - Institutionnel & Premium
============================================

Système de design professionnel (fond clair) pour l'Office National des Pêches.
Optimisé pour la lisibilité et l'analyse de données.
"""

import streamlit as st
from typing import Optional, Dict, Any
import plotly.graph_objects as go

# ==================== PALETTE DE COULEURS ====================
class ColorPalette:
    """Palette de couleurs Institutionnelle - ONP Maroc"""
    PRIMARY = "#0369A1"     # Bleu Marine Institutionnel
    SECONDARY = "#0EA5E9"   # Bleu Azur
    ACCENT = "#10B981"      # Vert Emeraude
    BACKGROUND = "#F8FAFC"
    SURFACE = "#FFFFFF"
    TEXT_MAIN = "#0F172A"
    TEXT_MUTED = "#64748B"

# ==================== STYLE CSS INSTITUTIONNEL ====================
def inject_css_styles():
    """Injecte le CSS institutionnel (Fond clair)"""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif !important;
        }

        .stApp {
            background-color: #F8FAFC !important;
        }

        /* ============= CARTES KPI INSTITUTIONNELLES ============= */
        .metric-card {
            background: white !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important;
            padding: 1.5rem !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
            margin-bottom: 1rem;
            transition: transform 0.2s ease;
        }

        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
        }

        /* ============= SIDEBAR PREMIUM (FOND SOMBRE & TEXTE BLANC) ============= */
        section[data-testid="stSidebar"] {
            background-color: #0F172A !important;
            border-right: 1px solid rgba(255,255,255,0.1) !important;
        }

        section[data-testid="stSidebar"] p, 
        section[data-testid="stSidebar"] span, 
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] .stMarkdown h3,
        section[data-testid="stSidebar"] .stMarkdown h4,
        section[data-testid="stSidebar"] .stMarkdown h2 {
            color: #FFFFFF !important;
        }

        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            color: #94A3B8 !important; /* Texte secondaire en gris clair */
        }

        /* Style spécifique pour les boutons de navigation dans la sidebar */
        section[data-testid="stSidebar"] .stButton > button {
            background: rgba(255, 255, 255, 0.05) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
            text-align: left !important;
            justify-content: flex-start !important;
        }

        section[data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(14, 165, 233, 0.2) !important;
            border-color: #0EA5E9 !important;
            transform: translateX(5px);
        }

        /* Style pour le bouton sélectionné (via type="primary" injecté dans app_premium.py) */
        section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background: #0EA5E9 !important;
            color: #FFFFFF !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3) !important;
        }

        /* ============= HERO BANNER (ADAPTÉ AU THÈME CLAIR) ============= */
        .hero-title, .hero-label, .hero-description {
            color: #0F172A; /* Retrait du !important pour permettre l'override inline */
            text-shadow: none;
        }

        /* ============= TITRES (RETOUR AU BLEU MARINE INSTITUTIONNEL) ============= */
        h1, h2, h3 {
            color: #0369A1 !important;
            font-weight: 700 !important;
        }

        /* Titre Header specifically */
        .header-title {
             color: #0369A1 !important;
        }

        /* ============= BOUTONS ============= */
        .stButton > button {
            background: #0369A1 !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            padding: 0.5rem 1.5rem !important;
            font-weight: 600 !important;
        }

        /* ============= TEXTES ============= */
        p, span, label {
            color: #475569 !important;
        }

        /* ============= PLOTLY CHARTS ============= */
        .plotly-graph-div {
            border-radius: 12px !important;
            overflow: hidden !important;
            border: 1px solid #E2E8F0 !important;
            background: white !important;
        }
    </style>
    """, unsafe_allow_html=True)

# ==================== COMPOSANTS RÉUTILISABLES ====================
class PremiumComponents:
    """Composants UI institutionnels"""
    
    @staticmethod
    def metric_card(title: str, value: str, icon_name: str = "home", 
                   subtitle: Optional[str] = None, color: str = "blue"):
        """Carte métrique institutionnelle"""
        color_map = {"blue": "#0369A1", "green": "#10B981", "orange": "#F59E0B", "red": "#EF4444"}
        main_color = color_map.get(color, "#0369A1")
        icon_html = LuxIcons.render(icon_name, size=28, color=main_color)
        
        html_code = f"""
<div class="metric-card" style="border-left: 5px solid {main_color}">
<div style="display: flex; justify-content: space-between; align-items: start;">
<div>
<p style="color: #64748B; font-size: 0.875rem; margin: 0; text-transform: uppercase;">{title}</p>
<h3 style="color: #0F172A !important; font-size: 1.75rem; margin: 0.25rem 0 0 0; font-weight: 800;">{value}</h3>
{f'<p style="color: #94A3B8; font-size: 0.825rem; margin: 0.25rem 0 0 0;">{subtitle}</p>' if subtitle else ''}
</div>
{icon_html}
</div>
</div>
"""
        st.markdown(html_code, unsafe_allow_html=True)

    @staticmethod
    def info_box(text: str, type: str = "info"):
        """Encadré d'information ou d'alerte institutionnel"""
        colors = {
            "info": ("#0EA5E9", "#F0F9FF", "#BAE6FD", "info"),
            "success": ("#10B981", "#F0FDF4", "#BBF7D0", "check-circle"),
            "warning": ("#F59E0B", "#FFFBEB", "#FEF3C7", "alert-triangle"),
            "error": ("#EF4444", "#FEF2F2", "#FEE2E2", "alert-circle")
        }
        main_color, bg_color, border_color, icon = colors.get(type, colors["info"])
        
        st.markdown(f"""
        <div style="
            background: {bg_color};
            border: 1px solid {border_color};
            border-left: 5px solid {main_color};
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            margin: 1.5rem 0;
            display: flex;
            align-items: center;
            gap: 15px;
        ">
            <div style="flex-shrink: 0;">{LuxIcons.render(icon, size=24, color=main_color)}</div>
            <div style="color: #1E293B; font-size: 0.95rem; line-height: 1.5;">{text}</div>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def section_header(title, subtitle="", icon_name=None, color="#0369A1"):
        """En-tête de section institutionnel"""
        icon_html = LuxIcons.render(icon_name, size=28, color=color, extra_style="margin-right: 12px;") if icon_name else ""
        st.markdown(f"""
            <div style="display: flex; align-items: center; margin-bottom: 1.5rem; padding-bottom: 0.75rem; border-bottom: 2px solid #F1F5F9;">
                {icon_html}
                <div>
                    <h2 style="margin: 0; color: #0F172A !important; font-size: 1.5rem; font-weight: 800;">{title}</h2>
                    <p style="margin: 2px 0 0 0; color: #64748B; font-size: 0.95rem;">{subtitle}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

class LuxIcons:
    """Librairie d'icônes SVG institutionnelles"""
    
    @staticmethod
    def get(name, size=24, color="currentColor"):
        icons = {
            "home": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
            "chart": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>',
            "brain": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 2t5 0a7.5 7.5 0 0 1 0 15n-5 0a7.5 7.5 0 0 1 0-15z"/></svg>',
            "fish": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 16s9-15 20-4c-11 11-20-4-20-4Z"/><circle cx="18" cy="12" r="2"/></svg>',
            "octo": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 12V2"/><path d="M12 12l5-5"/><path d="M12 12l5 5"/><path d="M12 12l-5 5"/><path d="M12 12l-5-5"/><circle cx="12" cy="12" r="4"/><path d="M16 8l3-3"/><path d="M16 16l3 3"/><path d="M8 16l-3 3"/><path d="M8 8l-3-3"/></svg>',
            "octo": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 12V2"/><path d="M12 12l5-5"/><path d="M12 12l5 5"/><path d="M12 12l-5 5"/><path d="M12 12l-5-5"/><circle cx="12" cy="12" r="4"/><path d="M16 8l3-3"/><path d="M16 16l3 3"/><path d="M8 16l-3 3"/><path d="M8 8l-3-3"/></svg>',
            "info": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
            "check-circle": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
            "alert-triangle": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m10.29 3.86 8 14a2 2 0 0 1-1.73 3H5.44a2 2 0 0 1-1.73-3l8-14a2 2 0 0 1 3.46 0Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
            "alert-circle": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
            "database": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
            "trending-up": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
            "trending-down": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>',
            "finance": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
            "target": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
            "anchor": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22V8"/><path d="M5 12H2a10 10 0 0 0 20 0h-3"/><circle cx="12" cy="5" r="3"/></svg>',
            "shield": f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
        }
        return icons.get(name, icons["home"])

    @staticmethod
    def render(name, size=24, color="#0369A1", extra_style=""):
        return f'<div style="opacity: 0.7; {extra_style}"><span style="display: inline-flex; align-items: center; justify-content: center; vertical-align: middle;">{LuxIcons.get(name, size, color)}</span></div>'

# ==================== MODÈLES PLOTLY INSTITUTIONNELS ====================
def apply_premium_plotly_styling(fig: go.Figure) -> go.Figure:
    """Style Plotly Premium (Clair) pour une lisibilité maximale"""
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Outfit, sans-serif", "size": 12, "color": "#0F172A"},
        hovermode="x unified",
        margin={"l": 40, "r": 20, "t": 60, "b": 40},
        colorway=["#0369A1", "#0891B2", "#0D9488", "#7C3AED"], # Couleurs professionnelles sur fond blanc
        title=dict(font=dict(color="#0F172A", size=18))
    )
    fig.update_xaxes(
        showgrid=True, 
        gridcolor="#F1F5F9", 
        zeroline=False,
        tickfont=dict(color="#1E293B")
    )
    fig.update_yaxes(
        showgrid=True, 
        gridcolor="#F1F5F9", 
        zeroline=False,
        tickfont=dict(color="#1E293B")
    )
    return fig

def create_premium_template() -> Dict[str, Any]:
    return {"layout": {"template": "plotly_white"}}

# ==================== EXPORTATION ============= 
__all__ = ["inject_css_styles", "PremiumComponents", "LuxIcons", "apply_premium_plotly_styling", "create_premium_template", "ColorPalette"]
