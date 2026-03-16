# Rapport Technique Complet : Plateforme d'Optimisation des Prix ONP

## 1. Vue d'Ensemble du Projet
La plateforme **ONP Premium** est un outil d'aide à la décision stratégique exploitant le Machine Learning pour optimiser la valorisation des produits de la pêche au Maroc. Elle transforme les données brutes de crie en insights exploitables pour les décideurs, les gestionnaires de ports et les crieurs.

## 2. Architecture Logicielle
L'application repose sur une architecture modulaire en couches :
- **Couche Présentation (`app_premium.py`)** : Interface Streamlit haute performance avec design "Glassmorphism".
- **Moteur d'Intelligence (`ml_models.py`)** : Orchestration des modèles prédictifs (XGBoost, Random Forest).
- **Couche Opérationnelle (`ml_operations.py`)** : Logique métier appliquée (Anomalies, Aide au débarquement).
- **Pipeline de Données (`data_loader.py`)** : Ingestion robuste et flexible des formats institutionnels.
- **Noyau Utilitaire (`utils.py`)** : Feature engineering, normalisation et intégrations externes (APIs).

## 3. Pipeline de Données & Ingestion Flexible
Une innovation majeure a été apportée pour garantir la continuité opérationnelle :
- **Détection par Contenu (Heuristique)** : Le système ne dépend plus de noms de feuilles fixes (ex: "Feuil2"). Il scanne dynamiquement les fichiers Excel pour identifier les colonnes "Volume", "CA", "Port" et "Espèce".
- **Alignement Automatique** : Détection de la ligne d'en-tête (header row) pour gérer les décalages de structure dans les rapports.
- **Nettoyage Intelligent** : Suppression automatique des outliers, gestion des valeurs manquantes par médiane mobile et filtrage des espèces non identifiées.

## 4. Machine Learning & Intelligence Artificielle
Le cœur prédictif utilise un ensemble de modèles optimisés :
- **XGBoost (Elite Model)** : Modèle de gradient boosting pour une précision maximale (R² > 0.90).
- **Élasticité Prix-Volume** : Utilisation de transformations logarithmiques (`log_volume`) pour capturer la sensibilité des prix aux tonnages, respectant la loi de l'offre et de la demande.
- **Apprentissage en Ligne (Online Learning)** : Possibilité de réentraînement instantané via l'interface dès l'importation de nouvelles données.
- **Interprétabilité (Feature Importance)** : Visualisation des facteurs influençant le prix (Port, Espèce, Saisonnalité, Météo).

## 5. Intelligence Métier & Variables Exogènes
L'application va au-delà des simples données historiques en intégrations :
- **Variables Météorologiques** : Connexion API (Open-Meteo) pour récupérer la force du vent et la hauteur des houles, impactant l'offre.
- **Variables Économiques** : Suivi du prix du gasoil avec gestion des **exonérations fiscales spécifiques au Grand-Sud**.
- **Repos Biologique** : Intégration des périodes de fermeture par espèce avec application d'un coefficient de rareté (+25% sur le prix prédit).

## 6. Fonctionnalités Stratégiques
- **Aide au Débarquement** : Comparaison en temps réel de la rentabilité nette entre différents ports pour une espèce donnée.
- **Assistant de Mise à Prix** : Suggestion de prix de départ pour les crieurs (85% du prix cible prédit).
- **Surveillance du Marché** : Détection d'anomalies basée sur le Z-Score et la déviation IA pour identifier les erreurs de saisie ou les prix atypiques.

## 7. Reporting & UX Premium
- **Design Institutionnel** : Palette de couleurs harmonisée, typographie moderne (Poppins) et micro-animations.
- **Exports Documentaires** : Génération automatisée de rapports Word (`python-docx`) détaillant les effets "Prix-Volume" pour les audits financiers.
- **Visualisations Interactives** : Graphiques Plotly dynamiques permettant une exploration granulaire des tendances.

---
*Ce document sert de référence technique pour la solution ONP Price Optimization (V 2.2).*
