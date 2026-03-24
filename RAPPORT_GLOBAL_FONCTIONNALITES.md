# Guide Complet : Plateforme d'Optimisation ONP Premium

Ce document offre une vue exhaustive de chaque section de l'application, expliquant les indicateurs clés (KPIs), les graphiques et la logique métier associée.

---

## 1. Vue Exécutive (Elite Command Center)
**Objectif** : Synthèse stratégique ultracondensée pour la haute direction (Vue 2024-2025).

*   **KPIs (Chiffres Clés)** : 
    *   **Chiffre d'Affaires Global** ($M\ DH$) : Somme des recettes réelles consolidées.
    *   **Volume Total Débarqué** ($T$) : Activité physique du secteur.
    *   **Prix Moyen Pondéré** ($DH/kg$) : Valeur unitaire moyenne de la ressource.
*   **Top 5 Espèces par Valeur** : Classement des espèces générant le plus de revenus, avec leur % de contribution au CA national.
*   **Alertes de Marché** : Détection automatique des chutes de prix > 15%. Utile pour identifier les crises sur des espèces spécifiques.

---

## 2. Accueil (Dashboard National)
**Objectif** : Monitoring opérationnel en temps réel et vision institutionnelle.

*   **Situation Halieutique (Haut)** : 
    *   **Index Carburant** : Prix du gasoil par zone (Std vs Exonéré).
    *   **État de la Mer** : Météo réelle (Vent, Houle) pour anticiper les baisses de débarquements.
*   **Live Market Pulse** : Activité quotidienne moyenne par port (ex: Agadir 25T/jour). Statut "Intense" si le port est en période de forte activité.
*   **Graphiques de Dynamique** :
    *   **Top 10 Espèces (Volume)** : Barres horizontales classant les captures.
    *   **Heatmaps d'Activité** : Cartes thermiques montrant la saisonnalité géographique (zones NORD/SUD) et portuaire.
*   **Carte Stratégique** : Maillage des 22 ports majeurs du Royaume avec leur importance relative.

---

## 3. Analyse Financière
**Objectif** : Performance économique détaillée et comparaison d'années.

*   **Top Halles & MG** : Classement par rentabilité brute des 20 premières halles et des marchés de gros.
*   **Analyse Comparative 2024-2025** :
    *   **Effet Volume** : Variation du CA due uniquement à la quantité (à prix constant).
    *   **Effet Prix** : Variation due uniquement au marché (à volume constant).
    *   *Utilité* : Comprendre si une baisse de CA est due à moins de poisson (volume) ou à un effondrement des cours (prix).

---

## 4. Analytics (Intelligence de Marché)
**Objectif** : Exploration granulaire des données.

*   **Distribution (Boxplots)** : Montre la stabilité des prix. Un boxplot court = prix stable ; long = prix très volatil.
*   **Volume ↔ Prix (Corrélation)** : Vérifie la loi de l'offre et de la demande. Si la courbe descend quand le volume monte, le marché est "sain".
*   **Saisonnalité** : Graphique en ligne montrant les pics de prix par mois sur plusieurs années.

---

## 5. Machine Learning (IA Prédictive)
**Objectif** : Anticiper et recommander.

*   **Assistant de Débarquement** : Suggère le port optimal (parmi les 22) pour vendre un lot spécifique au meilleur prix net estimé.
*   **Mise à Prix** : Calcule le prix de départ suggéré pour une vente (ex: commencer à 18 DH pour finir à 24 DH).
*   **Interprétation IA** : Explique *pourquoi* le prix est prédit à tel niveau (Impact du volume local, météo, saisonnalité).
*   **Importance Globale (XGBoost)** : Montre quels facteurs (Volume, Port, Mois) influencent le plus le prix au niveau national.

---

## 6. Simulateur B2B (Mares/Marge)
**Objectif** : Aide au calcul de rentabilité pour les mareyeurs.

*   **Logique de Calcul** : Intègre automatiquement les taxes réglementaires (**4% ONP + 1% Commune**).
*   **Coûts Logistiques** : Glace, manutention, transport, emballage.
*   **Waterfall Chart** : Graphique en "cascade" montrant comment la marge brute se réduit au fil des frais pour aboutir au **Profit Net**.

---

## 7. Simulateur Stratégique
**Objectif** : Analyse d'impact "What-If" sur les cours.

*   **Curseurs Interactifs** : Modifiez le volume débarqué (ex: +20%) et voyez l'impact instantané sur le prix prédit.
*   **Repos Biologique** : Alerte visuelle si l'espèce simulée est actuellement protégée.

---

## 8. Rapport (V1)
**Objectif** : Formalisation institutionnelle.

*   **Mise en Page** : Format "Facture/Bordereau" propre à l'ONP.
*   **Contenu** : Synthèse des KPIs, analyse sectorielle vs prévisions IA.
*   **Export Word (.docx)** : Génération automatisée d'un document prêt à l'impression pour les réunions de comité.

---
*Ce rapport constitue la base de formation pour l'utilisation experte de la plateforme ONP Premium.*
