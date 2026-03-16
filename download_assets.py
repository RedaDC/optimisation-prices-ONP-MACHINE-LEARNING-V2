
import os
import requests
import time

# Dossier de destination
IMG_DIR = r"c:\Users\reda\Downloads\optimisation-machine-learning--master (1)\assets\images"
os.makedirs(IMG_DIR, exist_ok=True)

# Liste des photos à télécharger (Sources Wikimedia Commons réelles)
IMAGES_TO_DOWNLOAD = {
    "sardine.jpg": "https://upload.wikimedia.org/wikipedia/commons/6/6a/Sardina_pilchardus1.jpg",
    "bonite.jpg": "https://upload.wikimedia.org/wikipedia/commons/b/bf/Sarda_sarda.jpg",
    "chinchard.jpg": "https://upload.wikimedia.org/wikipedia/commons/a/a1/Trachurus_trachurus.jpg",
    "maigre.jpg": "https://upload.wikimedia.org/wikipedia/commons/7/76/Argyrosomus_regius.jpg",
    "merou.jpg": "https://upload.wikimedia.org/wikipedia/commons/9/91/Merou.jpg",
    "alose.png": "https://upload.wikimedia.org/wikipedia/commons/5/5d/Alosa-alosa.png",
    "grondin.jpg": "https://upload.wikimedia.org/wikipedia/commons/2/20/Flying_gurnard.JPG",
    "turbot.jpg": "https://upload.wikimedia.org/wikipedia/commons/f/ff/FMIB_48896_Turbot.jpeg",
    "ombrine.jpg": "https://upload.wikimedia.org/wikipedia/commons/9/95/Umbrina_cirrosa_Italy_01.jpg",
    "merlu.jpg": "https://upload.wikimedia.org/wikipedia/commons/4/49/Merluccius_merluccius.jpg",
    "araignee.jpg": "https://upload.wikimedia.org/wikipedia/commons/9/91/Trachinus_araneus.jpg",
    "cernier.jpg": "https://upload.wikimedia.org/wikipedia/commons/a/af/Polyprion_americanus.jpg",
    "vive.jpg": "https://upload.wikimedia.org/wikipedia/commons/7/7d/Echiichthys_vipera.jpg",
    "carangue.jpg": "https://upload.wikimedia.org/wikipedia/commons/3/30/Crevalle_jack_aquarium.jpg",
    "vieille.jpg": "https://upload.wikimedia.org/wikipedia/commons/e/ee/Ballan_Wrasse.jpg",
    "thon_obese.jpg": "https://upload.wikimedia.org/wikipedia/commons/a/ac/Thunnus_obesus_%28bigeye_tuna%29.jpg",
    "albacore.jpg": "https://upload.wikimedia.org/wikipedia/commons/e/ed/Hooked_albacore_tuna.jpg",
    "mostelle.jpg": "https://upload.wikimedia.org/wikipedia/commons/6/65/Phycis_phycis.jpg",
    "dorade_grise.jpg": "https://upload.wikimedia.org/wikipedia/commons/d/dd/Spondyliosoma_cantharus.jpg",
    "sole.jpg": "https://upload.wikimedia.org/wikipedia/commons/8/87/Solea_solea.jpg",
    "crevette_rose.jpg": "https://upload.wikimedia.org/wikipedia/commons/a/ae/Crevette_rose.jpg",
    "crevette.jpg": "https://upload.wikimedia.org/wikipedia/commons/5/52/White_shrimp.jpg",
    "requin_ha.jpg": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Galeorhinus_galeus.jpg",
    "requin.jpg": "https://upload.wikimedia.org/wikipedia/commons/e/e3/White_shark.jpg",
    "bar.jpg": "https://upload.wikimedia.org/wikipedia/commons/6/6f/Dicentrarchus_labrax_177025102.jpg",
    "dorade_royale.jpg": "https://upload.wikimedia.org/wikipedia/commons/9/95/Sparus_aurata_Sardegna.jpg",
    "pageot.jpg": "https://upload.wikimedia.org/wikipedia/commons/4/45/Pagellus_erythrinus_France.jpg",
    "bogue.jpg": "https://upload.wikimedia.org/wikipedia/commons/6/6f/Boops_boops_Karpathos_01.JPG",
    "rascasse.jpg": "https://upload.wikimedia.org/wikipedia/commons/7/7f/Scorpaena_scrofa_02.JPG",
    "sabre.jpg": "https://upload.wikimedia.org/wikipedia/commons/8/82/Trichiurus_lepturus_%28RFEIMG-0382%29.jpg",
    "homard.jpg": "https://upload.wikimedia.org/wikipedia/commons/4/4d/Homarus_gammarus_-_Astice.jpg",
    "saint_pierre.jpg": "https://upload.wikimedia.org/wikipedia/commons/a/a6/Zeus.faber.jpg",
    "mulet_dore.jpg": "https://upload.wikimedia.org/wikipedia/commons/e/ee/Liza_aurata_Corsica.jpg"
}

def download_images():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    print(f"Début du téléchargement vers : {IMG_DIR}")
    
    for filename, url in IMAGES_TO_DOWNLOAD.items():
        path = os.path.join(IMG_DIR, filename)
        
        # On ne télécharge que si le fichier n'existe pas ou est trop petit
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            print(f"[-] {filename} existe déjà. Skip.")
            continue
            
        try:
            print(f"[+] Téléchargement de {filename}...")
            response = requests.get(url, headers=headers, timeout=20)
            if response.status_code == 200:
                with open(path, 'wb') as f:
                    f.write(response.content)
                print(f"    OK : {os.path.getsize(path)} octets")
            else:
                print(f"    ERREUR : Status {response.status_code}")
        except Exception as e:
            print(f"    ERREUR : {str(e)}")
        
        time.sleep(5) # Délai de sécurité Wikimedia

if __name__ == "__main__":
    download_images()
