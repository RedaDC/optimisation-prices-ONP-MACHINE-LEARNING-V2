"""
ONP Dynamic Logo & Assets Generator
===================================

Génère dynamiquement le logo ONP et les éléments graphiques.
Utilise le fichier "logo onp.png" lorsqu'il est présent, sinon SVG dynamique.
Compatible avec Streamlit - sans dépendances externes
"""

import os
import base64
from typing import Optional, Tuple

# Fichier logo ONP recherché (avec espace dans le nom)
LOGO_PNG_PATHS = ["logo onp.png", "logo_onp.png", "logo_onp.PNG", "logo onp.PNG"]

def get_logo_onp_png_base64() -> Optional[str]:
    """Charge le logo ONP depuis 'logo onp.png' si présent. Retourne le base64 ou None."""
    for path in LOGO_PNG_PATHS:
        if os.path.isfile(path):
            try:
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
            except Exception:
                pass
    return None

def get_onp_logo_svg() -> str:
    """Génère un logo ONP en SVG (aucune dépendance fichier)"""
    svg = """
    <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" width="200" height="200">
        <defs>
            <linearGradient id="blueGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#0369A1;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#0EA5E9;stop-opacity:1" />
            </linearGradient>
            <filter id="glow">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>
        
        <!-- Background Circle -->
        <circle cx="100" cy="100" r="95" fill="rgba(255,255,255,0.1)" stroke="#0EA5E9" stroke-width="2" filter="url(#glow)"/>
        
        <!-- Fish Body (Sardine) -->
        <ellipse cx="100" cy="100" rx="50" ry="35" fill="url(#blueGrad)" opacity="0.9"/>
        
        <!-- Fish Head -->
        <circle cx="145" cy="100" r="20" fill="#0EA5E9"/>
        
        <!-- Fish Eye -->
        <circle cx="150" cy="98" r="6" fill="#FFFFFF"/>
        <circle cx="151" cy="98" r="3" fill="#0369A1"/>
        
        <!-- Fish Tail -->
        <path d="M 50 100 L 20 80 L 30 100 L 20 120 Z" fill="#10B981" opacity="0.8"/>
        
        <!-- Fish Fins -->
        <ellipse cx="100" cy="70" rx="15" ry="8" fill="#38BDF8" opacity="0.7" transform="rotate(-45 100 70)"/>
        <ellipse cx="100" cy="130" rx="15" ry="8" fill="#38BDF8" opacity="0.7" transform="rotate(45 100 130)"/>
        
        <!-- Water Waves -->
        <path d="M 30 150 Q 40 145 50 150 T 70 150" stroke="#0EA5E9" stroke-width="2" fill="none" opacity="0.6"/>
        <path d="M 130 150 Q 140 145 150 150 T 170 150" stroke="#0EA5E9" stroke-width="2" fill="none" opacity="0.6"/>
        
        <!-- Text: ONP -->
        <text x="100" y="175" font-family="Arial, sans-serif" font-size="16" font-weight="bold" 
              text-anchor="middle" fill="#0369A1">ONP</text>
    </svg>
    """
    return svg

def display_premium_onp_logo(size: int = 200, with_animation: bool = True) -> str:
    """Affiche le logo ONP premium : utilise 'logo onp.png' si présent, sinon SVG sans animation."""
    b64 = get_logo_onp_png_base64()
    if b64:
        img_style = " filter: drop-shadow(0 10px 20px rgba(14, 165, 233, 0.25)); border-radius: 12px;"
        return f"""
        <div style="
            display: flex;
            justify-content: center;
            align-items: center;
        ">
            <img src="data:image/png;base64,{b64}" alt="Logo ONP" width="{size}" height="{size}" style="{img_style}" />
        </div>
        """
    svg = get_onp_logo_svg().replace('width="200" height="200"', f'width="{size}" height="{size}"')
    html = f"""
    <div style="
        display: flex;
        justify-content: center;
        align-items: center;
    ">
        {svg}
    </div>
    """
    return html

def create_animated_kpi_header() -> str:
    """Crée un header KPI statique et professionnel"""
    return """
    <div style="
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
        margin: 20px 0;
    ">
        <div style="
            background: linear-gradient(135deg, rgba(14, 165, 233, 0.1), rgba(16, 185, 129, 0.1));
            border: 1px solid rgba(14, 165, 233, 0.3);
            border-radius: 12px;
            padding: 15px;
            text-align: center;
            backdrop-filter: blur(10px);
            transition: all 0.3s;
        " class="kpi-card" onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 15px 30px rgba(14, 165, 233, 0.2)';"
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
            <div style="font-size: 18px; margin-bottom: 5px; color: #0369A1;">●</div>
            <div style="color: #94A3B8; font-size: 12px; text-transform: uppercase;">Prix moyen</div>
            <div style="color: #0369A1; font-size: 20px; font-weight: 700;">-</div>
        </div>
        
        <div style="
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(245, 158, 11, 0.1));
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 12px;
            padding: 15px;
            text-align: center;
            backdrop-filter: blur(10px);
            transition: all 0.3s;
        " class="kpi-card" onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 15px 30px rgba(16, 185, 129, 0.2)';"
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
            <div style="font-size: 18px; margin-bottom: 5px; color: #059669;">●</div>
            <div style="color: #94A3B8; font-size: 12px; text-transform: uppercase;">Recette</div>
            <div style="color: #059669; font-size: 20px; font-weight: 700;">-</div>
        </div>
        
        <div style="
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(239, 68, 68, 0.1));
            border: 1px solid rgba(245, 158, 11, 0.3);
            border-radius: 12px;
            padding: 15px;
            text-align: center;
            backdrop-filter: blur(10px);
            transition: all 0.3s;
        " class="kpi-card" onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 15px 30px rgba(245, 158, 11, 0.2)';"
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
            <div style="font-size: 18px; margin-bottom: 5px; color: #D97706;">●</div>
            <div style="color: #94A3B8; font-size: 12px; text-transform: uppercase;">Top espèce</div>
            <div style="color: #D97706; font-size: 20px; font-weight: 700;">-</div>
        </div>
        
        <div style="
            background: linear-gradient(135deg, rgba(14, 165, 233, 0.1), rgba(99, 102, 241, 0.1));
            border: 1px solid rgba(14, 165, 233, 0.3);
            border-radius: 12px;
            padding: 15px;
            text-align: center;
            backdrop-filter: blur(10px);
            transition: all 0.3s;
        " class="kpi-card" onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 15px 30px rgba(14, 165, 233, 0.2)';"
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
            <div style="font-size: 18px; margin-bottom: 5px; color: #4F46E5;">●</div>
            <div style="color: #94A3B8; font-size: 12px; text-transform: uppercase;">Volume</div>
            <div style="color: #4F46E5; font-size: 20px; font-weight: 700;">-</div>
        </div>
    </div>
    
    <style>
        .kpi-card {
            cursor: pointer;
        }
    </style>
    """

def create_dynamic_background() -> str:
    """Crée un background statique et élégant"""
    return """
    <div style="
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        background: radial-gradient(circle at 20% 50%, rgba(14, 165, 233, 0.05) 0%, transparent 50%),
                    radial-gradient(circle at 80% 80%, rgba(16, 185, 129, 0.05) 0%, transparent 50%),
                    linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
        pointer-events: none;
    "></div>
    """

def get_dynamic_stats() -> dict:
    """Retourne des stats dynamiques pour l'app"""
    return {
        "pages": 5,
        "features": 15,
        "animations": 0,
        "colors": 60,
        "components": 12
    }

# Export
__all__ = [
    "get_logo_onp_png_base64",
    "get_onp_logo_svg",
    "display_premium_onp_logo",
    "create_animated_kpi_header",
    "create_dynamic_background",
    "get_dynamic_stats"
]
