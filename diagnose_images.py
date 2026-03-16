
import pandas as pd
import os
import requests
from utils import get_species_image_path, normalize_species_name, get_unique_valid_species
from onp_assets import IMAGES_PECHE_MAROC

def check_image_status(species_name):
    path = get_species_image_path(species_name)
    normalized = normalize_species_name(species_name)
    default_img = IMAGES_PECHE_MAROC.get("marche_poisson", "")
    
    status = "OK"
    error_detail = ""
    
    if not path or path == default_img:
        status = "FALLBACK"
        error_detail = "Uses default image"
    elif path.startswith("http"):
        try:
            # Check if URL is valid (lightweight check)
            r = requests.head(path, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code >= 400:
                status = "BROKEN_URL"
                error_detail = f"HTTP {r.status_code}"
        except Exception as e:
            status = "URL_ERROR"
            error_detail = str(e)
    else:
        if not os.path.exists(path):
            status = "MISSING_FILE"
            error_detail = f"File not found: {path}"
            
    return {
        "Species": species_name,
        "Normalized": normalized,
        "Path/URL": path,
        "Status": status,
        "Detail": error_detail
    }

def run_diagnostic():
    # Load data
    data_file = 'onp_reinforced_ml_data.csv' if os.path.exists('onp_reinforced_ml_data.csv') else 'onp_real_ml_data.csv'
    df = pd.read_csv(data_file)
    
    # Get species exactly as seen in UI
    ui_species = get_unique_valid_species(df)
    
    results = []
    print(f"Checking {len(ui_species)} UI species...")
    
    for sp in ui_species:
        print(f"  Diagnosing: {sp}", end="\r")
        results.append(check_image_status(sp))
    
    report_df = pd.DataFrame(results)
    
    # Filter for problems
    problems = report_df[report_df['Status'] != 'OK']
    
    print("\n\n--- Diagnostic Report ---")
    print(f"Total checked: {len(report_df)}")
    print(f"OK: {len(report_df[report_df['Status'] == 'OK'])}")
    print(f"Problems found: {len(problems)}")
    
    if not problems.empty:
        print("\nProblematic Species:")
        print(problems[['Species', 'Status', 'Detail']].to_string(index=False))
        
    report_df.to_csv('image_diagnostic_report.csv', index=False)
    print("\nFull report saved to 'image_diagnostic_report.csv'")

if __name__ == "__main__":
    run_diagnostic()
