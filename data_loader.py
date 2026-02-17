import pandas as pd
import numpy as np
import os

def extract_ml_data(file_input, output_path='onp_real_ml_data.csv'):
    """
    Extrait les données mensuelles détaillées pour l'entraînement du Machine Learning.
    Transforme le format 'large' de Feuil2 en format 'long'.
    """
    print(f"DEBUG: Loading {file_input}...")
    try:
        xl = pd.ExcelFile(file_input)
        print(f"DEBUG: Sheets found: {xl.sheet_names}")
        
        # Use first sheet if Page1_1 is found or fallback to first
        sheet_name = 'Page1_1' if 'Page1_1' in xl.sheet_names else xl.sheet_names[0]
        print(f"DEBUG: Using sheet: {sheet_name}")
        
        df = xl.parse(sheet_name, header=None)
        print(f"DEBUG: Dataset shape: {df.shape}")
        
    except Exception as e:
        print(f"Erreur lecture ML data: {e}")
        return None

    row_year = df.iloc[0].ffill().astype(str).tolist()
    row_month = df.iloc[1].astype(str).tolist()
    row_met = df.iloc[2].astype(str).tolist()
    
    data_raw = df.iloc[3:].copy()
    data_raw[0] = data_raw[0].ffill() # Port
    
    ml_records = []
    
    # Parcourir chaque colonne à partir de la 2ème
    for col_idx in range(2, df.shape[1]):
        year = row_year[col_idx]
        month = row_month[col_idx]
        metric = str(row_met[col_idx]).lower()
        
        # On ne prend que les colonnes mensuelles (pas les totaux)
        if month == 'nan' or month == '' or month == 'None':
            continue
            
        # On traite par paire Volume/CA. Pour simplifier, on cherche le Volume 
        # et on suppose que le CA est juste à côté (structure habituelle de l'Excel)
        if "volume" in metric:
            # Chercher le CA correspondant (généralement col suivante)
            ca_col_idx = col_idx + 1
            if ca_col_idx < df.shape[1] and ("ca" in str(row_met[ca_col_idx]).lower() or "chiffre" in str(row_met[ca_col_idx]).lower()):
                
                for _, row in data_raw.iterrows():
                    port = row[0]
                    species = row[1]
                    vol = str(row[col_idx]).replace(' ', '').replace(',', '.')
                    ca = str(row[ca_col_idx]).replace(' ', '').replace(',', '.')
                    
                    try:
                        v_val = float(vol)
                        c_val = float(ca)
                        if v_val > 0:
                            price = c_val / v_val # Prix unitaire en KDh/T -> DH/kg (c'est la même chose)
                            ml_records.append({
                                'port': port,
                                'espece': species,
                                'annee': int(float(year)),
                                'mois': int(float(month)),
                                'volume_kg': v_val * 1000,
                                'prix_unitaire_dh': price
                            })
                    except Exception as e:
                        # print(f"Skip row: {vol} / {ca} - {e}")
                        continue
    
    print(f"DEBUG: Records found: {len(ml_records)}")
    
    ml_df = pd.DataFrame(ml_records)
    if not ml_df.empty:
        # Nettoyage additionnel
        ml_df = ml_df.dropna()
        ml_df.to_csv(output_path, index=False)
        print(f"DONE: Dataset ML genere: {output_path} ({len(ml_df)} lignes)")
        return ml_df
    return None

def process_onp_report(file_input, output_path=None):
    """
    Traite le rapport ONP (Excel) et retourne un DataFrame nettoyé.
    Priorise la feuille 'Feuil2' qui contient les totaux annuels explicites.
    """
    try:
        xl = pd.ExcelFile(file_input)
        # On cherche Feuil2 ou similar, sinon la première feuille
        sheet_name = 'Feuil2' if 'Feuil2' in xl.sheet_names else xl.sheet_names[0]
        df = xl.parse(sheet_name, header=None)
    except Exception as e:
        print(f"Erreur lecture Excel: {e}")
        return None
    
    if df.shape[1] < 5: 
        return None

    # --- LOGIQUE DE DÉTECTION DES COLONNES ---
    # Ligne 0: Années
    # Ligne 1: Mois (ou vide pour les totaux)
    # Ligne 2: Métriques
    
    row_year = df.iloc[0].astype(str).tolist()
    row_month = df.iloc[1].astype(str).tolist()
    row_met = df.iloc[2].astype(str).tolist()
    
    # On cherche les colonnes TOTALES pour CA et Volume
    col_ca_2024, col_vol_2024 = None, None
    col_ca_2025, col_vol_2025 = None, None
    
    # Split 2024 / 2025
    idx_2025 = 25 # Default
    for i, y in enumerate(row_year):
        if "2025" in str(y): 
            idx_2025 = i
            break

    for i in range(df.shape[1]):
        met = str(row_met[i]).lower()
        mon = str(row_month[i]).lower()
        
        is_total = mon == 'nan' or mon == '' or 'total' in met
        if i < 2: continue
        
        if is_total:
            if "volume" in met:
                if i < idx_2025: 
                    if col_vol_2024 is None: col_vol_2024 = i
                else: 
                    if col_vol_2025 is None: col_vol_2025 = i
            elif "ca" in met or "chiffre" in met:
                if i < idx_2025: 
                    if col_ca_2024 is None: col_ca_2024 = i
                else: 
                    if col_ca_2025 is None: col_ca_2025 = i

    # Si on n'a pas trouvé les colonnes totales (ex: Page1_1), on somme les mois
    # (Cas de repli pour plus de robustesse)
    
    data_raw = df.iloc[3:].copy().reset_index(drop=True)
    def to_float(x):
        try: return float(str(x).replace(' ', '').replace(',', '.'))
        except: return 0.0

    # Helper function to get or sum
    def get_column_data(idx_total, metric_keyword, start_y, end_y):
        if idx_total is not None:
            return data_raw[idx_total].apply(to_float)
        else:
            # Sommations des mois
            series = pd.Series(0.0, index=data_raw.index)
            for j in range(start_y, end_y):
                if metric_keyword in str(row_met[j]).lower() and 'nan' not in str(row_month[j]).lower():
                    series += data_raw[j].apply(to_float)
            return series

    ca_2024 = get_column_data(col_ca_2024, "ca", 2, idx_2025)
    ca_2025 = get_column_data(col_ca_2025, "ca", idx_2025, df.shape[1])
    vol_2024 = get_column_data(col_vol_2024, "volume", 2, idx_2025)
    vol_2025 = get_column_data(col_vol_2025, "volume", idx_2025, df.shape[1])

    final_df = pd.DataFrame({
        'port': data_raw[0],
        'espece_categorie': data_raw[1],
        'ca_2024_kdh': ca_2024,
        'ca_2025_kdh': ca_2025,
        'vol_2024_t': vol_2024,
        'vol_2025_t': vol_2025
    })
    
    final_df['port'] = final_df['port'].ffill()
    final_df = final_df[(final_df['ca_2024_kdh'] > 0) | (final_df['ca_2025_kdh'] > 0) | 
                        (final_df['vol_2024_t'] > 0) | (final_df['vol_2025_t'] > 0)]
    
    # --- MAPPING DÉLÉGATION (DR) DYNAMIQUE ---
    map_dict = {}
    try:
        # Priorité à Feuil5 pour les noms complets
        if 'Feuil5' in xl.sheet_names:
            df5 = xl.parse('Feuil5')
            if 'PORT' in df5.columns and 'DR' in df5.columns:
                m5 = df5[['PORT', 'DR']].dropna().drop_duplicates()
                for _, row in m5.iterrows():
                    p, dr = str(row['PORT']).strip().upper(), str(row['DR']).strip().upper()
                    map_dict[p] = dr
        
        # Complément avec Feuil1
        if 'Feuil1' in xl.sheet_names:
            df1 = xl.parse('Feuil1')
            if 'PORT' in df1.columns and 'DR' in df1.columns:
                m1 = df1[['PORT', 'DR']].dropna().drop_duplicates()
                for _, row in m1.iterrows():
                    p, dr = str(row['PORT']).strip().upper(), str(row['DR']).strip().upper()
                    if p not in map_dict: map_dict[p] = dr
    except Exception as e:
        print(f"Erreur extraction mapping: {e}")

    def get_delegation(p):
        p_up = str(p).strip().upper()
        dr = map_dict.get(p_up, 'AUTRE')
        
        # Standardisation vers les noms officiels de Feuil6
        if dr == 'LSH': return 'LAAYOUNE SAKIA LHAMRA'
        if dr == 'CS': return 'CASA SETTAT'
        if dr == 'MS': return 'MARRAKECH SAFI'
        if dr == 'GON': return 'GON'
        if 'DAKHLA' in dr: return 'DAKHLA OUED EDAHAB'
        if 'TANGER' in dr: return 'TANGER TETOUAN AL HCOEIMA'
        if 'MARRAKECH' in dr: return 'MARRAKECH SAFI'
        if 'ORIENTAL' in dr: return 'ORIENTALE'
        return dr

    final_df['delegation'] = final_df['port'].apply(get_delegation)
    
    final_df['ca_diff_kdh'] = final_df['ca_2025_kdh'] - final_df['ca_2024_kdh']
    final_df['reduction_pct'] = np.where(final_df['ca_2024_kdh'] > 0, (final_df['ca_diff_kdh']/final_df['ca_2024_kdh'])*100, 0)
    
    if output_path:
        final_df.to_csv(output_path, index=False)
        print(f"Extraction terminee via feuille '{sheet_name}'")
        print(f"Total CA 2024: {final_df['ca_2024_kdh'].sum():,.2f} KDh")
        print(f"Total Vol 2024: {final_df['vol_2024_t'].sum():,.2f} Tonnes")
        
    return final_df
