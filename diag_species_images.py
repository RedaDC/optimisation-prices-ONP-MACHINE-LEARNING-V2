
import pandas as pd
import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from utils import normalize_species_name, has_real_species_image, get_species_image_path, load_default_data

df = load_default_data()

if df is not None:
    # Use the correct column name from the data
    col_name = "espece" if "espece" in df.columns else "Espèce" if "Espèce" in df.columns else None
    if col_name:
        all_raw = sorted(df[col_name].dropna().unique().tolist())
        print(f"Total raw species in data: {len(all_raw)}")
        
        missing_images = []
        has_images = []
        
        for s in all_raw:
            if has_real_species_image(s):
                has_images.append((s, normalize_species_name(s)))
            else:
                missing_images.append((s, normalize_species_name(s)))
                
        print(f"\nSpecies WITH images ({len(has_images)}):")
        # for s, n in has_images[:10]:
        #    print(f"  {s} -> {n}")
        
        print(f"\nSpecies MISSING images ({len(missing_images)}):")
        for s, n in missing_images:
            print(f"  {s} -> {n}")
    else:
        print("Species column not found in DataFrame.")
        print(f"Columns found: {df.columns.tolist()}")
else:
    print("DataFrame could not be loaded.")
