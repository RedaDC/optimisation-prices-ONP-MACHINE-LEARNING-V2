# Rapport de Fonctionnement : Application ONP Premium

## 1. Vue d'Ensemble
L'application **ONP Premium** est une plateforme d'intelligence décisionnelle conçue pour l'Office National des Pêches. Elle combine analyse de données historiques, pilotage financier et prédiction algorithmique pour optimiser la valorisation des produits de la mer au Maroc.

---

## 2. Architecture du Système
L'architecture est modulaire, séparant l'interface utilisateur de la logique métier et du moteur d'IA.

### Composants Clés :
- **`app_premium.py`** : Interface principale (Streamlit) utilisant un design "Glassmorphism" professionnel.
- **`ml_models.py`** : Moteur de machine learning (HGBoost) avec contraintes de monotonie pour garantir l'élasticité prix-volume.
- **`utils.py`** : Pipeline de préparation de données, nettoyage et ingénierie de variables (Features).
- **`ml_interpretation.py`** : Moteur d'explication "Pourquoi" transformant les coefficients mathématiques en insights métier.
- **`ml_operations.py`** : Fonctions opérationnelles (Détection d'anomalies, Mise à prix suggérée, Recommandations de débarquement).

---

## 3. Modules Fonctionnels

### A. Analyse de Marché (Analytics)
Analyse visuelle des tendances de prix par port et par espèce. Permet de détecter les cycles saisonniers et les disparités géographiques.

### B. Analyse Financière
Calcul de l'effet "Prix-Volume" permettant de comprendre si l'évolution du chiffre d'affaires est due à une hausse des cours ou à une augmentation des tonnages.

### C. Intelligence Artificielle (Machine Learning)
Prédiction des prix unitaires (DH/kg) basée sur 16 variables, dont :
- **Volume et Log-Volume** : Pour une sensibilité accrue aux tonnages.
- **Repos Biologique** : Intégration des périodes de fermeture réglementaire.
- **Saisonnalité** : Synchronisation avec la date réelle du jour.

### D. Simulateur d'Impact
Outil de "What-if" permettant de simuler des scénarios de débarquement et d'anticiper les prix de vente avant la criée.

---

## 4. Logique Métier Avancée

### Élasticité Prix-Volume
Le modèle respecte la loi de l'offre et de la demande :
- **Hausse du Volume** → Baisse fluide du prix prédit.
- **Baisse du Volume** → Hausse du prix.
L'usage de transformations logarithmiques permet une précision maximale sur les petits et grands tonnages.

### Repos Biologique
Le système intègre une cartographie précise des périodes de fermeture (Céphalopodes, Crustacés, etc.). 
- **Impact** : Un coefficient de rareté (+25%) est appliqué pour refléter la hausse des cours due à la suspension des captures.
- **Explication** : Le moteur détaille les raisons (pression de la demande, arrêt des captures) dans l'interface.

### Détection d'Anomalies
Analyse en temps réel de la conformité des transactions :
- **Z-Score Statistique** : Détecte les prix hors-normes historiquement.
- **Déviation IA** : Signale quand le prix de vente réel s'écarte trop de la valeur "juste" prédite par le modèle.

---

## 5. Sécurité et Fiabilité
- **Plancher Économique** : Aucune prédiction ne peut descendre en dessous de 1.0 DH/kg.
- **Traitement des Valeurs Manquantes** : Remplissage intelligent basé sur les moyennes historiques par port et espèce.
- **Branding Institutionnel** : Interface unifiée respectant l'identité visuelle de l'ONP.

---
*Ce rapport a été généré pour documenter l'état actuel de la solution ONP Price Optimization (Version 2.0).*
