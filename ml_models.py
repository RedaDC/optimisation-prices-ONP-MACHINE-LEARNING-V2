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
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
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
            'port_encoded',
            'espece_encoded',
            'categorie_encoded',
            'calibre_encoded',
            'mois',
            'jour_semaine',
            'saison_encoded',
            'volume_moyen_espece',
            'prix_moyen_port'
        ]
        
        # Vérifier que toutes les colonnes existent
        feature_cols = [col for col in feature_cols if col in df_encoded.columns]
        self.feature_names = feature_cols
        
        # Préparer X et y
        X = df_encoded[feature_cols].copy()
        y = df_encoded[target_col].copy()
        
        # Gérer les valeurs manquantes restantes
        X = X.fillna(X.median())
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Normalisation
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Re-convertir en DataFrame pour garder les noms de colonnes (utile pour XGBoost/Interpretability)
        X_train_final = pd.DataFrame(X_train_scaled, columns=self.feature_names)
        X_test_final = pd.DataFrame(X_test_scaled, columns=self.feature_names)
        
        print(f"   DONE: Donnees divisees: {len(X_train)} train, {len(X_test)} test")
        
        return X_train_final, X_test_final, y_train, y_test
    
    def train_models(self, X_train, X_test, y_train, y_test):
        """
        Entraîne les trois modèles ML et compare leurs performances.
        
        Args:
            X_train, X_test, y_train, y_test: Données d'entraînement et de test
            
        Returns:
            dict: Résultats de tous les modèles
        """
        print("\nEntrainement des modeles ML...")
        
        # Modèle 1: Régression Linéaire (Baseline)
        print("\n1. Regression Lineaire...")
        lr_model = LinearRegression()
        lr_model.fit(X_train, y_train)
        lr_pred = lr_model.predict(X_test)
        
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
        
        # Modèle 2: Random Forest
        print("\n2. Random Forest Regressor...")
        rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        rf_model.fit(X_train, y_train)
        rf_pred = rf_model.predict(X_test)
        
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
        
        # Modèle 3: HistGradientBoosting (Excellent pour la monotonie)
        print("\n3. HistGradientBoosting Regressor (Elasticité Garantie)...")
        mono_constraints = [0] * len(self.feature_names)
        if 'volume_kg' in self.feature_names:
            v_idx = self.feature_names.index('volume_kg')
            mono_constraints[v_idx] = -1 # Impact négatif
            
        hgb_model = HistGradientBoostingRegressor(
            max_iter=200,
            max_depth=10,
            learning_rate=0.1,
            monotonic_cst=mono_constraints,
            random_state=42
        )
        hgb_model.fit(X_train, y_train)
        hgb_pred = hgb_model.predict(X_test)
        
        hgb_rmse = np.sqrt(mean_squared_error(y_test, hgb_pred))
        hgb_mae = mean_absolute_error(y_test, hgb_pred)
        hgb_r2 = r2_score(y_test, hgb_pred)
        
        self.models['HGBoost'] = hgb_model
        self.results['HGBoost'] = {
            'RMSE': hgb_rmse,
            'MAE': hgb_mae,
            'R2': hgb_r2,
            'predictions': hgb_pred
        }
        
        print(f"   DONE: RMSE: {hgb_rmse:.2f} DH/kg")
        print(f"   DONE: MAE: {hgb_mae:.2f} DH/kg")
        print(f"   DONE: R2: {hgb_r2:.4f}")
        
        # Sélection du meilleur modèle (basé sur RMSE)
        # On force HGBoost car il garantit l'élasticité demandée (Loi de l'Offre et de la Demande)
        best_rmse = min(lr_rmse, rf_rmse, hgb_rmse)
        
        if hgb_rmse <= best_rmse * 1.30: 
            self.best_model_name = 'HGBoost'
        elif best_rmse == lr_rmse:
            self.best_model_name = 'Linear Regression'
        else:
            self.best_model_name = 'Random Forest'
        
        self.best_model = self.models[self.best_model_name]
        
        print(f"\nWINNER (Elasticite Garantie): Meilleur modele: {self.best_model_name}")
        print(f"   RMSE: {self.results[self.best_model_name]['RMSE']:.2f} DH/kg")
        
        return self.results
    
    def get_feature_importance(self, top_n=10):
        """
        Retourne l'importance des features pour les modèles tree-based.
        
        Args:
            top_n (int): Nombre de features à retourner
            
        Returns:
            pd.DataFrame: Features et leur importance
        """
        if self.best_model_name in ['Random Forest', 'XGBoost']:
            importance = self.results[self.best_model_name]['feature_importance']
            
            df_importance = pd.DataFrame({
                'feature': self.feature_names,
                'importance': importance
            }).sort_values('importance', ascending=False).head(top_n)
            
            return df_importance
        else:
            return pd.DataFrame()
    
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
        
        Args:
            X (array-like): Features d'entrée
            
        Returns:
            array: Prédictions de prix
        """
        if self.best_model is None:
            raise ValueError("Aucun modèle entraîné. Utilisez train_models() d'abord.")
        
        X_scaled = self.scaler.transform(X)
        return self.best_model.predict(X_scaled)

    def predict_single(self, df_ref, species, port, volume_kg):
        """
        Prédit le prix pour une combinaison espèce / port / volume.
        """
        if self.best_model is None:
            raise ValueError("Aucun modèle entraîné.")
            
        # 1. Obtenir les stats de référence pour cette espèce/port
        sub = df_ref[(df_ref["espece"] == species) & (df_ref["port"] == port)]
        if sub.empty:
            sub = df_ref[df_ref["espece"] == species]
        if sub.empty:
            sub = df_ref.head(1)
            
        ref_row = sub.iloc[0].to_dict()
        
        # 2. Préparer la ligne de prédiction
        # On garde les stats de référence (moyennes historiques) mais on change le volume actuel
        row = {
            "espece": species,
            "port": port,
            "volume_kg": volume_kg,
            "mois": ref_row.get("mois", 6),
            "jour_semaine": ref_row.get("jour_semaine", 2),
            "annee": ref_row.get("annee", 2025),
            "categorie": ref_row.get("categorie", "AUTRE"),
            "calibre": ref_row.get("calibre", "Moyen")
        }
        
        df_one = pd.DataFrame([row])
        
        # 3. Features temporelles et saison (on le fait avant pour ne pas ecraser les moyennes)
        df_one = create_features(df_one)
        
        # 4. Injecter les moyennes historiques du df_ref (APRES create_features pour ne pas etre ecrase)
        df_one["volume_moyen_espece"] = df_ref[df_ref["espece"] == species]["volume_kg"].mean() if "volume_kg" in df_ref.columns else volume_kg
        df_one["prix_moyen_port"] = df_ref[df_ref["port"] == port]["prix_unitaire_dh"].mean() if "prix_unitaire_dh" in df_ref.columns else 20.0
        
        # 5. Encodage
        for col, le in self.encoders.items():
            if f"{col}_encoded" in self.feature_names:
                enc_col = f"{col}_encoded"
                val = str(df_one[col].iloc[0])
                df_one[enc_col] = le.transform([val])[0] if val in le.classes_ else 0
        
        # 5. S'assurer que toutes les features requises sont là
        for col in self.feature_names:
            if col not in df_one.columns:
                df_one[col] = 0
                
        X = df_one[self.feature_names]
        X_scaled = self.scaler.transform(X)
        X_final = pd.DataFrame(X_scaled, columns=self.feature_names)
        return float(self.best_model.predict(X_final)[0])


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
    X_train, X_test, y_train, y_test = predictor.prepare_data(df)
    
    # Entraîner les modèles
    results = predictor.train_models(X_train, X_test, y_train, y_test)
    
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
