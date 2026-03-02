
import os
import requests

IMG_DIR = r"c:\Users\reda\Downloads\optimisation-machine-learning--master (1)\assets\images"

images = {
    "wiki_moule_mediterraneenn.jpg": "https://upload.wikimedia.org/wikipedia/commons/4/4b/Mytilus_galloprovincialis_shell.jpg",
    "wiki_crevette_rose.jpg": "https://upload.wikimedia.org/wikipedia/commons/2/2a/Gamba_blanca_01.JPG",
    "wiki_crevette_grise.jpg": "https://upload.wikimedia.org/wikipedia/commons/e/e0/Crangon_crangon_%28dorsal%29.jpg",
    "wiki_huitres.jpg": "https://upload.wikimedia.org/wikipedia/commons/b/b3/Crassostrea_gigas_01.jpg",
    "wiki_calmar.jpg": "https://upload.wikimedia.org/wikipedia/commons/1/1a/Loligo_vulgaris.jpg",
    "wiki_sole_ruardon_commune.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Solea_senegalensis.jpg/1200px-Solea_senegalensis.jpg",
    "wiki_mulet_dore.jpg": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Liza_aurata.jpg",
    "wiki_requin_ha.jpg": "https://upload.wikimedia.org/wikipedia/commons/e/e6/Galeorhinus_galeus.jpg",
    "wiki_sparaillon_commun.jpg": "https://upload.wikimedia.org/wikipedia/commons/b/b5/Diplodus_annularis_%28Linnaeus%2C_1758%29.jpg"
}

def download_images():
    if not os.path.exists(IMG_DIR):
        os.makedirs(IMG_DIR)
        
    for name, url in images.items():
        try:
            print(f"Downloading {name}...")
            r = requests.get(url, timeout=20, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code == 200:
                with open(os.path.join(IMG_DIR, name), 'wb') as f:
                    f.write(r.content)
                print(f"Successfully downloaded {name}")
            else:
                print(f"Failed to download {name}: Status {r.status_code}")
        except Exception as e:
            print(f"Error downloading {name}: {e}")

if __name__ == '__main__':
    download_images()
