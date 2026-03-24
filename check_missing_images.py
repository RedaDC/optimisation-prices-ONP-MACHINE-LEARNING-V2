
import pandas as pd
import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from utils import normalize_species_name
from onp_assets import IMAGES_PECHE_MAROC

def check_missing():
    df = pd.read_csv('donnees_simulation_onp.csv')
    all_species = df['espece'].dropna().unique()
    
    missing = []
    found = []
    
    for s in all_species:
        norm = normalize_species_name(s)
        if norm in IMAGES_PECHE_MAROC:
            found.append((s, norm))
        else:
            missing.append((s, norm))
            
    print(f"Total Species in Data: {len(all_species)}")
    print(f"Species with Images: {len(found)}")
    print(f"Species MISSING Images: {len(missing)}")
    
    print("\nTop Missing Species (first 50):")
    for s, n in sorted(missing)[:50]:
        print(f"  - {s} (norm: {n})")

if __name__ == "__main__":
    check_missing()
