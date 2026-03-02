# Rapport de Fonctionnalité - Application ONP Premium

Ce document détaille les fonctionnalités et l'architecture technique de la plateforme d'optimisation et de prédiction des prix pour l'Office National des Pêches (ONP).

## 1. Vue d'Ensemble
L'application est une plateforme d'aide à la décision basée sur l'Intelligence Artificielle. Elle permet de suivre l'activité halieutique nationale en temps réel et de prédire les cours du poisson en fonction de variables exogènes (météo, carburant) et endogènes (volumes, périodes de repos).

## 2. Fonctionnalités Clés

### A. Pilotage National (Nouveau)
- **Synthèse Météo du Royaume** : Suivi en temps réel des conditions de mer (vent, houle) sur les ports stratégiques de Tanger, Casablanca, Agadir et Dakhla.
- **Index Carburant Régional** : Gestion différenciée des prix du gasoil entre le Nord/Centre et les provinces du Sud (application automatique des exonérations fiscales).

### B. Moteur Prédictif (Machine Learning)
- **Modélisation Avancée** : Utilisation du modèle HistGradientBoosting pour garantir le respect de la loi de l'offre et de la demande (élasticité prix/volume).
- **Considérations Métier** : Intégration des périodes de repos biologique et de la météo marine comme facteurs d'influence sur les cours.
- **Apprentissage Continu** : Capacité du modèle à se réajuster avec de nouvelles données d'extraction.

### C. Tableaux de Bord et Analytics
- **Elite Command Center** : KPIs dynamiques (Recette, Prix Moyen, Volumes) filtrables par délégation régionale (DR), port et espèce.
- **Analyse Comparative** : Module dédié à la comparaison des performances entre 2024 et 2025.
- **Cartographie Stratégique** : Visualisation géographique du maillage territorial de l'ONP.

## 3. Architecture Technique
- **Interface** : Streamlit avec design system premium personnalisé (LuxIcons, PremiumComponents).
- **Traitement de Données** : Pipeline de Feature Engineering automatisé (`utils.py`).
- **Modèles ML** : Comparaison automatique entre Régression Linéaire, Random Forest et Gradient Boosting (`ml_models.py`).

## 4. Guide d'Utilisation Rapide
1. **Accueil** : Vision globale du marché et conditions marines nationales.
2. **Analytics** : Exploration approfondie des données historiques.
3. **Machine Learning** : Entraînement du modèle et consultation de l'importance des variables.
4. **Simulateur** : Test de scénarios (impact d'une tempête ou d'une hausse du carburant sur les prix).

---
*Document généré le 19 février 2026.*
