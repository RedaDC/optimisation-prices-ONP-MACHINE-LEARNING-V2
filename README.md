# ONP Premium - Optimisation des Prix de Vente (v2.0)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)](https://streamlit.io/)
[![Status](https://img.shields.io/badge/Status-Enterprise%20Ready-success)](#)

> **Intelligence de Marché & Aide à la Décision Stratégique pour l'Office National des Pêches (ONP) - Maroc**

## 📋 Présentation

**ONP Premium** est une plateforme analytique de pointe développée pour moderniser la filière halieutique marocaine. Elle transforme les données massives de vente à la criée en insights actionnables via des modèles de Machine Learning (XGBoost) et des visualisations haute fidélité.

### 🌟 Points Forts
- **Intelligence Artificielle** : Prédiction précise des cours via Gradient Boosting.
- **Visualisation Elite** : Design Glassmorphism et graphiques Plotly interactifs.
- **Souveraineté des Données** : Rapport institutionnel automatisé (Word/PDF).
- **Richesse Visuelle** : Base de données de +290 espèces avec photos réelles.

## ✨ Fonctionnalités Clés

### 📊 Suite Analytique Stratégique
1. **Pilotage National** : Dashboard exécutif avec KPIs temps réel et Market Pulse.
2. **Intelligence de Marché** : Exploration multidimensionnelle (Volume/Prix/Port).
3. **Analyse de Saisonnalité** : Modélisation 4-facteurs (Biologie, Climat, Carburant, Captures).
4. **Interactive Strategy Map** : Monitoring des 22 ports majeurs du Royaume.

### 🧮 Simulateurs Avancés
- **Simulateur de Prix (Halieutis)** : Impact des variations de volume sur les recettes nationales.
- **Simulateur B2B (Marge)** : Calcul du coût de revient total (Taxes ONP 4%, Logistique) pour les mareyeurs.
- **Vue Exécutive** : Synthèse flash et alertes de marché pour la Direction.

## 🚀 Installation & Lancement

```bash
# 1. Installation des dépendances
pip install -r requirements.txt

# 2. Lancement de l'application Premium
streamlit run app_premium.py
```

## 📁 Architecture du Projet

```
📦 ONP Premium/
├── 📄 app_premium.py          # Interface Elite (Entry Point)
├── 📄 utils.py                # Coeur algorithmique & Normalisation
├── 📄 ml_models.py            # Intelligence Artificielle (XGBoost)
├── 📄 financial_analysis.py   # Analyse de rentabilité & Effet Prix/Vol
├── 📄 simulateur_b2b.py       # Logique de marge mareyeur
├── 📄 saisonnalite.py         # Moteur d'analyse saisonnière
├── 📄 onp_assets.py           # Assets institutionnels & Mapping Images
├── 📄 design_system.py        # Framework visuel Premium
└── 📄 donnees_simulation_onp.csv # Data source granulaire
```

## 🎨 Design Institutionnel
L'application respecte la charte graphique de l'**ONP**, utilisant une palette "Économie Bleue" (Navy, Cyan, Emerald) avec une typographie moderne (**Outfit/Inter**) et des composants sur mesure pour une expérience utilisateur premium.

## 🎓 Contexte Académique
Projet réalisé par **Reda Abousaid** dans le cadre du **Master Finance & Data Science**, en partenariat avec l'**Office National des Pêches**.

---
**Développé avec ❤️ pour l'Office National des Pêches (ONP) - Maroc 🇲🇦**
