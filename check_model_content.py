import joblib
import pandas as pd
from ml_models import ONPPricePredictor

def check_model():
    predictor = ONPPricePredictor()
    if predictor.load_model('models/best_model.pkl'):
        print(predictor.results.keys())
        for k, v in predictor.results.items():
            print(f"{k}: R2={v.get('R2')}")
    else:
        print("Model not loaded.")

check_model()
