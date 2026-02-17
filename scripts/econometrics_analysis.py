import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

def analyze_elasticity():
    # Chargement
    df = pd.read_csv("donnees_simulation_onp.csv")
    
    # Pour l'élasticité, on utilise souvent le log-log model : log(prix) = alpha + beta * log(volume)
    # beta est alors l'élasticité prix par rapport au volume (ou inversement selon le sens)
    
    results = []
    species = df['espece'].unique()
    
    for sp in species:
        subset = df[df['espece'] == sp].copy()
        
        # Log transformation (ajout de 1 pour éviter log(0))
        subset['log_price'] = np.log(subset['prix_unitaire_dh'])
        subset['log_volume'] = np.log(subset['volume_kg'] + 1)
        
        # Régression linéaire : log(P) ~ log(V) + is_ramadan + is_summer
        X = subset[['log_volume', 'is_ramadan', 'is_summer']]
        X = sm.add_constant(X)
        y = subset['log_price']
        
        model = sm.OLS(y, X).fit()
        
        elasticity = model.params['log_volume']
        p_value = model.pvalues['log_volume']
        
        results.append({
            "Espece": sp,
            "Elasticite_Prix_Volume": round(elasticity, 4),
            "P-Value": round(p_value, 4),
            "Significatif": "Oui" if p_value < 0.05 else "Non"
        })
    
    df_elasticity = pd.DataFrame(results)
    print("\n--- Analyse d'Élasticité par Espèce ---")
    print(df_elasticity)
    
    # Interprétation pour le PFE
    print("\nInterprétation Économique :")
    for index, row in df_elasticity.iterrows():
        if row['Elasticite_Prix_Volume'] < 0:
            change = abs(row['Elasticite_Prix_Volume']) * 10
            print(f"- {row['Espece']} : Une augmentation de 10% du volume débarqué entraîne une baisse de prix de {change:.2f}%.")

if __name__ == "__main__":
    analyze_elasticity()
