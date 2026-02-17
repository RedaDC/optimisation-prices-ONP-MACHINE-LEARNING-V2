# Application ONP - Guide de Démarrage Rapide

## Fichiers Créés

Tous les fichiers ont été créés avec succès :

- `app.py` - Application Streamlit principale (5 pages)
- `utils.py` - Fonctions utilitaires
- `ml_models.py` - Modèles ML (Linear Regression, Random Forest, XGBoost)
- `eda_analysis.py` - Analyses exploratoires
- `financial_analysis.py` - Analyses financières
- `README.md` - Documentation complète
- `test_app.py` - Script de test
- `requirements.txt` - Dépendances

## Installation et Lancement

### Étape 1: Installer les dépendances ML

```bash
pip install scikit-learn xgboost joblib seaborn matplotlib scipy openpyxl
```

### Étape 2: Lancer l'application

L'application est normalement lancée sur le port 8501.

**Ouvrez votre navigateur à l'adresse :**
```
http://localhost:8501
```

Si vous devez la relancer :
```bash
py -m streamlit run app.py --server.port 8501
```

## Pages de l'Application

1. **Accueil** - Vue d'ensemble avec KPIs
2. **Analyse des Prix** - Graphiques interactifs
3. **Analyse Financière** - Recettes et rentabilité
4. **Modèle ML** - Entraînement et comparaison
5. **Simulation** - Impact et recommandations

## Fonctionnalités

### Filtres (Menu Latéral)
- Période d'analyse
- Port (Casablanca, Agadir, Tanger, etc.)
- Espèce (Sardine, Poulpe, Crevette, etc.)

### Analyses Disponibles
- Distribution des prix par espèce
- Prix par port
- Relation volume-prix
- Saisonnalité
- Tendances temporelles
- Recettes par port
- Top espèces rentables
- Évolution des recettes

### Machine Learning
- 3 modèles comparés automatiquement
- Sélection du meilleur modèle
- Feature importance
- Métriques RMSE, MAE, R²

### Simulation
- Impact d'un changement de volume
- Calcul automatique du nouveau prix
- Impact sur les recettes
- Recommandations

## Note Importante

Si vous voyez l'erreur `ModuleNotFoundError: No module named 'sklearn'`, exécutez :

```bash
pip install scikit-learn xgboost
```

Puis rechargez la page dans votre navigateur (F5).

## Documentation

Consultez `README.md` pour la documentation complète et `walkthrough.md` pour les détails techniques.

---

Développé pour l'Office National des Pêches (ONP) - Maroc
