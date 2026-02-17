import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta


def generate_mock_data(n_rows=2000):
    """
    Génère des données simulées.
    Si 'ca_reduction_2024_2025.csv' existe, on s'aligne sur ces données (Ports, Espèces, Volume approx).
    Sinon, on utilise des valeurs par défaut.
    """
    import os
    
    # 1. Tentative de chargement du rapport réel pour calibration
    real_data_path = 'ca_reduction_2024_2025.csv'
    use_real_distribution = False
    
    ports_dist = ["Casablanca", "Agadir", "Tanger", "Dakhla", "Safi", "Larache"]
    species_list = ["Sardine", "Crevette", "Merlan", "Poulpe", "Espadon", "Sole", "Calamar"]
    
    if os.path.exists(real_data_path):
        try:
            df_real = pd.read_csv(real_data_path)
            # Extraire les ports uniques et espèces
            if 'port' in df_real.columns:
                real_ports = df_real['port'].unique().tolist()
                if len(real_ports) > 0:
                    ports_dist = real_ports
                    use_real_distribution = True
            
            if 'espece_categorie' in df_real.columns:
                real_species = df_real['espece_categorie'].unique().tolist()
                # Nettoyer les espèces (parfois c'est des catégories)
                species_list = [s for s in real_species if isinstance(s, str) and len(s) > 2]
                
            print(f"Calibration sur rapport réel : {len(ports_dist)} ports, {len(species_list)} espèces.")
        except Exception as e:
            print(f"Erreur lecture rapport réel, repli sur défaut : {e}")

    # Configuration des espèces (Prix et catégorie)
    # On essaie de mapper si on a chargé des espèces réelles, sinon défaut
    species_config = []
    
    categories = ["Pélagique", "Crustacé", "Poisson Blanc", "Céphalopode", "Espèce Noble"]
    
    for sp_name in species_list:
        # Estimation basique des propriétés
        base_price = 20 # Défaut
        cat = "Poisson Blanc" # Défaut
        
        lower_name = str(sp_name).lower()
        if "sardine" in lower_name or "anchois" in lower_name or "maquereau" in lower_name:
            base_price = 8
            cat = "Pélagique"
        elif "crevette" in lower_name or "homard" in lower_name:
            base_price = 120
            cat = "Crustacé"
        elif "poulpe" in lower_name or "calamar" in lower_name or "seiche" in lower_name:
            base_price = 70
            cat = "Céphalopode"
        elif "espadon" in lower_name or "thon" in lower_name:
            base_price = 90
            cat = "Espèce Noble"
        elif "merlan" in lower_name or "sole" in lower_name:
            base_price = 50
            cat = "Poisson Blanc"
        else:
            base_price = np.random.randint(15, 60)
            cat = random.choice(categories)
            
        species_config.append({
            "name": sp_name,
            "base_price": base_price,
            "volatility": 0.15,
            "category": cat
        })
    
    calibres = ["T1", "T2", "T3", "T4", "Mix"]
    
    data = []
    # Génération sur 2024 et 2025 pour coller au rapport
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 12, 31)
    days_range = (end_date - start_date).days
    
    for i in range(n_rows):
        # Distribution aléatoire de date
        date = start_date + timedelta(days=random.randint(0, days_range))
        
        # Sélection port/espèce
        port = random.choice(ports_dist)
        sp = random.choice(species_config)
        calibre = random.choice(calibres)
        
        # Facteurs d'influence
        is_ramadan = 1 if (datetime(2024, 3, 11) <= date <= datetime(2024, 4, 10)) or \
                           (datetime(2025, 2, 28) <= date <= datetime(2025, 3, 30)) else 0
        is_summer = 1 if (6 <= date.month <= 8) else 0
        
        # Volume débarqué
        volume = np.random.gamma(shape=2, scale=800)
        
        # boost volume si on utilise la distribution réelle pour avoir des gros chiffres
        if use_real_distribution:
             volume *= 2.5 

        # Prix
        price = sp['base_price']
        if is_ramadan and sp['category'] == "Poisson Blanc": price *= 1.3
        if is_summer: price *= 1.15
        
        # Elasticité prix/volume
        price *= (1 - 0.08 * np.log1p(volume/1000))
        price += np.random.normal(0, price * sp['volatility'])
        
        data.append({
            "date_vente": date.strftime("%Y-%m-%d"),
            "port": port,
            "espece": sp['name'],
            "categorie": sp['category'],
            "calibre": calibre,
            "volume_kg": round(volume, 2),
            "is_ramadan": is_ramadan,
            "is_summer": is_summer,
            "prix_unitaire_dh": max(2, round(price, 2))
        })
        
    df = pd.DataFrame(data)
    df.sort_values("date_vente", inplace=True)
    return df

if __name__ == "__main__":
    df_mock = generate_mock_data(2000)
    # Sauvegarde dans le workspace de l'utilisateur
    output_path = "donnees_simulation_onp.csv"
    df_mock.to_csv(output_path, index=False)
    print(f"Simulation terminée : {len(df_mock)} lignes générées dans {output_path}")
