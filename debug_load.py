
import pandas as pd
import os
from utils import clean_data, create_features

def test_load():
    if os.path.exists('onp_real_ml_data.csv'):
        df = pd.read_csv('onp_real_ml_data.csv')
        print(f"Initial shape: {df.shape}")
        
        if 'categorie' not in df.columns: df['categorie'] = 'Inconnue'
        if 'calibre' not in df.columns: df['calibre'] = 'Moyen'
        
        df_cleaned = clean_data(df)
        print(f"After clean_data: {df_cleaned.shape}")
        
        df_feat = create_features(df_cleaned)
        print(f"After create_features: {df_feat.shape}")
        
        if df_feat.empty:
            print("ERROR: Resulting DataFrame is empty!")
        else:
            print("SUCCESS: Data loaded and processed correctly.")
            print(df_feat.head())
    else:
        print("ERROR: onp_real_ml_data.csv not found!")

if __name__ == "__main__":
    test_load()
