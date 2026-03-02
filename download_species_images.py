"""
Script de téléchargement d'images réelles pour les espèces manquantes.
Utilise l'API Wikipedia pour trouver des images de poissons.
"""
import os
import re
import time
import requests
import pandas as pd
import unicodedata

IMG_DIR = os.path.join("assets", "images")

def normalize(name):
    """Normalise le nom pour la recherche: minuscules, sans accents, underscores."""
    name = str(name).lower().strip()
    # Supprimer accents
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    # Remplacer tirets/espaces par _
    name = re.sub(r'[\s\-]+', '_', name)
    # Supprimer caractères spéciaux
    name = re.sub(r'[^a-z0-9_]', '', name)
    return name

def get_base_name(species):
    """Extrait le nom de base en supprimant les suffixes de taille (G, M, P, T, GG)."""
    s = species.strip()
    # Supprimer suffixes courants: " G", " M", " P", " T", " GG", " (PP)", etc.
    s = re.sub(r'\s+[GMPT]+$', '', s)
    s = re.sub(r'\s+GG$', '', s)
    s = re.sub(r'\s+\(PP\)$', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+COMMUN\s*G$', '', s, flags=re.IGNORECASE)
    # Supprimer les préfixes de catégorie comme "M CREVETTE", "T CREVETTE", "P CREVETTE"
    s = re.sub(r'^[MPGT]\s+', '', s)
    return s.strip()

def search_wikipedia_image(query, lang='fr'):
    """Cherche une image sur Wikipedia via l'API."""
    # Essai avec le nom français d'abord, puis anglais
    for language in [lang, 'en']:
        try:
            # Recherche de la page Wikipedia
            search_url = f"https://{language}.wikipedia.org/w/api.php"
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': query,
                'srlimit': 3,
                'format': 'json',
                'srprop': 'snippet'
            }
            r = requests.get(search_url, params=params, timeout=10,
                           headers={'User-Agent': 'ONP-Fish-App/1.0 (educational)'})
            results = r.json().get('query', {}).get('search', [])
            if not results:
                continue

            # Prendre le premier résultat et chercher son image principale
            page_title = results[0]['title']
            image_url = f"https://{language}.wikipedia.org/w/api.php"
            img_params = {
                'action': 'query',
                'titles': page_title,
                'prop': 'pageimages',
                'pithumbsize': 800,
                'format': 'json'
            }
            r2 = requests.get(image_url, params=img_params, timeout=10,
                            headers={'User-Agent': 'ONP-Fish-App/1.0 (educational)'})
            pages = r2.json().get('query', {}).get('pages', {})
            for page in pages.values():
                thumb = page.get('thumbnail', {})
                if thumb and thumb.get('source'):
                    return thumb['source']
        except Exception as e:
            print(f"  Error searching '{query}' on {language}.wikipedia.org: {e}")
    return None

def download_image(url, save_path):
    """Télécharge une image depuis une URL."""
    try:
        r = requests.get(url, timeout=15, headers={'User-Agent': 'ONP-Fish-App/1.0'})
        if r.status_code == 200 and 'image' in r.headers.get('Content-Type', ''):
            with open(save_path, 'wb') as f:
                f.write(r.content)
            return True
    except Exception as e:
        print(f"  Download error: {e}")
    return False

def has_image(base_key):
    """Vérifie si une image existe déjà pour cette clé."""
    all_imgs = [f.lower() for f in os.listdir(IMG_DIR)]
    # Exact matches
    for ext in ['.png', '.jpg']:
        if f"{base_key}{ext}" in all_imgs:
            return True
    if f"wiki_{base_key}.jpg" in all_imgs:
        return True
    # Partial match
    if any(base_key in img for img in all_imgs):
        return True
    return False

def main():
    # Charger les espèces
    df = pd.read_csv("species_global_avg_prices.csv")
    all_species = sorted(df['species'].dropna().unique().tolist())
    
    # Grouper par nom de base pour éviter les doublons
    base_to_species = {}
    for sp in all_species:
        base = get_base_name(sp)
        base_key = normalize(base)
        if base_key not in base_to_species:
            base_to_species[base_key] = (base, sp)

    # Filtrer seulement les manquants
    to_download = []
    for base_key, (base_name, original) in base_to_species.items():
        if not has_image(base_key):
            to_download.append((base_key, base_name, original))

    print(f"Espèces uniques à télécharger: {len(to_download)}")
    
    # Requêtes de recherche pour les espèces marines en français et anglais
    SEARCH_OVERRIDES = {
        'merlu': 'merlu europeen poisson',
        'poulpe': 'poulpe commun octopus',
        'calamar': 'calmar commun loligo',
        'seiche': 'seiche commune poisson',
        'sardine': 'sardine atlantique poisson',
        'thon': 'thon rouge atlantique',
        'lotte': 'lotte de mer baudroie',
        'mulet': 'mulet lippe poisson',
        'grondin': 'grondin rouge gurnard fish',
        'rascasse': 'rascasse rouge scorpionfish',
        'sole': 'sole commune flatfish',
        'raie': 'raie commune stingray',
        'pageot': 'pageot rouge commun',
        'dorade': 'dorade grise sea bream',
        'homard': 'homard europeen lobster',
        'langouste': 'langouste rouge spiny lobster',
        'langoustine': 'langoustine norway lobster',
        'crevette': 'crevette rose shrimp',
        'turbot': 'turbot flatfish',
        'bar': 'bar commun sea bass',
        'maquereau': 'maquereau atlantique mackerel fish',
        'anchois': 'anchois europeen anchoveta',
        'moule': 'moule commune mussel',
        'oursin': 'oursin violet sea urchin',
        'pieuvre': 'pieuvre octopus vulgaris',
        'requin': 'requin bleu blue shark',
        'espadon': 'espadon swordfish',
        'listao': 'bonite ventre raye skipjack tuna',
        'bonite': 'bonite skipjack tuna fish',
        'merou': 'merou brun grouper fish',
        'saint_pierre': 'poisson saint pierre john dory',
        'ombrine': 'ombrine Atlantic croaker fish',
        'boops': 'bogue boop fish sea',
        'grondeur': 'grondeur metis grunt fish',
        'oblade': 'oblade saddle bream fish',
        'saupe': 'saupe salema porgy fish',
        'girelle': 'girelle commune rainbow wrasse',
        'vieille': 'vieille coquette wrasse fish',
        'serran': 'serran chevre comber fish',
        'murane': 'murene commune moray eel',
        'anguille': 'anguille commune european eel',
        'orphie': 'orphie garfish belone',
        'limande': 'limande sole dab flatfish',
        'flet': 'flet europeen flounder fish',
        'barbue': 'barbue brill flatfish',
        'chinchard': 'chinchard horse mackerel',
        'palomette': 'palomette pomfret fish',
        'liche': 'liche commune amberjack fish',
        'tassergal': 'tassergal bluefish pomatomus',
        'maigre': 'maigre meagre argyrosomus fish',
        'sabre': 'poisson sabre cutlassfish trichiurus',
        'poisson_lune': 'poisson lune mola mola sunfish',
        'pretre': 'pretre silverside fish',
        'sprat': 'sprat clupea sprattus fish',
        'hareng': 'hareng atlantique herring fish',
        'thazard': 'thazard blanc king mackerel fish',
        'voilier': 'voilier atlantique sailfish',
        'esturgeon': 'esturgeon sturgeon fish',
    }
    
    downloaded = 0
    skipped = 0
    failed = 0
    
    for i, (base_key, base_name, original) in enumerate(to_download):
        save_path = os.path.join(IMG_DIR, f"wiki_{base_key}.jpg")
        
        # Construire la requête de recherche
        query = SEARCH_OVERRIDES.get(base_key, f"{base_name} poisson marin")
        
        print(f"[{i+1}/{len(to_download)}] Recherche: '{base_name}' -> query: '{query}'")
        
        img_url = search_wikipedia_image(query)
        
        if img_url:
            # Vérifier que c'est bien une image de poisson (éviter les logos, cartes etc.)
            if any(skip in img_url.lower() for skip in ['logo', 'flag', 'map', 'icon', 'badge', 'emblem']):
                print(f"  Skipped (non-fish image): {img_url}")
                failed += 1
            elif download_image(img_url, save_path):
                print(f"  Downloaded: {save_path}")
                downloaded += 1
            else:
                print(f"  Download failed for {img_url}")
                failed += 1
        else:
            print(f"  No image found on Wikipedia")
            failed += 1
        
        # Politesse: pause entre les requêtes
        time.sleep(0.3)
    
    print(f"\n=== RÉSULTAT ===")
    print(f"Téléchargées: {downloaded}")
    print(f"Échouées: {failed}")
    print(f"Total traité: {downloaded + failed}")

if __name__ == '__main__':
    main()
