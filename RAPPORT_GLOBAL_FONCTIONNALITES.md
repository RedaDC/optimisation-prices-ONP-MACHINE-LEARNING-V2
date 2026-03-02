# Rapport Global : Plateforme d'Optimisation ONP Premium

Ce rapport présente une description exhaustive des fonctionnalités, de la logique métier et de l'architecture technique de l'application de pilotage halieutique.

## 1. Vision et Objectifs Stratégiques
L'application ONP Premium est conçue comme un "Command Center Digital" pour l'Office National des Pêches. Elle vise à :
- Centraliser les données de crie nationales.
- Anticiper les fluctuations du marché via le Machine Learning.
- Offrir une visibilité immédiate sur les conditions opérationnelles (Météo/Économie).

## 2. Modules de l'Interface

### A. Centre de Commande (Accueil)
- **Tableau de Bord National** : Synthèse dynamique de la météo marine (vent, mer) pour les ports de Tanger, Casablanca, Agadir et Dakhla.
- **Observatoire des Coûts** : Affichage en temps réel du prix du gasoil avec distinction automatique entre le régime standard (Nord/Centre) et exonéré (Sud).
- **Cartographie Interactive** : Maillage territorial complet du Royaume montrant les zones de captation stratégiques.
- **Market Pulse** : Visualisation du flux d'activité des halles en direct.
- **Météo des Prix** : Analyse thermique des tendances par espèce majeure.

### B. Module Analytics (Exploration de Données)
- **Filtres Avancés** : Segmentation par Délégation Régionale (DR), Port et Espèce.
- **Visualisations Temporelles** : Évolution des prix et volumes sur plusieurs années.
- **Top Espèces** : Identification automatique des espèces leaders en volume et en valeur.

### C. Analyse Financière et Comparative
- **Comparaison N vs N-1** : Analyse détaillée des écarts de performance entre 2024 et 2025.
- **Impact DR** : Contribution de chaque direction régionale à la recette globale.
- **Générateur de Rapports** : Exportation automatisée des analyses vers des formats documentaires.

### D. Moteur Machine Learning (IA)
- **Algorithmes** : Utilisation d'un modèle HistGradientBoosting optimisé.
- **Lois Économiques** : Intégration de contraintes de monotonie pour garantir que la relation "Offre/Demande" est respectée (si le volume augmente, le prix prédit baisse logiquement).
- **Importance des Variables** : Analyse des facteurs influençant le plus les prix (Volume, Port, Mois, Météo).

### E. Simulateur de Scénarios
- **Impact Météo** : Simulation du prix de vente en cas de tempête ou mer agitée (réduction supposée de l'offre).
- **Impact Carburant** : Répercussion des variations du prix du gasoil sur les cours du poisson.
- **Impact Réglementaire** : Prise en compte automatique des périodes de repos biologique par espèce.

## 3. Architecture et Flux de Données

### Pipeline Technique
1. **Extraction/Ingestion** : Importation de fichiers Excel/CSV via le module d'extraction dédié.
2. **Feature Engineering** (`utils.py`) : Création automatique de variables dérivées (Log Volume, Saisonnalité, Rareté relative, Conditions exogènes).
3. **Prédiction** (`ml_models.py`) : Moteur de calcul basé sur les dernières données entraînées.
4. **Visualisation** (`app_premium.py`) : Interface premium sans emojis pour un ton strictement professionnel.

## 4. Maintenance et Évolutivité
- **Données Externes** : Connexion automatisée aux APIs Open-Meteo et sources de cours du pétrole.
- **Apprentissage Continu** : Le modèle peut être réentraîné via l'interface dès que de nouvelles données réelles sont disponibles.

---
*Ce rapport constitue la documentation officielle de la version 2.0 de la plateforme ONP Premium.*
