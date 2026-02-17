# ONP - Optimisation des Prix de Vente des Produits de la Pêche

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-Academic-green.svg)](LICENSE)

> **Application d'aide à la décision basée sur le Machine Learning pour l'Office National des Pêches (ONP) - Maroc**

![ONP Dashboard](https://img.shields.io/badge/Status-Production%20Ready-success)

## 📋 Description

Application web interactive développée dans le cadre d'un **Projet de Fin d'Études (PFE)** en Master Finance & Data Science. Cette plateforme utilise des techniques avancées de Machine Learning pour analyser les données historiques de vente à la criée et optimiser les prix de vente des produits de la pêche.

### Objectifs

- ✅ Analyser les facteurs influençant les prix (espèce, port, volume, saison)
- ✅ Prédire le prix de vente optimal grâce à des modèles ML
- ✅ Simuler l'impact des décisions sur les recettes financières
- ✅ Fournir un dashboard professionnel pour les décideurs de l'ONP

## ✨ Fonctionnalités

### 📱 Interface Streamlit (5 Pages)

1. **Accueil** - Vue d'ensemble avec KPIs principaux
2. **Analyse des Prix** - Visualisations exploratoires interactives
3. **Analyse Financière** - Recettes, rentabilité, évolution
4. **Modèle ML** - Entraînement et comparaison de 3 modèles
5. **Simulation** - Impact et recommandations

### 🤖 Machine Learning

- **3 Modèles implémentés** :
  - Régression Linéaire (baseline)
  - Random Forest (ensemble)
  - XGBoost (gradient boosting)
- **Sélection automatique** du meilleur modèle
- **Feature importance** pour interprétabilité
- **Métriques** : RMSE, MAE, R²

### 📊 Analyses

- Distribution des prix par espèce
- Prix par port et saisonnalité
- Relation volume-prix
- Recettes par port et espèce
- Top espèces rentables
- Évolution temporelle

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes

1. **Cloner le repository**

```bash
git clone https://github.com/VOTRE_USERNAME/onp-ml-pricing.git
cd onp-ml-pricing
```

2. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

3. **Lancer l'application**

```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à `http://localhost:8501`

## 📁 Structure du Projet

```
📦 ONP ML Pricing/
├── 📄 app.py                      # Application Streamlit principale
├── 📄 utils.py                    # Fonctions utilitaires
├── 📄 ml_models.py                # Modèles ML
├── 📄 eda_analysis.py             # Analyses exploratoires
├── 📄 financial_analysis.py       # Analyses financières
├── 📄 donnees_simulation_onp.csv  # Données historiques
├── 📄 requirements.txt            # Dépendances Python
├── 📄 README.md                   # Ce fichier
├── 📄 .gitignore                  # Fichiers à ignorer
├── 📁 models/                     # Modèles ML sauvegardés
└── 📁 scripts/                    # Scripts utilitaires
```

## 🎨 Design

- **Couleurs** : Dégradé bleu → cyan → vert (couleurs ONP)
- **Effets** : Glassmorphism, animations, hover effects
- **Typographie** : Poppins (Google Fonts)
- **Framework** : Streamlit + Plotly

## 🔧 Technologies

| Catégorie | Technologies |
|-----------|-------------|
| **Frontend** | Streamlit, Plotly |
| **Data Science** | Pandas, NumPy, SciPy |
| **Machine Learning** | Scikit-learn, XGBoost |
| **Visualisation** | Plotly, Matplotlib, Seaborn |

## 📊 Résultats Attendus

### Performances ML (exemple)

| Modèle | RMSE (DH/kg) | MAE (DH/kg) | R² |
|--------|--------------|-------------|-----|
| Linear Regression | ~15-20 | ~10-15 | 0.75-0.80 |
| Random Forest | ~10-15 | ~7-10 | 0.85-0.90 |
| **XGBoost** ⭐ | **~8-12** | **~6-8** | **0.90-0.95** |

## 🎓 Contexte Académique

**Projet de Fin d'Études (PFE)**  
Master Finance & Data Science  
Office National des Pêches (ONP) - Maroc

### Compétences démontrées

- ✅ Data Science & Machine Learning
- ✅ Développement web (Streamlit)
- ✅ Analyse financière
- ✅ Visualisation de données
- ✅ Communication technique

## 📸 Screenshots

*Ajoutez des captures d'écran de votre application ici*

## 🤝 Contribution

Ce projet est développé dans le cadre d'un PFE académique. Les contributions sont les bienvenues pour améliorer l'application.

## 📄 Licence

Projet académique - Master Finance & Data Science

## 👤 Auteur

**Votre Nom**  
Master Finance & Data Science  
📧 Email: votre.email@example.com  
🔗 LinkedIn: [Votre Profil](https://linkedin.com/in/votre-profil)

## 🙏 Remerciements

- Office National des Pêches (ONP) - Maroc
- Encadrants académiques
- Équipe pédagogique Master Finance & Data Science

---

**Développé avec ❤️ pour l'Office National des Pêches (ONP) - Maroc 🇲🇦**
