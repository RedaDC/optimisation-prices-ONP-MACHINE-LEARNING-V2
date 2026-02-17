"""
Assets ONP - Contenu et images inspirés de onp.ma
================================================

Textes et URLs d'images pour l'application, alignés avec
l'Office National des Pêches (ONP) - Maroc.
Site officiel : https://onp.ma/
"""

import os

# Lien site officiel ONP
ONP_WEBSITE_URL = "https://onp.ma/"

# Textes inspirés de la communication ONP
ONP_EDITO = (
    "Au service du développement de la filière pêche depuis 1969, "
    "l'Office National des Pêches (ONP) est un acteur majeur du secteur au Maroc. "
    "Cette application accompagne les professionnels avec des analyses de prix, "
    "des statistiques de commercialisation et des outils d'aide à la décision."
)

ONP_TAGLINE = "Au service du développement de la filière pêche depuis 1969"

ONP_STRATEGY = "Bras opérationnel de la Stratégie Halieutis"

# Images réelles et professionnelles du secteur de la pêche au Maroc
# Sources : Wikimedia Commons (Libre de droits) et Unsplash
# Note : Pour une utilisation hors-ligne, placez les images dans assets/images/ avec les noms correspondants
IMAGES_PECHE_MAROC = {
    # Images with higher reliability and direct access
    "hero": "https://images.unsplash.com/photo-1534067783941-51c9c23ecefd?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80",
    "marche_poisson": "https://images.unsplash.com/photo-1544526226-d45680d0739c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80", 
    "port_essaouira": "https://images.unsplash.com/photo-1569336415962-a4bd9f69cd83?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
    "sardines_poisson": "https://plus.unsplash.com/premium_photo-1667803697960-96f9a061c556?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
    "pecheur_bateau": "https://images.unsplash.com/photo-1596711679095-2c813f433990?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
    "halle_poisson": "https://images.unsplash.com/photo-1563564993683-1c3906a5b23d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
    "port_agadir": "https://images.unsplash.com/photo-1628109886470-87a1c7db135a?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
    "bateaux_bleus": "https://images.unsplash.com/photo-1535567554900-58957bf7794e?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80"
}

def get_image_path(key):
    """
    Retourne le chemin de l'image (local si présent, sinon URL).
    """
    local_filename = f"{key}.jpg"
    local_path = os.path.join("assets", "images", local_filename)
    if os.path.exists(local_path):
        return local_path
    return IMAGES_PECHE_MAROC.get(key, "")

# Légendes professionnelles et contextuelles
IMAGE_CAPTIONS = {
    "hero": "Vision stratégique : Le Port d'Essaouira au crépuscule",
    "marche_poisson": "L'excellence halieutique marocaine : Fraîcheur et tradition",
    "port_essaouira": "La flottille emblématique des chalutiers bleus d'Essaouira",
    "sardines_poisson": "Sardines de l'Atlantique : Le trésor argenté du Royaume",
    "pecheur_bateau": "Savoir-faire et passion : Les gardiens de la mer marocaine",
    "halle_poisson": "Logistique portuaire : L'industrie vers l'avenir 2026",
    "port_agadir": "Agadir : Premier pôle d'exportation halieutique en Afrique",
    "bateaux_bleus": "Patrimoine maritime : Les reflets d'une économie bleue durable",
}
