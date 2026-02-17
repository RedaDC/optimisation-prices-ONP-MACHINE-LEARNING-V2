"""
Configuration Thèmes & Palettes - ONP Premium
=============================================

Fichier de configuration centralisée pour tous les thèmes et couleurs
Permet de personnaliser l'application facilement
"""

from enum import Enum
from typing import Dict, Tuple

# ==================== PALETTES DE COULEURS ====================
class ThemeColors(Enum):
    """Énumération des thèmes disponibles"""
    OCEAN = "ocean"           # Thème par défaut (océan/bleu)
    FOREST = "forest"         # Thème nature (vert)
    SUNSET = "sunset"         # Thème coucher (orange/rouge)
    NIGHT = "night"           # Thème nuit (gris/violet)

# ==================== COULEURS PAR THÈME ====================
THEMES: Dict[str, Dict[str, str]] = {
    "ocean": {
        # Bleus marins - couleurs principales
        "primary": "#0EA5E9",           # Sky Blue
        "primary_dark": "#0369A1",      # Dark Blue
        "accent": "#38BDF8",            # Light Blue
        
        # Neutrals & Backgrounds
        "dark_bg": "#0F172A",           # Slate Dark
        "light_bg": "#F8FAFC",          # Slate Light
        "white": "#FFFFFF",
        
        # Accents
        "accent_green": "#10B981",      # Emerald
        "accent_orange": "#F59E0B",     # Amber
        "accent_red": "#EF4444",        # Red
        
        # Semantic
        "success": "#10B981",
        "warning": "#F59E0B",
        "error": "#EF4444",
        "info": "#0EA5E9",
        
        # Text
        "text_primary": "#0F172A",
        "text_secondary": "#64748B",
        "text_tertiary": "#94A3B8",
        "text_inverse": "#FFFFFF",
    },
    
    "forest": {
        # Verts naturels
        "primary": "#059669",           # Emerald
        "primary_dark": "#047857",      # Dark Emerald
        "accent": "#10B981",            # Light Emerald
        
        # Backgrounds
        "dark_bg": "#1F2937",           # Dark Gray
        "light_bg": "#F0FDF4",          # Very Light Green
        "white": "#FFFFFF",
        
        # Accents
        "accent_green": "#6EE7B7",      # Pale Green
        "accent_orange": "#FB923C",     # Orange
        "accent_red": "#F87171",        # Red
        
        # Semantic
        "success": "#059669",
        "warning": "#FB923C",
        "error": "#F87171",
        "info": "#10B981",
        
        # Text
        "text_primary": "#1F2937",
        "text_secondary": "#6B7280",
        "text_tertiary": "#9CA3AF",
        "text_inverse": "#FFFFFF",
    },
    
    "sunset": {
        # Couleurs chaudes
        "primary": "#F59E0B",           # Amber
        "primary_dark": "#D97706",      # Dark Amber
        "accent": "#FBBF24",            # Light Amber
        
        # Backgrounds
        "dark_bg": "#78350F",           # Very Dark Brown
        "light_bg": "#FFFBEB",          # Cream
        "white": "#FFFFFF",
        
        # Accents
        "accent_green": "#34D399",      # Teal
        "accent_orange": "#FB923C",     # Orange
        "accent_red": "#F87171",        # Red
        
        # Semantic
        "success": "#34D399",
        "warning": "#F59E0B",
        "error": "#F87171",
        "info": "#FBBF24",
        
        # Text
        "text_primary": "#78350F",
        "text_secondary": "#92400E",
        "text_tertiary": "#B45309",
        "text_inverse": "#FFFFFF",
    },
    
    "night": {
        # Thème sombre avancé
        "primary": "#818CF8",           # Indigo
        "primary_dark": "#6366F1",      # Dark Indigo
        "accent": "#A5B4FC",            # Light Indigo
        
        # Backgrounds
        "dark_bg": "#111827",           # Very Dark Gray
        "light_bg": "#1F2937",          # Dark Gray
        "white": "#F3F4F6",             # Off White
        
        # Accents
        "accent_green": "#4ADE80",      # Bright Green
        "accent_orange": "#FB923C",     # Orange
        "accent_red": "#F87171",        # Red
        
        # Semantic
        "success": "#4ADE80",
        "warning": "#FB923C",
        "error": "#F87171",
        "info": "#818CF8",
        
        # Text
        "text_primary": "#F3F4F6",
        "text_secondary": "#D1D5DB",
        "text_tertiary": "#9CA3AF",
        "text_inverse": "#111827",
    }
}

# ==================== GRADIENTS ====================
GRADIENTS: Dict[str, Tuple[str, str]] = {
    "ocean": ("#0369A1", "#0EA5E9"),
    "forest": ("#047857", "#059669"),
    "sunset": ("#D97706", "#F59E0B"),
    "night": ("#6366F1", "#818CF8"),
}

# ==================== FONTS ====================
FONTS = {
    "primary": "'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    "secondary": "'Poppins', sans-serif",
    "code": "'Monaco', 'Courier New', monospace",
}

# ==================== SPACING ====================
SPACING = {
    "xs": "0.25rem",
    "sm": "0.5rem",
    "md": "1rem",
    "lg": "1.5rem",
    "xl": "2rem",
    "2xl": "3rem",
    "3xl": "4rem",
}

# ==================== BORDER RADIUS ====================
BORDER_RADIUS = {
    "sm": "4px",
    "md": "8px",
    "lg": "12px",
    "xl": "16px",
    "2xl": "20px",
    "full": "9999px",
}

# ==================== SHADOWS ====================
SHADOWS = {
    "sm": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
    "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
    "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1)",
    "2xl": "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
    "inner": "inset 0 2px 4px 0 rgba(0, 0, 0, 0.05)",
    "none": "0 0 0 0 rgba(0, 0, 0, 0)",
}

# ==================== DURATIONS (Animations) ====================
DURATIONS = {
    "fast": "150ms",
    "normal": "300ms",
    "slow": "500ms",
    "slower": "800ms",
    "slowest": "1200ms",
}

# ==================== TRANSITIONS ====================
TRANSITIONS = {
    "default": "all 300ms cubic-bezier(0.4, 0, 0.2, 1)",
    "ease_in": "all 300ms cubic-bezier(0.4, 0, 1, 1)",
    "ease_out": "all 300ms cubic-bezier(0, 0, 0.2, 1)",
    "ease_in_out": "all 300ms cubic-bezier(0.4, 0, 0.2, 1)",
    "bounce": "all 500ms cubic-bezier(0.175, 0.885, 0.32, 1.275)",
}

# ==================== OPACITY ====================
OPACITY = {
    "0": "0",
    "5": "0.05",
    "10": "0.1",
    "20": "0.2",
    "30": "0.3",
    "40": "0.4",
    "50": "0.5",
    "60": "0.6",
    "70": "0.7",
    "80": "0.8",
    "90": "0.9",
    "100": "1",
}

# ==================== BREAKPOINTS (Responsive) ====================
BREAKPOINTS = {
    "xs": "320px",
    "sm": "640px",
    "md": "768px",
    "lg": "1024px",
    "xl": "1280px",
    "2xl": "1536px",
}

# ==================== DEFAULT THEME ====================
DEFAULT_THEME = "ocean"

# ==================== UTILITY FUNCTIONS ====================
def get_theme_colors(theme_name: str = DEFAULT_THEME) -> Dict[str, str]:
    """Obtient les couleurs d'un thème"""
    return THEMES.get(theme_name, THEMES[DEFAULT_THEME])

def get_gradient(theme_name: str = DEFAULT_THEME) -> Tuple[str, str]:
    """Obtient le gradient d'un thème"""
    return GRADIENTS.get(theme_name, GRADIENTS[DEFAULT_THEME])

def get_color(theme_name: str, color_key: str) -> str:
    """Obtient une couleur spécifique d'un thème"""
    theme = get_theme_colors(theme_name)
    return theme.get(color_key, "#0EA5E9")

# ==================== CSS GENERATOR ====================
def generate_css_variables(theme_name: str = DEFAULT_THEME) -> str:
    """Génère les variables CSS pour un thème"""
    colors = get_theme_colors(theme_name)
    
    css = ":root {\n"
    
    # Colors
    for key, value in colors.items():
        css += f"  --color-{key}: {value};\n"
    
    # Spacing
    for key, value in SPACING.items():
        css += f"  --spacing-{key}: {value};\n"
    
    # Border Radius
    for key, value in BORDER_RADIUS.items():
        css += f"  --radius-{key}: {value};\n"
    
    # Shadows
    for key, value in SHADOWS.items():
        css += f"  --shadow-{key}: {value};\n"
    
    # Durations
    for key, value in DURATIONS.items():
        css += f"  --duration-{key}: {value};\n"
    
    # Transitions
    for key, value in TRANSITIONS.items():
        css += f"  --transition-{key}: {value};\n"
    
    # Fonts
    for key, value in FONTS.items():
        css += f"  --font-{key}: {value};\n"
    
    css += "}\n"
    return css

# ==================== EXPORT ====================
__all__ = [
    "THEMES",
    "GRADIENTS",
    "FONTS",
    "SPACING",
    "BORDER_RADIUS",
    "SHADOWS",
    "DURATIONS",
    "TRANSITIONS",
    "OPACITY",
    "BREAKPOINTS",
    "DEFAULT_THEME",
    "get_theme_colors",
    "get_gradient",
    "get_color",
    "generate_css_variables",
    "ThemeColors",
]

# ==================== INFO ====================
if __name__ == "__main__":
    print("ONP Premium - Theme Configuration")
    print("==================================\n")
    
    for theme_name in THEMES.keys():
        print(f"Theme: {theme_name.upper()}")
        colors = get_theme_colors(theme_name)
        print(f"  Primary: {colors['primary']}")
        print(f"  Accent: {colors['accent']}")
        print(f"  Success: {colors['success']}")
        print(f"  Warning: {colors['warning']}")
        print(f"  Error: {colors['error']}")
        print()
