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
    "Bras opérationnel de la Stratégie Halieutis, l'Office National des Pêches (ONP) "
    "assure la modernisation de la filière et la valorisation optimale de la ressource. "
    "Notre intelligence prédictive accompagne les acteurs du secteur dans la maîtrise "
    "des cours et l'optimisation des flux de commercialisation nationale."
)

ONP_TAGLINE = "L'Excellence Halieutique au Cœur de l'Économie Bleue"

ONP_STRATEGY = "Bras opérationnel de la Stratégie Halieutis"

# Images réelles et professionnelles du secteur de la pêche au Maroc
IMAGES_PECHE_MAROC = {
    "hero": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Fish_market_in_Tsukiji.jpg/1200px-Fish_market_in_Tsukiji.jpg",
    "marche_poisson": "https://upload.wikimedia.org/wikipedia/commons/9/95/Sparus_aurata_Sardegna.jpg",
    "port_essaouira": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Mercado_de_Pescado_de_Sidi_Ifni.jpg/1200px-Mercado_de_Pescado_de_Sidi_Ifni.jpg",
    "sardines_poisson": "https://upload.wikimedia.org/wikipedia/commons/6/6a/Sardina_pilchardus1.jpg",
    "pecheur_bateau": "https://upload.wikimedia.org/wikipedia/commons/9/95/Sparus_aurata_Sardegna.jpg",
    "halle_poisson": "https://upload.wikimedia.org/wikipedia/commons/9/95/Sparus_aurata_Sardegna.jpg",
    "port_agadir": "https://upload.wikimedia.org/wikipedia/commons/9/95/Sparus_aurata_Sardegna.jpg",
    "bateaux_bleus": "https://upload.wikimedia.org/wikipedia/commons/9/95/Sparus_aurata_Sardegna.jpg",
    "real_port": "https://upload.wikimedia.org/wikipedia/commons/9/95/Sparus_aurata_Sardegna.jpg",
    "industrial_port": "https://upload.wikimedia.org/wikipedia/commons/9/95/Sparus_aurata_Sardegna.jpg",
    "calamar": "https://upload.wikimedia.org/wikipedia/commons/9/95/Sparus_aurata_Sardegna.jpg",
    "bar": "https://upload.wikimedia.org/wikipedia/commons/6/6f/Dicentrarchus_labrax_177025102.jpg",
    "crevette_grise": "https://upload.wikimedia.org/wikipedia/commons/9/95/Sparus_aurata_Sardegna.jpg",
    "mulet_dore": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Liza_aurata.jpg",
    "sole": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Solea_senegalensis.jpg/800px-Solea_senegalensis.jpg",
    "requin_ha": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Galeorhinus_galeus.jpg",
    "sparaillon_commun": "https://upload.wikimedia.org/wikipedia/commons/b/b5/Diplodus_annularis_%28Linnaeus%2C_1758%29.jpg",
    "maquereau": "https://upload.wikimedia.org/wikipedia/commons/8/84/Cornish_mackerel_1.jpg",
    "anchois": "https://upload.wikimedia.org/wikipedia/commons/d/d0/Boquerones_%28Engraulis_encrasicolus%29%2C_Set%C3%BAbal%2C_Portugal%2C_2020-08-01%2C_DD_16.jpg",
    "dorade": "https://upload.wikimedia.org/wikipedia/commons/9/95/Sparus_aurata_Sardegna.jpg",
    "pageot": "https://upload.wikimedia.org/wikipedia/commons/4/45/Pagellus_erythrinus_France.jpg",
    "bogue": "https://upload.wikimedia.org/wikipedia/commons/6/6f/Boops_boops_Karpathos_01.JPG",
    "rascasse": "https://upload.wikimedia.org/wikipedia/commons/7/7f/Scorpaena_scrofa_02.JPG",
    "sabre": "https://upload.wikimedia.org/wikipedia/commons/8/82/Trichiurus_lepturus_%28RFEIMG-0382%29.jpg",
    "homard": "https://upload.wikimedia.org/wikipedia/commons/1/18/KreeftbijDenOsse.jpg",
    "pagre": "https://upload.wikimedia.org/wikipedia/commons/9/94/Pargo_com%C3%BAn_%28Pagrus_pagrus%29%2C_Parque_natural_de_la_Arr%C3%A1bida%2C_Portugal%2C_2021-09-09%2C_DD_36.jpg",
    "saint_pierre": "https://upload.wikimedia.org/wikipedia/commons/a/a6/Zeus.faber.jpg",
    "poulpe": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Octopus_vulgaris_2.jpg",
    "sardine": "https://upload.wikimedia.org/wikipedia/commons/6/6a/Sardina_pilchardus1.jpg",
    "sar": "https://upload.wikimedia.org/wikipedia/commons/6/62/Diplodus_sargus.jpg",
    "rouget": "https://upload.wikimedia.org/wikipedia/commons/e/e1/Mullus_surmuletus.jpg",
    "baudroie": "https://upload.wikimedia.org/wikipedia/commons/a/a3/Lophius_piscatorius.jpg",
    "besugue": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Pagellus_bogaraveo_-_Baron_Cuvier.jpg",
    "abadeche": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Pink_ling.jpg/640px-Pink_ling.jpg",
    "pouce_pied": "https://upload.wikimedia.org/wikipedia/commons/0/07/Pollicipes_pollicipes.jpg",
    "bonite": "https://upload.wikimedia.org/wikipedia/commons/b/bf/Sarda_sarda.jpg",
    "chinchard": "https://upload.wikimedia.org/wikipedia/commons/a/a1/Trachurus_trachurus.jpg",
    "maigre": "https://upload.wikimedia.org/wikipedia/commons/7/76/Argyrosomus_regius.jpg",
    "merou": "https://upload.wikimedia.org/wikipedia/commons/9/91/Merou.jpg",
    "alose": "https://upload.wikimedia.org/wikipedia/commons/5/5d/Alosa-alosa.png",
    "grondin": "https://upload.wikimedia.org/wikipedia/commons/2/20/Flying_gurnard.JPG",
    "turbot": "https://upload.wikimedia.org/wikipedia/commons/f/ff/FMIB_48896_Turbot.jpeg",
    "ombrine": "https://upload.wikimedia.org/wikipedia/commons/9/95/Umbrina_cirrosa_Italy_01.jpg",
    "merlu": "https://upload.wikimedia.org/wikipedia/commons/4/49/Merluccius_merluccius.jpg",
    "araignee": "https://upload.wikimedia.org/wikipedia/commons/9/91/Trachinus_araneus.jpg",
    "cernier": "https://upload.wikimedia.org/wikipedia/commons/a/af/Polyprion_americanus.jpg",
    "vive": "https://upload.wikimedia.org/wikipedia/commons/7/7d/Echiichthys_vipera.jpg",
    "carangue": "https://upload.wikimedia.org/wikipedia/commons/3/30/Crevalle_jack_aquarium.jpg",
    "vieille": "https://upload.wikimedia.org/wikipedia/commons/e/ee/Ballan_Wrasse.jpg",
    "thon_obese": "https://upload.wikimedia.org/wikipedia/commons/a/ac/Thunnus_obesus_%28bigeye_tuna%29.jpg",
    "albacore": "https://upload.wikimedia.org/wikipedia/commons/e/ed/Hooked_albacore_tuna.jpg",
    "mostelle": "https://upload.wikimedia.org/wikipedia/commons/6/65/Phycis_phycis.jpg",
    "dorade_grise": "https://upload.wikimedia.org/wikipedia/commons/d/dd/Spondyliosoma_cantharus.jpg",
    "sole": "https://upload.wikimedia.org/wikipedia/commons/8/87/Solea_solea.jpg",
    "sole_senegal": "https://upload.wikimedia.org/wikipedia/commons/5/50/Solea_senegalensis.jpg",
    "crevette_rose": "https://upload.wikimedia.org/wikipedia/commons/a/ae/Crevette_rose.jpg",
    "crevette": "https://upload.wikimedia.org/wikipedia/commons/5/52/White_shrimp.jpg",
    "requin_ha": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Galeorhinus_galeus.jpg",
    "requin": "https://upload.wikimedia.org/wikipedia/commons/e/e3/White_shark.jpg",
    "coquillages": "https://upload.wikimedia.org/wikipedia/commons/3/3a/Seashells_on_beach.jpg",
    "calamar_veine": "assets/images/wiki_calamar_veine.jpg",
    "crevette_grise": "assets/images/wiki_crevette_grise.jpg",
    "crevette_royale": "assets/images/wiki_crevette_royale.jpg",
    "emissole_lisse": "assets/images/wiki_emissole_lisse.jpg",
    "huitres": "assets/images/wiki_huitres.jpg",
    "moule_mediterraneenne": "assets/images/wiki_moule_mediterraneenne.jpg",
    "sole_ceteau": "assets/images/wiki_sole_ceteau.jpg",
    "sole_pole": "assets/images/wiki_sole_pole.png",
    "sole_rauradon_commune": "assets/images/wiki_sole_rauradon_commune.jpg",
    "sole_ocellee": "assets/images/wiki_sole_ocellee.jpg",
    "sole_perdrix": "assets/images/wiki_sole_perdrix.jpg",
    "squale_et_requin": "assets/images/wiki_squale_et_requin.jpg",
    "algue": "https://upload.wikimedia.org/wikipedia/commons/9/95/Sparus_aurata_Sardegna.jpg",
    "algue_rouge": "https://upload.wikimedia.org/wikipedia/commons/9/95/Sparus_aurata_Sardegna.jpg",
    "algue_gelidium": "https://upload.wikimedia.org/wikipedia/commons/9/95/Sparus_aurata_Sardegna.jpg",
    "baliste": "https://upload.wikimedia.org/wikipedia/commons/2/2a/Balistes_capriscus.jpg",
    "ananas": "https://upload.wikimedia.org/wikipedia/commons/5/52/Cleidopus_gloriamaris.jpg",
    "allache": "https://upload.wikimedia.org/wikipedia/commons/1/1a/Sardinella_aurita_2.jpg",
    "anguille": "https://upload.wikimedia.org/wikipedia/commons/2/23/Anguilla_anguilla.jpg",
    "hero_user": ""
}

def get_image_path(key):
    """Retourne le chemin de l'image (local si présent, sinon URL)."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    for ext in ['.jpg', '.png', '.jpeg']:
        local_filename = f"{key}{ext}"
        local_path = os.path.join(base_dir, "assets", "images", local_filename)
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
    "halle_onp_1": "Halle aux poissons moderne : Digitalisation des flux",
    "halle_onp_2": "Vente à la crie : Transparence et efficacité",
    "port_onp_1": "Infrastructure portuaire : Ancrage national stratégique",
    "port_agadir_new": "Port d'Agadir : Hub logistique et halieutique majeur",
    "showcase_secondary": "Modernisation des structures halieutiques",
}
