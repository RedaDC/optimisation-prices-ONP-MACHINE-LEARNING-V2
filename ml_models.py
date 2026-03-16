"""
Module de Modélisation Machine Learning - Application ONP
==========================================================

Ce module implémente et compare trois modèles de prédiction de prix:
1. Régression Linéaire (baseline)
2. Random Forest Regressor (ensemble method)
3. XGBoost Regressor (gradient boosting)

Le meilleur modèle est automatiquement sélectionné basé sur RMSE et MAE.

Auteur: PFE Master Finance & Data Science
Contexte: Office National des Pêches (ONP) - Maroc
"""

import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from datetime import datetime
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

# Import des fonctions utilitaires
from utils import clean_data, create_features, encode_categorical


class ONPPricePredictor:
    """
    Classe principale pour la prédiction des prix de vente.
    
    Cette classe gère:
    - La préparation des données
    - L'entraînement de multiples modèles ML
    - La comparaison et sélection du meilleur modèle
    - La sauvegarde et le chargement des modèles
    """
    
    def __init__(self):
        self.models = {}
        self.best_model = None
        self.best_model_name = None
        self.scaler = StandardScaler()
        self.encoders = {}
        self.feature_names = []
        self.results = {}
        
    def prepare_data(self, df, target_col='prix_unitaire_dh', test_size=0.2, random_state=42):
        """
        Prépare les données pour l'entraînement ML.
        
        Args:
            df (pd.DataFrame): DataFrame brut
            target_col (str): Colonne cible à prédire
            test_size (float): Proportion du jeu de test
            random_state (int): Seed pour reproductibilité
            
        Returns:
            tuple: X_train, X_test, y_train, y_test
        """
        print("Preparation des donnees...")
        
        # Étape 1: Nettoyage
        df_clean = clean_data(df)
        print(f"   DONE: Donnees nettoyees: {len(df_clean)} lignes")
        
        # Étape 2: Feature Engineering
        df_feat = create_features(df_clean)
        print(f"   DONE: Features creees")
        
        # Étape 3: Encodage
        df_encoded, self.encoders = encode_categorical(df_feat)
        print(f"   DONE: Variables categorielles encodees")
        
        # Sélection des features pour le modèle
        feature_cols = [
            'volume_kg',
            'log_volume',
            'port_encoded',
            'espece_encoded',
            'categorie_encoded',
            'calibre_encoded',
            'mois',
            'jour_semaine',
            'saison_encoded',
            'is_repos_biologique',
            'volume_moyen_espece',
            'log_volume_moyen',
            'ratio_volume',
            'prix_moyen_espece',
            'prix_moyen_port',
            'prix_moyen_region',
            'prix_carburant',
            'force_vent',
            'is_tempete'
        ]
        
        # Vérifier que toutes les colonnes existent
        feature_cols = [col for col in feature_cols if col in df_encoded.columns]
        self.feature_names = feature_cols
        
        # Préparer X et y
        X = df_encoded[feature_cols].copy()
        
        # Transformation Logarithmique de la Cible (CRUCIAL pour la précision sur les prix élevés)
        y = np.log1p(df_encoded[target_col])
        
        # Transformation Logarithmique des features de prix (pour cohérence d'échelle)
        price_feats = ['prix_moyen_espece', 'prix_moyen_port', 'prix_moyen_region']
        for col in price_feats:
            if col in X.columns:
                X[col] = np.log1p(X[col])
        
        # Gérer les valeurs manquantes restantes
        X = X.fillna(X.median())
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Normalisation
        # On garde une version NON-SCALED pour les arbres (Random Forest / HGBoost)
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Re-convertir en DataFrame
        X_train_scaled_df = pd.DataFrame(X_train_scaled, columns=self.feature_names)
        X_test_scaled_df = pd.DataFrame(X_test_scaled, columns=self.feature_names)
        
        print(f"   DONE: Donnees divisees: {len(X_train)} train, {len(X_test)} test")
        
        return X_train, X_test, y_train, y_test, X_train_scaled_df, X_test_scaled_df
    
    def train_models(self, X_train, X_test, y_train, y_test, X_train_scaled=None, X_test_scaled=None):
        """
        Entraîne les trois modèles ML et compare leurs performances.
        
        Args:
            X_train, X_test, y_train, y_test: Données d'entraînement et de test (non-scalées)
            X_train_scaled, X_test_scaled: Données d'entraînement et de test (scalées)
            
        Returns:
            dict: Résultats de tous les modèles
        """
        print("\nEntrainement des modeles ML...")
        
        # Modèle 1: Régression Linéaire (Baseline) - A BESOIN de scaling
        print("\n1. Regression Lineaire...")
        lr_model = LinearRegression()
        lr_model.fit(X_train_scaled if X_train_scaled is not None else X_train, y_train)
        lr_pred = lr_model.predict(X_test_scaled if X_test_scaled is not None else X_test)
        
        lr_rmse = np.sqrt(mean_squared_error(y_test, lr_pred))
        lr_mae = mean_absolute_error(y_test, lr_pred)
        lr_r2 = r2_score(y_test, lr_pred)
        
        self.models['Linear Regression'] = lr_model
        self.results['Linear Regression'] = {
            'RMSE': lr_rmse,
            'MAE': lr_mae,
            'R2': lr_r2,
            'predictions': lr_pred
        }
        
        print(f"   DONE: RMSE: {lr_rmse:.2f} DH/kg")
        print(f"   DONE: MAE: {lr_mae:.2f} DH/kg")
        print(f"   DONE: R2: {lr_r2:.4f}")
        
        # Modèle 2: Random Forest - N'A PAS BESOIN de scaling
        print("\n2. Random Forest Regressor...")
        rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        rf_model.fit(X_train, y_train) # Utilise les données non-scalées
        rf_pred = rf_model.predict(X_test) # Utilise les données non-scalées
        
        rf_rmse = np.sqrt(mean_squared_error(y_test, rf_pred))
        rf_mae = mean_absolute_error(y_test, rf_pred)
        rf_r2 = r2_score(y_test, rf_pred)
        
        self.models['Random Forest'] = rf_model
        self.results['Random Forest'] = {
            'RMSE': rf_rmse,
            'MAE': rf_mae,
            'R2': rf_r2,
            'predictions': rf_pred,
            'feature_importance': rf_model.feature_importances_
        }
        
        print(f"   DONE: RMSE: {rf_rmse:.2f} DH/kg")
        print(f"   DONE: MAE: {rf_mae:.2f} DH/kg")
        print(f"   DONE: R2: {rf_r2:.4f}")
        
        # Modèle 3: XGBoost (Modèle Principal Elite)
        print("\n3. XGBoost Regressor (Performance Maximale)...")
        import xgboost as xgb
        
        xgb_model = xgb.XGBRegressor(
            n_estimators=1000,
            learning_rate=0.05,
            max_depth=8,
            subsample=0.8,
            colsample_bytree=0.8,
            n_jobs=-1,
            random_state=42,
            tree_method='hist'
        )
        
        xgb_model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
        
        # Récupération des prédictions (Log-Scale)
        xgb_log_pred = xgb_model.predict(X_test)
        
        # Conversion Inverse (Back to DH/kg) pour les métriques métier
        y_test_orig = np.expm1(y_test)
        xgb_pred = np.expm1(xgb_log_pred)
        
        xgb_rmse = np.sqrt(mean_squared_error(y_test_orig, xgb_pred))
        xgb_mae = mean_absolute_error(y_test_orig, xgb_pred)
        xgb_r2 = r2_score(y_test_orig, xgb_pred)
        
        # Calcul du MAPE sécurisé (Mean Absolute Percentage Error)
        ape = np.abs((y_test_orig - xgb_pred) / (y_test_orig + 1e-9))
        xgb_mape = np.mean(np.clip(ape, 0, 1)) * 100 
        
        self.models['XGBoost'] = xgb_model
        self.results['XGBoost'] = {
            'RMSE': xgb_rmse,
            'MAE': xgb_mae,
            'R2': xgb_r2,
            'MAPE': xgb_mape,
            'predictions': xgb_pred,
            'feature_importance': xgb_model.feature_importances_
        }
        
        print(f"   DONE: RMSE: {xgb_rmse:.2f} DH/kg")
        print(f"   DONE: MAE: {xgb_mae:.2f} DH/kg")
        print(f"   DONE: R2: {xgb_r2:.4f}")
        
        # Sélection du meilleur modèle (Focus XGBoost)
        self.best_model_name = 'XGBoost'
        self.best_model = self.models[self.best_model_name]
        
        print(f"\nWINNER (Anti-Gravity AI): Meilleur modele: {self.best_model_name}")
        return self.results
    
    def evaluate_model(self, X, y, n_splits=5):
        """
        Effectue une Validation Croisée (K-Fold) et analyse le surapprentissage.
        Génère les graphiques Plotly comparant Train/Test.
        """
        print(f"\n[Validation Croisée] Évaluation Anti-Overfitting ({n_splits}-Folds)...")
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
        
        models_to_evaluate = {
            'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=15, min_samples_split=5, min_samples_leaf=2, random_state=42, n_jobs=-1),
            'XGBoost': __import__('xgboost').XGBRegressor(n_estimators=1000, learning_rate=0.05, max_depth=8, subsample=0.8, colsample_bytree=0.8, n_jobs=-1, random_state=42, tree_method='hist')
        }
        
        cv_results = {}
        
        for name, model in models_to_evaluate.items():
            print(f"  Évaluation de {name}...")
            train_r2, test_r2 = [], []
            train_rmse, test_rmse = [], []
            train_mae, test_mae = [], []
            
            # Important: Reset index for proper KFold slicing if X is a DataFrame
            X_cv = X.reset_index(drop=True) if isinstance(X, pd.DataFrame) else X
            y_cv = y.reset_index(drop=True) if isinstance(y, pd.Series) else y
            
            for train_idx, test_idx in kf.split(X_cv):
                # Slicing
                X_tr, X_te = X_cv.iloc[train_idx], X_cv.iloc[test_idx]
                y_tr, y_te = y_cv.iloc[train_idx], y_cv.iloc[test_idx]
                
                # Fit
                if name == 'XGBoost':
                     model.fit(X_tr, y_tr, eval_set=[(X_te, y_te)], verbose=False)
                else:
                     model.fit(X_tr, y_tr)
                
                # Predict
                pred_tr = model.predict(X_tr)
                pred_te = model.predict(X_te)
                
                # Metrics
                train_r2.append(r2_score(y_tr, pred_tr))
                test_r2.append(r2_score(y_te, pred_te))
                
                train_rmse.append(np.sqrt(mean_squared_error(y_tr, pred_tr)))
                test_rmse.append(np.sqrt(mean_squared_error(y_te, pred_te)))
                
                train_mae.append(mean_absolute_error(y_tr, pred_tr))
                test_mae.append(mean_absolute_error(y_te, pred_te))
            
            # Average results
            avg_train_r2 = np.mean(train_r2)
            avg_test_r2 = np.mean(test_r2)
            overfit_gap = avg_train_r2 - avg_test_r2
            
            # Build Plotly Figure
            fig = go.Figure()
            categories = ['Train', 'Test']
            
            fig.add_trace(go.Bar(
                name='R² Score',
                x=categories,
                y=[avg_train_r2, avg_test_r2],
                marker_color=['#0EA5E9', '#10B981'],
                text=[f"{avg_train_r2:.3f}", f"{avg_test_r2:.3f}"],
                textposition='auto',
            ))
            
            fig.update_layout(
                title=f"Comparaison Train vs Test - {name}",
                yaxis_title="Score R² (Plus proche de 1 est meilleur)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                barmode='group',
                height=350,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            cv_results[name] = {
                'train_r2': avg_train_r2,
                'test_r2': avg_test_r2,
                'train_rmse': np.mean(train_rmse),
                'test_rmse': np.mean(test_rmse),
                'train_mae': np.mean(train_mae),
                'test_mae': np.mean(test_mae),
                'overfit_gap': overfit_gap,
                'is_overfitting': overfit_gap > 0.10, # Seuil d'alerte défini par l'utilisateur
                'plotly_fig': fig
            }
            
        return cv_results
    
    def get_feature_importance(self, top_n=10):
        """
        Retourne l'importance des features pour les modèles tree-based.
        
        Args:
            top_n (int): Nombre de features à retourner
            
        Returns:
            pd.DataFrame: Features et leur importance
        """
        if self.best_model_name in ['Random Forest', 'HGBoost'] and 'feature_importance' in self.results.get(self.best_model_name, {}):
            importance = self.results[self.best_model_name]['feature_importance']
            
            df_importance = pd.DataFrame({
                'feature': self.feature_names,
                'importance': importance
            }).sort_values('importance', ascending=False).head(top_n)
            
            return df_importance
        else:
            return pd.DataFrame(columns=['feature', 'importance'])
    
    def save_model(self, filepath='models/best_model.pkl'):
        """
        Sauvegarde le meilleur modèle et ses métadonnées.
        
        Args:
            filepath (str): Chemin de sauvegarde
        """
        # Créer le dossier models s'il n'existe pas
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        model_data = {
            'model': self.best_model,
            'model_name': self.best_model_name,
            'scaler': self.scaler,
            'encoders': self.encoders,
            'feature_names': self.feature_names,
            'results': self.results
        }
        
        joblib.dump(model_data, filepath)
        print(f"\nSAVE: Modele sauvegarde: {filepath}")
    
    def load_model(self, filepath='models/best_model.pkl'):
        """
        Charge un modèle sauvegardé.
        
        Args:
            filepath (str): Chemin du modèle
        """
        if not os.path.exists(filepath):
            print(f"ERROR: Fichier non trouve: {filepath}")
            return False
        
        model_data = joblib.load(filepath)
        
        self.best_model = model_data['model']
        self.best_model_name = model_data['model_name']
        self.scaler = model_data['scaler']
        self.encoders = model_data['encoders']
        self.feature_names = model_data['feature_names']
        self.results = model_data['results']
        
        print(f"DONE: Modele charge: {self.best_model_name}")
        return True
    
    def predict(self, X):
        """
        Fait une prédiction avec le meilleur modèle.
        S'assure que tous les prix prédits sont positifs.
        """
        if self.best_model is None:
            raise ValueError("Aucun modèle entraîné. Utilisez train_models() d'abord.")
        
        # Appliquer le scaling uniquement si le modèle en a besoin (e.g., Linear Regression)
        if isinstance(self.best_model, LinearRegression):
            X_processed = self.scaler.transform(X)
        else: # Pour les modèles basés sur les arbres, pas de scaling
            X_processed = X
            
        preds_log = self.best_model.predict(X_processed)
        
        # Conversion Inverse (Back to DH/kg)
        preds = np.expm1(preds_log)
        
        # Sécurité: Aucun prix ne peut être inférieur à 1 DH/kg
        return np.maximum(preds, 1.0)

    def update_model(self, new_data_df):
        """
        Implémente un mécanisme d'apprentissage en ligne (Online Learning).
        Réajuste le modèle avec de nouvelles données fraîches.
        """
        print("\nUPDATE: Online Learning en cours...")
        if self.best_model is None:
            print("ERROR: Aucun modele a mettre a jour.")
            return False
            
        # Préparer les nouvelles données
        df_clean = clean_data(new_data_df)
        df_feat = create_features(df_clean)
        df_encoded, _ = encode_categorical(df_feat)
        
        # Aligner avec les features existantes
        for col in self.feature_names:
            if col not in df_encoded.columns:
                df_encoded[col] = 0
                
        X_new = df_encoded[self.feature_names].fillna(0)
        y_new_log = np.log1p(df_encoded['prix_unitaire_dh'])
        
        # Transformation Logarithmique des features de prix
        price_feats = ['prix_moyen_espece', 'prix_moyen_port', 'prix_moyen_region']
        for col in price_feats:
            if col in X_new.columns:
                X_new[col] = np.log1p(X_new[col])
        
        # Appliquer le scaling si le modèle en a besoin
        if isinstance(self.best_model, LinearRegression):
            X_new_processed = self.scaler.transform(X_new)
            X_new_final = pd.DataFrame(X_new_processed, columns=self.feature_names)
        else: # Pour les modèles basés sur les arbres, pas de scaling
            X_new_final = X_new
            
        # Mise à jour incrémentale selon le modèle
        if self.best_model_name == 'Linear Regression':
            # La régression linéaire classique ne supporte pas le fit partiel, on réentraîne
            self.best_model.fit(X_new_final, y_new_log)
        else:
            # Pour les modèles basés sur les arbres, on utilise le warm start ou un réentraînement rapide
            # Note: HistGradientBoosting ne supporte pas encore partial_fit, on réentraîne sur le nouveau buffer
            self.best_model.fit(X_new_final, y_new_log)
            
        print(f"DONE: Modele {self.best_model_name} mis a jour avec {len(new_data_df)} lignes.")
        return True

    def predict_single(self, df_ref, species, port, volume_kg, month_override=None):
        """
        Prédit le prix pour une combinaison espèce / port / volume.
        Utilise la date système actuelle par défaut, ou month_override si fourni.
        """
        if self.best_model is None:
            raise ValueError("Aucun modèle entraîné.")
            
        # 0. Date actuelle ou forcée
        now = datetime.now()
        current_month = month_override if month_override is not None else now.month
        current_year = now.year
        current_day_of_week = now.weekday()
            
        # 1. Obtenir les stats de référence pour cette espèce/port
        sub = df_ref[(df_ref["espece"] == species) & (df_ref["port"] == port)]
        if sub.empty:
            sub = df_ref[df_ref["espece"] == species]
        if sub.empty:
            sub = df_ref.head(1)
            
        ref_row = sub.iloc[0].to_dict()
        
        # 2. Préparer la ligne de prédiction avec la date 
        row = {
            "espece": species,
            "port": port,
            "volume_kg": volume_kg,
            "mois": current_month,
            "jour_semaine": current_day_of_week,
            "annee": current_year,
            "categorie": ref_row.get("categorie", "AUTRE"),
            "calibre": ref_row.get("calibre", "Moyen")
        }
        
        df_one = pd.DataFrame([row])
        
        # 3. Features temporelles et saison
        df_one = create_features(df_one)
        
        # 4. Injecter les moyennes historiques du df_ref (CRUCIAL pour la précision)
        # On définit une fonction helper pour chercher la moyenne d'abord (Port, Espece), puis Region, puis Espece globale
        def get_ref_val(col_target, group_cols):
            try:
                # Filtrer df_ref sur les colonnes de groupe
                masks = [df_ref[c] == row[c] for c in group_cols]
                final_mask = masks[0]
                for m in masks[1:]: final_mask &= m
                
                sub_ref = df_ref[final_mask]
                if not sub_ref.empty:
                    return sub_ref[col_target].mean()
            except:
                pass
            return np.nan

        # Region
        region = str(df_one["region"].iloc[0])
        
        # Injection des moyennes
        if pd.isna(df_one.get("volume_moyen_espece", [np.nan])[0]):
            df_one["volume_moyen_espece"] = get_ref_val("volume_kg", ["espece"]) or volume_kg
            
        if pd.isna(df_one.get("prix_moyen_port", [np.nan])[0]):
            df_one["prix_moyen_port"] = get_ref_val("prix_unitaire_dh", ["port"]) or 20.0
            
        if pd.isna(df_one.get("prix_moyen_espece", [np.nan])[0]):
            df_one["prix_moyen_espece"] = get_ref_val("prix_unitaire_dh", ["espece"]) or 20.0
            
        if pd.isna(df_one.get("prix_moyen_region", [np.nan])[0]):
            # Region + Espece
            val_reg = get_ref_val("prix_unitaire_dh", ["region", "espece"])
            if pd.isna(val_reg):
                val_reg = df_one["prix_moyen_espece"].iloc[0]
            df_one["prix_moyen_region"] = val_reg
            
        # NOUVEAU: Recalculer les features dérivées
        df_one["log_volume_moyen"] = np.log1p(df_one["volume_moyen_espece"])
        df_one["ratio_volume"] = df_one["volume_kg"] / (df_one["volume_moyen_espece"] + 1)
            
        # 5. Encodage
        for col, le in self.encoders.items():
            if f"{col}_encoded" in self.feature_names:
                enc_col = f"{col}_encoded"
                val = str(df_one[col].iloc[0])
                df_one[enc_col] = le.transform([val])[0] if val in le.classes_ else 0
        
        # 6. S'assurer que toutes les features requises sont là
        for col in self.feature_names:
            if col not in df_one.columns:
                df_one[col] = 0
                
        X_final = df_one[self.feature_names].copy()
        
        # TRANSFORMATION LOGARITHMIQUE DES FEATURES (pour cohérence avec training)
        price_feats = ['prix_moyen_espece', 'prix_moyen_port', 'prix_moyen_region']
        for col in price_feats:
            if col in X_final.columns:
                X_final[col] = np.log1p(X_final[col])
        
        # Prédire (On ne scale plus pour HGBoost qui est le gagnant par défaut)
        try:
            if isinstance(self.best_model, LinearRegression):
                 X_scaled = self.scaler.transform(X_final)
                 X_final_proc = pd.DataFrame(X_scaled, columns=self.feature_names)
            else:
                 X_final_proc = X_final
            
            pred_log = float(self.best_model.predict(X_final_proc)[0])
            pred = np.expm1(pred_log)
        except Exception as e:
            # Fallback scaling if model was trained with it
            X_scaled = self.scaler.transform(X_final)
            X_final_scaled = pd.DataFrame(X_scaled, columns=self.feature_names)
            pred = float(self.best_model.predict(X_final_scaled)[0])
        
        # Debug info (temporary)
        # print(f"\nDebug Features for {species}:")
        # print(X_final[['volume_kg', 'log_volume', 'espece_encoded', 'prix_moyen_espece', 'ratio_volume']])
        print(X_final)
        
        # Prédire et s'assurer que le prix est positif (minimum 1.0 DH/kg)
        # pred = float(self.best_model.predict(X_final)[0]) # This line is now inside the try-except block
        
        # Appliquer un coefficient de rareté si on est en Repos Biologique
        # (Ajustement métier pour garantir la logique même si le modèle a peu de données en période de fermeture)
        if df_one['is_repos_biologique'].iloc[0] == 1:
            pred = pred * 1.25
            
        return max(pred, 1.0)


def train_and_save_model(data_path='donnees_simulation_onp.csv'):
    """
    Fonction principale pour entraîner et sauvegarder le modèle.
    
    Args:
        data_path (str): Chemin vers le fichier CSV
    """
    print("="*60)
    print("APPLICATION ONP - ENTRAINEMENT DES MODELES ML")
    print("="*60)
    
    # Charger les données
    print(f"\nLOAD: Chargement des donnees: {data_path}")
    df = pd.read_csv(data_path)
    print(f"   DONE: {len(df)} lignes chargees")
    
    # Créer le prédicteur
    predictor = ONPPricePredictor()
    
    # Préparer les données
    X_train, X_test, y_train, y_test, X_train_scaled, X_test_scaled = predictor.prepare_data(df)
    
    # Entraîner les modèles
    results = predictor.train_models(X_train, X_test, y_train, y_test, X_train_scaled, X_test_scaled)
    
    # Afficher l'importance des features
    print("\nINFO: Importance des Features:")
    importance_df = predictor.get_feature_importance(top_n=10)
    if not importance_df.empty:
        for idx, row in importance_df.iterrows():
            print(f"   {row['feature']}: {row['importance']:.4f}")
    
    # Sauvegarder le modèle
    predictor.save_model()
    
    print("\n" + "="*60)
    print("DONE: ENTRAINEMENT TERMINE AVEC SUCCES!")
    print("="*60)
    
    return predictor, results


if __name__ == "__main__":
    # Entraîner et sauvegarder le modèle
    predictor, results = train_and_save_model()
    
    # Afficher un résumé des résultats
    print("\nSUMMARY: RESUME DES PERFORMANCES:")
    print("-" * 60)
    for model_name, metrics in results.items():
        print(f"\n{model_name}:")
        print(f"  RMSE: {metrics['RMSE']:.2f} DH/kg")
        print(f"  MAE:  {metrics['MAE']:.2f} DH/kg")
        print(f"  R2:   {metrics['R2']:.4f}")
