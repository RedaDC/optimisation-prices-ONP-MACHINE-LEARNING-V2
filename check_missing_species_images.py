
import pandas as pd
import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from utils import normalize_species_name, has_real_species_image

# Directly read the CSV known to exist from app_premium.py and file list
csv_path = 'onp_real_ml_data.csv'

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    all_raw = sorted(df['espece'].dropna().unique().tolist())
    print(f"Total raw species in {csv_path}: {len(all_raw)}")
    
    missing_images = []
    has_images = []
    
    for s in all_raw:
        if has_real_species_image(s):
            has_images.append(s)
        else:
            missing_images.append(s)
            
    print(f"\nSpecies WITH images ({len(has_images)}):")
    for s in has_images[:5]:
        print(f"  - {s}")
    print("  ...")
    
    print(f"\nSpecies MISSING images ({len(missing_images)}):")
    for s in missing_images:
        print(f"  - {s}")
else:
    print(f"File {csv_path} not found.")
