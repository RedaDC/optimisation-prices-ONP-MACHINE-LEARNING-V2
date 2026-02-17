
import pandas as pd
import os
import sys

# Mocking parts of the app to test data loading directly
sys.path.append('.')
from data_loader import extract_ml_data

def diagnostic():
    dr_file = 'New Report(2024-2025) -DR (3).xlsx'
    
    if not os.path.exists(dr_file):
        print(f"FAIL: {dr_file} not found at root.")
        return

    print(f"START: Testing extraction from {dr_file}")
    df = extract_ml_data(dr_file)
    
    if df is None:
        print("FAIL: extract_ml_data returned None.")
    elif df.empty:
        print("FAIL: extract_ml_data returned an empty DataFrame.")
    else:
        print(f"SUCCESS: Extracted {len(df)} rows.")
        print("Columns:", df.columns.tolist())
        print("Years found:", df['annee'].unique())
        print("Ports found:", len(df['port'].unique()))
        
        # Verify 2024 and 2025
        years = df['annee'].unique()
        if 2024 in years and 2025 in years:
            print("VERIFIED: 2024 and 2025 are both present.")
        else:
            print(f"WARNING: Missing years. Found only: {years}")

if __name__ == "__main__":
    diagnostic()
