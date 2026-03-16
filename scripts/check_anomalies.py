import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from ml_models import ONPPricePredictor
from ml_operations import detect_market_anomalies
from utils import clean_data, create_features

def main():
    # Load data
    data_file = 'onp_reinforced_ml_data.csv'
    if not os.path.exists(data_file):
        data_file = 'onp_real_ml_data.csv'
    
    df = pd.read_csv(data_file)
    df = clean_data(df)
    df = create_features(df)
    
    # Load model
    predictor = ONPPricePredictor()
    model_path = 'models/best_model.pkl'
    if os.path.exists(model_path):
        predictor.load_model(model_path)
    else:
        # Train if not exists (unlikely given the app state)
        X_train, X_test, y_train, y_test = predictor.prepare_data(df)
        predictor.train_models(X_train, X_test, y_train, y_test)
    
    # Detect anomalies
    anomalies = detect_market_anomalies(df, predictor)
    
    if not anomalies.empty:
        print(f"Detected {len(anomalies)} anomalies:")
        print(anomalies[['date', 'espece', 'port', 'actual_price', 'expected_price', 'deviation_pct', 'severity']])
    else:
        print("No anomalies detected.")

if __name__ == "__main__":
    main()
