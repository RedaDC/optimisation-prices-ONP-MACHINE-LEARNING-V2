import joblib
import pandas as pd
import numpy as np

def check_model():
    data = joblib.load('models/best_model.pkl')
    model = data['model']
    features = data['feature_names']
    
    # Feature Importance
    if hasattr(model, 'feature_importances_'):
        importance = model.feature_importances_
        df_imp = pd.DataFrame({'feature': features, 'importance': importance}).sort_values('importance', ascending=False)
        print("\n--- FEATURE IMPORTANCE ---")
        print(df_imp)
    
    # Check a specific prediction manually
    # For POUCE-PIED, HALLE CASABLANCA, Volume 36.31
    # We need to know what features were generated.
    # The test script showed it predicted 8.32.
    
if __name__ == "__main__":
    check_model()
