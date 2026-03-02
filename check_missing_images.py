
import os
import pandas as pd
import re
import unicodedata

IMG_DIR = r"c:\Users\reda\Downloads\optimisation-machine-learning--master (1)\assets\images"
CSV_PATH = r"c:\Users\reda\Downloads\optimisation-machine-learning--master (1)\species_global_avg_prices.csv"

def normalize(name):
    name = str(name).lower().strip()
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    name = re.sub(r'[\s\-]+', '_', name)
    name = re.sub(r'[^a-z0-9_]', '', name)
    return name

def get_base_name(species):
    s = species.strip()
    s = re.sub(r'\s+[GMPT]+$', '', s)
    s = re.sub(r'\s+GG$', '', s)
    s = re.sub(r'\s+\(PP\)$', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+COMMUN\s*G$', '', s, flags=re.IGNORECASE)
    s = re.sub(r'^[MPGT]\s+', '', s)
    return s.strip()

def has_image(base_key, all_imgs):
    for ext in ['.png', '.jpg']:
        if f"{base_key}{ext}" in all_imgs:
            return True
        if f"wiki_{base_key}{ext}" in all_imgs:
            return True
    return False

def check_missing():
    if not os.path.exists(CSV_PATH):
        print(f"CSV not found: {CSV_PATH}")
        return
    
    df = pd.read_csv(CSV_PATH)
    all_species = df['species'].dropna().unique().tolist()
    
    all_imgs = [f.lower() for f in os.listdir(IMG_DIR)]
    
    missing = []
    for sp in sorted(all_species):
        base = get_base_name(sp)
        base_key = normalize(base)
        if not has_image(base_key, all_imgs):
            missing.append((sp, base))
            
    print(f"Total species: {len(all_species)}")
    print(f"Missing images: {len(missing)}")
    for sp, base in missing[:20]:
        print(f"- {sp} (Base: {base})")
    if len(missing) > 20:
        print("...")

if __name__ == '__main__':
    check_missing()
