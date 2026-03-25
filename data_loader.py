import pandas as pd
import numpy as np
import os

def extract_ml_data(file_input, output_path='onp_real_ml_data.csv'):
    """
    Extrait les données mensuelles détaillées pour l'entraînement du Machine Learning.
    Version robuste : Scan intelligent des en-têtes pour détecter Port, Espèce, Dates et Métriques.
    """
    # print(f"--- TRACE: Beginning extraction for {file_input}")
    try:
        xl = pd.ExcelFile(file_input)
        
        # 1. Sélection de la meilleure feuille
        sheet_candidates = []
        for sn in xl.sheet_names:
            try:
                df_test = xl.parse(sn, header=None, nrows=20)
                if df_test.empty: continue
                
                keywords = ["volume", "ca", "chiffre", "cas", "recette", "espece", "port"]
                score = 0
                for i in range(min(15, len(df_test))):
                    row_vals = [str(x).lower() for x in df_test.iloc[i].dropna().tolist()]
                    row_score = sum(1 for k in keywords if any(k in v for v in row_vals))
                    score = max(score, row_score)
                
                # Bonus pour les noms de feuilles explicites
                sn_lower = sn.lower()
                if any(x in sn_lower for x in ["extract", "brute", "data", "base", "real"]): score += 2
                if any(x in sn_lower for x in ["variant", "compar", "delta", "recap"]): score -= 1
                
                # Bonus pour les feuilles larges (plus de colonnes = souvent plus de mois)
                if df_test.shape[1] > 10: score += 1
                
                sheet_candidates.append((sn, score))
            except: continue
            
        if sheet_candidates:
            sheet_candidates.sort(key=lambda x: x[1], reverse=True)
            # Priorité aux feuilles qui semblent être des extractions brutes pour avoir tout le détail
            best_candidates = [s for s, score in sheet_candidates if "brute" in s.lower() or "extraction" in s.lower()]
            sheet_name = best_candidates[0] if best_candidates else sheet_candidates[0][0]
            # print(f"--- TRACE: Best sheet candidate: '{sheet_name}' (score {sheet_candidates[0][1]})")
        else:
            sheet_name = xl.sheet_names[0]
            # print(f"--- TRACE: No candidates, using first sheet: '{sheet_name}'")
            
        df = xl.parse(sheet_name, header=None)
    except Exception as e:
        # print(f"--- TRACE ERROR: {e}")
        return None

    # 2. Identification de la ligne d'en-tête principale
    header_idx = -1
    max_score = 0
    keywords_main = ["volume", "ca", "chiffre", "esp", "port"]
    for i in range(min(25, len(df))):
        row_vals = [str(x).lower() for x in df.iloc[i].dropna().tolist()]
        score = sum(1 for k in keywords_main if any(k in v for v in row_vals))
        if score > max_score:
            max_score = score
            header_idx = i
            
    if header_idx == -1:
        # print("--- TRACE: Could not identify header row.")
        return None
    # print(f"--- TRACE: Header row identified at index {header_idx}")
    
    # 3. Scan des colonnes
    header_area = df.iloc[:header_idx+1].copy()
    
    # Remplissage intelligent des headers fusionnés (ex: Années)
    for r in range(header_area.shape[0]):
        # version future-safe pour ffill
        header_area.iloc[r] = header_area.iloc[r].ffill()
    
    col_port = 0
    col_species = 1
    main_row_strs = [str(x).lower() for x in df.iloc[header_idx].tolist()]
    
    # Détection plus fine
    found_port = False
    found_species = False
    for i, val in enumerate(main_row_strs):
        if not found_port and any(k in val for k in ["port", "halles", "entité"]): 
            col_port = i
            found_port = True
        elif not found_species and "esp" in val: 
            col_species = i
            found_species = True
            
    # Correction spécifique pour les rapports de type 'Variation' ou 'DR'
    if main_row_strs[0] == 'dr/espece' or main_row_strs[0] == 'dr':
        col_port = 0
        col_species = 0 # Dans certains cas ils sont fusionnés ou un seul suffit
        # Mais si on a 'Entité' en col 1, c'est le port
        if len(main_row_strs) > 1 and "entité" in main_row_strs[1]:
            col_port = 1
            col_species = 4 # Souvent l'espèce est plus loin (col 4 pour esp)
        elif len(main_row_strs) > 4 and "esp" in main_row_strs[4]:
            col_species = 4

    # print(f"--- TRACE: Port column: {col_port}, Species column: {col_species} (Source: {main_row_strs[:6]})")

    ml_records = []
    import re
    
    for c in range(max(col_port, col_species) + 1, df.shape[1]):
        col_headers = [str(x).lower().strip() for x in header_area[c].tolist() if pd.notna(x)]
        full_header_str = " ".join(col_headers)
        
        if "volume" in full_header_str and all(x not in full_header_str for x in ["cumul", "total", "variation"]):
            # Extract year from volume header first
            vol_year = None
            for h_val in col_headers:
                y_match = re.search(r'(202[0-9])', h_val)
                if y_match: 
                    vol_year = int(y_match.group(1))
                    break
            
            ca_idx = -1
            # Search for CA column nearby with SAME year
            for offset in [1, -1, 2, -2, 3, -3, 4, -4]:
                test_c = c + offset
                if 0 <= test_c < df.shape[1]:
                    test_headers = [str(x).lower().strip() for x in header_area[test_c].tolist() if pd.notna(x)]
                    test_header_str = " ".join(test_headers)
                    if any(x in test_header_str for x in ["ca", "chiffre", "recette", "cas"]):
                        # Verify year match
                        if vol_year:
                            test_year = None
                            for th in test_headers:
                                ty_match = re.search(r'(202[0-9])', th)
                                if ty_match:
                                    test_year = int(ty_match.group(1))
                                    break
                            if test_year == vol_year:
                                ca_idx = test_c
                                break
                        else:
                            ca_idx = test_c
                            break
            
            if ca_idx != -1:
                year, month = vol_year, None
                for h_val in col_headers:
                    if h_val == 'nan' or not h_val.strip(): continue
                    if not year:
                        y_match = re.search(r'(202[0-9])', h_val)
                        if y_match: year = int(y_match.group(1))
                    if not month:
                        month_map = {
                             'jan': 1, 'fév': 2, 'mar': 3, 'avr': 4, 'mai': 5, 'jui': 6, 'jul': 7, 
                             'aoû': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'déc': 12, 'janv': 1, 
                             'fevr': 2, 'mars': 3, 'avri': 4, 'juin': 6, 'juil': 7, 'aout': 8, 
                             'sept': 9, 'octo': 10, 'nove': 11, 'dece': 12
                        }
                        for m_name, m_num in month_map.items():
                            if m_name in h_val: 
                                month = m_num
                                break
                        if not month:
                            m_match = re.search(r'\b(0?[1-9]|1[0-2])\b', h_val)
                            if m_match and len(h_val) <= 5: month = int(m_match.group(1))
                
                if year and not month:
                    month = 12
                    # print(f"--- TRACE: Annual data detected for {year}, defaulting to month 12")

                if year and month:
                    # print(f"--- TRACE: Processing Col {c} (Vol) & {ca_idx} (CA) for {month}/{year}")
                    data_slice = df.iloc[header_idx + 1:].copy()
                    current_port = "Unknown"
                    found_in_col = 0
                    
                    for idx, v_raw in data_slice[c].items():
                        c_raw = data_slice.loc[idx, ca_idx]
                        raw_val_0 = str(data_slice.loc[idx, 0]).strip()
                        
                        if col_port == col_species:
                             if pd.isna(v_raw) or str(v_raw).lower() == 'nan':
                                 if len(raw_val_0) > 1 and "total" not in raw_val_0.lower(): current_port = raw_val_0
                                 continue
                             p, s = current_port, raw_val_0
                        else:
                             p = str(data_slice.loc[idx, col_port]).strip()
                             s = str(data_slice.loc[idx, col_species]).strip()
                        
                        if not p or p.lower() == 'nan' or 'total' in p.lower(): continue
                        
                        # Fix MG: If species is missing or "total", check if it's an MG row which often has aggregate data
                        if not s or s.lower() == 'nan' or 'total' in s.lower():
                            if "MG " in p.upper():
                                s = "TOUTES ESPECES (MG)"
                            else:
                                continue
                        
                        try:
                            v_val = float(str(v_raw).replace(' ', '').replace(',', '.'))
                            c_val = float(str(c_raw).replace(' ', '').replace(',', '.'))
                            if v_val > 0:
                                ml_records.append({
                                    'port': p, 'espece': s, 'annee': year, 'mois': month,
                                    'volume_kg': v_val * 1000, 'prix_unitaire_dh': (c_val/v_val)
                                })
                                found_in_col += 1
                        except: continue
                    # print(f"--- TRACE: Found {found_in_col} rows in this column couple.")
                else:
                    pass

    if ml_records:
        ml_df = pd.DataFrame(ml_records)
        ml_df = ml_df[ml_df['port'].str.len() > 1]
        ml_df.to_csv(output_path, index=False)
        # print(f"--- TRACE SUCCESS: {len(ml_df)} total records saved.")
        return ml_df
    
    # print("--- TRACE WARNING: No records found at the end.")
    return None
    
    # print("WARNING: No data records found.")
    return None

def process_onp_report(file_input, output_path=None):
    """
    Traite le rapport ONP (Excel) et retourne un DataFrame nettoyé.
    Priorise la feuille 'Feuil2' qui contient les totaux annuels explicites.
    """
    try:
        xl = pd.ExcelFile(file_input)
        
        # Recherche intelligente de la feuille de données par contenu
        sheet_candidates = []
        for sn in xl.sheet_names:
            try:
                df_test = xl.parse(sn, header=None, nrows=15)
                keywords = ["volume", "ca", "chiffre", "cas", "recette", "espece", "port"]
                score = 0
                for i in range(len(df_test)):
                    row_values = [str(x).lower() for x in df_test.iloc[i].dropna().tolist()]
                    score = max(score, sum(1 for k in keywords if any(k in v for v in row_values)))
                if score >= 2:
                    sheet_candidates.append((sn, score))
            except: continue
            
        if sheet_candidates:
            sheet_candidates.sort(key=lambda x: x[1], reverse=True)
            # Priorité aux feuilles type 'Variation' ou 'RECAP' pour les rapports DR si MG est l'objectif
            prio_sheets = [s for s, score in sheet_candidates if any(x in s.lower() for x in ["recap", "variation"])]
            sheet_name = prio_sheets[0] if prio_sheets else sheet_candidates[0][0]
        else:
            sheet_name = 'RECAP' if 'RECAP' in xl.sheet_names else ('Feuil2' if 'Feuil2' in xl.sheet_names else xl.sheet_names[0])
            
        # print(f"DEBUG: process_onp_report using sheet: '{sheet_name}'")
        df = xl.parse(sheet_name, header=None)
    except Exception as e:
        # print(f"Erreur lecture Excel: {e}")
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
        pass
        # print(f"Erreur extraction mapping: {e}")

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
        # print(f"Extraction terminee via feuille '{sheet_name}'")
        # print(f"Total CA 2024: {final_df['ca_2024_kdh'].sum():,.2f} KDh")
        # print(f"Total Vol 2024: {final_df['vol_2024_t'].sum():,.2f} Tonnes")
        
    return final_df
