# DOCUMENT DE SYNTHÈSE STRATÉGIQUE
## Plateforme d'Aide à la Décision Halieutique (v2.0)

**Date** : 19 Février 2026  
**Objet** : Documentation Fonctionnelle et Technique Institutionnelle  
**Projet** : Optimisation et Numérisation des Flux (Plan Halieutis 2026)

---

### TABLE DES MATIÈRES
1. [SYNTHÈSE EXÉCUTIVE](#1-synthèse-exécutive)
2. [PÉRIMÈTRE FONCTIONNEL](#2-périmètre-fonctionnel)
   - 2.1 [Souveraineté Halieutique et Monitoring](#21-souveraineté-halieutique-et-monitoring)
   - 2.2 [Analytics et Intelligence de Marché](#22-analytics-et-intelligence-de-marché)
3. [MOTEUR D'INTELLIGENCE ARTIFICIELLE](#3-moteur-dintelligence-artificielle)
   - 3.1 [Modélisation et Élasticité Prix-Volume](#31-modélisation-et-élasticité-prix-volume)
   - 3.2 [Considérations Multi-Régionales](#32-considérations-multi-régionales)
4. [SPÉCIFICATIONS TECHNIQUES](#4-spécifications-techniques)
5. [CONCLUSION ET PERSPECTIVES](#5-conclusion-et-perspectives)

---

### 1. SYNTHÈSE EXÉCUTIVE
Ce document présente les capacités opérationnelles de la nouvelle interface ONP Premium. La transition vers une architecture "National-First" permet désormais un pilotage unifié des 22 ports stratégiques du Royaume, intégrant des dimensions exogènes critiques telles que la météo marine et les disparités énergétiques régionales.

### 2. PÉRIMÈTRE FONCTIONNEL

#### 2.1 Souveraineté Halieutique et Monitoring
La plateforme assure une surveillance continue de l'ensemble du littoral marocain via deux piliers :
- **Synthèse Météorologique Nationale** : Intégration en temps réel des conditions de mer (force du vent, état de la houle) sur des points nodaux (Tanger, Casablanca, Agadir, Dakhla). Cette donnée permet d'anticiper les ruptures d'approvisionnement.
- **Index Énergétique Territorial** : Gestion automatisée du coût des intrants (gasoil) selon le régime fiscal applicable. Le système distingue nativement les zones de droit commun du régime exonéré spécifique aux provinces du Sud.

#### 2.2 Analytics et Intelligence de Marché
Le module d'analyse offre une granularité décisionnelle sans précédent :
- **KPIs Dynamiques** : Recette totale (en MDH), prix moyens pondérés et volumes transactionnels.
- **Analyse Comparative Inter-annuelle** : Étude fine des différentiels entre les exercices 2024 et 2025 pour l'identification des tendances de fond.

### 3. MOTEUR D'INTELLIGENCE ARTIFICIELLE

#### 3.1 Modélisation et Élasticité Prix-Volume
Le cœur du système repose sur un algorithme de Gradient Boosting (HGBR) configuré pour respecter les fondamentaux économiques de la loi de l'offre et de la demande. Des contraintes de monotonie négative sont appliquées aux volumes pour garantir la cohérence des prédictions (un enrichissement de l'offre entraînant mécaniquement une pression baissière sur les cours).

#### 3.2 Considérations Multi-Régionales
Contrairement aux modèles standards, l'IA de l'ONP pondère les prédictions en fonction de la localisation géographique et du régime énergétique associé, assurant une précision accrue pour les halles de Dakhla et Laâyoune.

### 4. SPÉCIFICATIONS TECHNIQUES
- **Interface Utilisateur** : Design System institutionnel "Elite Command Center" basé sur le framework Streamlit.
- **Traitement de Données** : Pipeline de Feature Engineering automatisé traitant les périodes de repos biologique et les variables saisonnières.
- **Interopérabilité** : Architecture prête pour l'ingestion de flux via APIs gouvernementales et maritimes.

### 5. CONCLUSION ET PERSPECTIVES
La plateforme ONP Premium version 2.0 s'impose comme l'outil de référence pour la valorisation des ressources halieutiques. Son approche scientifique de la prédiction des prix sécurise les revenus des pêcheurs et optimise la transparence des transactions à l'échelle nationale.

---
*Fin du document.*
