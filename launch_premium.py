#!/usr/bin/env python3
"""
ONP Premium Application Launcher
================================

Script de lancement de l'application ONP avec la version Premium
Gère les dépendances, configuration et démarrage du serveur Streamlit

Usage:
    python launch_premium.py
"""

import subprocess
import sys
import os
import time
import platform
import webbrowser
from pathlib import Path

# ==================== CONFIGURATION ====================
CONFIG = {
    "app_file": "app_premium.py",
    "port": 8501,
    "host": "localhost",
    "title": "ONP - Optimisation des Prix",
    "description": "Application Premium avec Design Moderne",
    "requirements_file": "requirements.txt"
}

# Couleurs pour la sortie
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header():
    """Affiche le header de l'application"""
    print(f"""
{Colors.BOLD}{Colors.CYAN}
+--------------------------------------------------------+
|                                                        |
|          ONP Premium Application Launcher            |
|                                                        |
|    Optimisation des Prix - Office National des Peches |
|                                                        |
|         Design Modern - Glassmorphism - Premium        |
|                                                        |
+--------------------------------------------------------+
{Colors.END}
    """)

def check_python():
    """Vérifie la version de Python"""
    print(f"{Colors.BLUE}[1/4]{Colors.END} Verification de Python...")
    
    version = sys.version_info
    min_version = (3, 8)
    
    if version >= min_version:
        print(f"    {Colors.GREEN}[OK]{Colors.END} Python {version.major}.{version.minor} detecte")
        return True
    else:
        print(f"    {Colors.RED}[X]{Colors.END} Python 3.8+ requis (actuellement: {version.major}.{version.minor})")
        return False

def check_dependencies():
    """Vérifie si les dépendances sont installées"""
    print(f"\n{Colors.BLUE}[2/4]{Colors.END} Verification des dependances...")
    
    required_packages = [
        "streamlit",
        "pandas",
        "numpy",
        "plotly",
        "sklearn"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"    {Colors.GREEN}[OK]{Colors.END} {package}")
        except ImportError:
            missing.append(package)
            print(f"    {Colors.RED}[X]{Colors.END} {package}")
    
    if missing:
        print(f"\n{Colors.YELLOW}[Installation]{Colors.END} Dependances manquantes trouvees")
        print(f"Installation d'une {CONFIG['requirements_file']}...")
        return install_requirements()
    
    return True

def install_requirements():
    """Installe les dépendances depuis requirements.txt"""
    try:
        req_file = Path(CONFIG['requirements_file'])
        if not req_file.exists():
            print(f"    {Colors.RED}[X]{Colors.END} {CONFIG['requirements_file']} non trouve")
            return False
        
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", CONFIG['requirements_file']],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"    {Colors.GREEN}[OK]{Colors.END} Dependances installees avec succes")
            return True
        else:
            print(f"    {Colors.RED}[X]{Colors.END} Erreur lors de l'installation")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"    {Colors.RED}[X]{Colors.END} Erreur: {str(e)}")
        return False

def check_app_file():
    """Vérifie que le fichier app_premium.py existe"""
    print(f"\n{Colors.BLUE}[3/4]{Colors.END} Verification des fichiers...")
    
    app_file = Path(CONFIG['app_file'])
    
    if app_file.exists():
        print(f"    {Colors.GREEN}[OK]{Colors.END} {CONFIG['app_file']} trouve")
        return True
    else:
        print(f"    {Colors.RED}[X]{Colors.END} {CONFIG['app_file']} non trouve")
        return False

def launch_app():
    """Lance l'application Streamlit"""
    print(f"\n{Colors.BLUE}[4/4]{Colors.END} Demarrage de l'application...")
    
    url = f"http://{CONFIG['host']}:{CONFIG['port']}"
    
    print(f"""
{Colors.BOLD}{Colors.GREEN}+--------------------------------------------------------+
|                  APPLICATION EN COURS DE DEMARRAGE    |
+--------------------------------------------------------+{Colors.END}

    URL: {url}
    Application: {CONFIG['app_file']}
    Port: {CONFIG['port']}
    Design: Premium Glassmorphism

{Colors.YELLOW}Conseil:{Colors.END} L'application s'ouvrira automatiquement dans votre navigateur
{Colors.YELLOW}Appuyez sur CTRL+C pour arrêter l'application{Colors.END}

    """)
    
    try:
        # Essayer d'ouvrir le navigateur après un délai
        time.sleep(2)
        try:
            webbrowser.open(url)
        except Exception:
            pass
        
        # Lancer Streamlit
        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            CONFIG['app_file'],
            "--server.port", str(CONFIG['port']),
            "--logger.level=warning",
            "--client.showErrorDetails=true"
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[STOP] Application arretee par l'utilisateur{Colors.END}\n")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}[X] Erreur lors du demarrage: {str(e)}{Colors.END}")
        sys.exit(1)

def main():
    """Fonction principale"""
    print_header()
    
    # Vérifications
    if not check_python():
        print(f"\n{Colors.RED}[X] Lancement impossible: Python 3.8+ requis{Colors.END}\n")
        sys.exit(1)
    
    if not check_dependencies():
        print(f"\n{Colors.RED}[X] Lancement impossible: Verifiez les dependances{Colors.END}\n")
        sys.exit(1)
    
    if not check_app_file():
        print(f"\n{Colors.RED}[X] Lancement impossible: Fichier app_premium.py manquant{Colors.END}\n")
        sys.exit(1)
    
    print(f"\n{Colors.GREEN}[OK] Toutes les verifications sont passees{Colors.END}")
    
    # Lancer l'application
    launch_app()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n{Colors.RED}[X] Erreur fatale: {str(e)}{Colors.END}\n")
        sys.exit(1)
