"""
Module d'Analyse de la Saisonnalité des Prix — ONP Premium
===========================================================
Dashboard interactif à 4 facteurs :
  1. Volume & Prix mensuel par espèce/catégorie
  2. Calendrier biologique (repos biologique)
  3. Corrélation prix-carburant
  4. Indicateurs climatiques (SST, anomalies)
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# ═══════════════════════════════════════════════════════════════════
# 1. DONNÉES DE RÉFÉRENCE STATIQUES
# ═══════════════════════════════════════════════════════════════════

MOIS_LABELS = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
               'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']

# Calendrier de repos biologique (mois: 1-12 = repos)
# Sources: Bulletin Officiel ONP, Réglementation halieutique marocaine
CALENDRIER_BIOLOGIQUE = {
    'CEPHALOPODES': {
        'mois_repos': [10, 11, 12, 1],   # Oct-Jan: repos poulpe/calmar côte atlantique
        'motif': 'Repos biologique Poulpe\n(reproduction atlantique)',
        'couleur': 'rgba(244, 63, 94, 0.15)'
    },
    'POISSON PELAGIQUE': {
        'mois_repos': [3, 4, 8],          # Mars-Avr: sardine fraie / Août: maquereau
        'motif': 'Restriction captures pélagiques\n(sardine/maquereau)',
        'couleur': 'rgba(59, 130, 246, 0.15)'
    },
    'CRUSTACES': {
        'mois_repos': [5, 6],             # Mai-Juin: crevettes (saison fraie)
        'motif': 'Repos biologique Crevettes\n(saison de fraie)',
        'couleur': 'rgba(249, 115, 22, 0.15)'
    },
    'POISSON BLANC': {
        'mois_repos': [2, 3],             # Fév-Mar: merlu
        'motif': 'Repos biologique Merlu\n(fraie hivernale)',
        'couleur': 'rgba(16, 185, 129, 0.15)'
    },
    'COQUILLAGES': {
        'mois_repos': [6, 7, 8],          # Été: risque sanitaire + fraie
        'motif': 'Suspension sanitaire estivale\n(qualité des eaux)',
        'couleur': 'rgba(139, 92, 246, 0.15)'
    },
    'ALGUES': {
        'mois_repos': [7, 8],             # Été: chaleur dégradant la biomasse
        'motif': 'Pause récolte estivale\n(biomasse faible)',
        'couleur': 'rgba(234, 179, 8, 0.15)'
    }
}

# Mapping des espèces spécifiques vers leur catégorie biologique
def get_biocalendar_for_species(esp: str) -> dict:
    esp_up = str(esp).upper()
    if esp_up in CALENDRIER_BIOLOGIQUE: return CALENDRIER_BIOLOGIQUE[esp_up]
    
    if any(x in esp_up for x in ['POULPE', 'CALMAR', 'SEICHE', 'ENCORNET']):
        return CALENDRIER_BIOLOGIQUE['CEPHALOPODES']
    if any(x in esp_up for x in ['SARDINE', 'MAQUEREAU', 'ANCHOIS', 'CHINCHARD']):
        return CALENDRIER_BIOLOGIQUE['POISSON PELAGIQUE']
    if any(x in esp_up for x in ['CREVETTE', 'LANGOUSTE', 'HOMARD', 'CRABE', 'ARAIGNEE']):
        return CALENDRIER_BIOLOGIQUE['CRUSTACES']
    if any(x in esp_up for x in ['MERLU', 'SOLE', 'PAGEOT', 'DORADE', 'BAR', 'BADECHE']):
        return CALENDRIER_BIOLOGIQUE['POISSON BLANC']
    if any(x in esp_up for x in ['MOULE', 'HUITRE', 'COQUE', 'PRAIRE', 'PALOURDE']):
        return CALENDRIER_BIOLOGIQUE['COQUILLAGES']
    # Algues spécifiques
    if 'ALGUE' in esp_up:
         return CALENDRIER_BIOLOGIQUE['ALGUES']
         
    return {}

# Prix du carburant mensuel (DH/L) — Historique 2024-2025 CENTRE
# Basé sur données ONHYM/Afriquia 2024-2025
FUEL_PRICES_2024 = [10.20, 10.18, 10.25, 10.30, 10.35, 10.40,
                    10.42, 10.45, 10.50, 10.52, 10.48, 10.45]
FUEL_PRICES_2025 = [10.43, 10.40, 10.38, 10.35, 10.32, 10.30,
                    10.28, 10.25, 10.22, 10.20, 10.18, 10.15]

# Température Surface de la Mer (SST) — Atlantique côte marocaine (°C)
# Sources: NOAA/Copernicus Marine, Moyennes 2020-2025
SEA_TEMP_2024 = [17.2, 16.8, 17.5, 18.2, 19.0, 20.5,
                  22.1, 23.0, 22.5, 21.0, 19.5, 18.0]
SEA_TEMP_2025 = [17.5, 17.0, 17.8, 18.5, 19.3, 20.8,
                  22.4, 23.3, 22.8, 21.2, 19.8, 18.3]
# Climatologie normale (moyennes 1991-2020)
SEA_TEMP_NORME = [17.0, 16.5, 17.2, 18.0, 18.8, 20.2,
                   21.8, 22.5, 22.0, 20.5, 19.0, 17.5]


# ═══════════════════════════════════════════════════════════════════
# 2. FONCTIONS D'AGRÉGATION DES DONNÉES
# ═══════════════════════════════════════════════════════════════════

def get_monthly_stats(df: pd.DataFrame, espece_list: list, annee: int) -> pd.DataFrame:
    """
    Calcule les statistiques mensuelles agrégées pour une liste de catégories d'espèces.
    Returns DataFrame with mois 1-12, vol_t (tonnes), prix_moy (DH/kg), ca_kdh.
    """
    mask = (df['annee'] == annee)
    if espece_list:
        mask = mask & (df['espece'].isin(espece_list))

    df_sub = df[mask].copy()
    if df_sub.empty:
        return pd.DataFrame({'mois': range(1, 13), 'vol_t': 0, 'prix_moy': 0, 'ca_kdh': 0})

    df_sub['ca'] = df_sub['volume_kg'] * df_sub['prix_unitaire_dh']
    monthly = df_sub.groupby('mois').agg(
        vol_t=('volume_kg', lambda x: x.sum() / 1000),
        ca_kdh=('ca', lambda x: x.sum() / 1000),
    ).reset_index()

    # Prix moyen pondéré par le volume (évite la moyenne simple biaisée)
    def weighted_price(grp):
        vol = grp['volume_kg'].sum()
        return (grp['volume_kg'] * grp['prix_unitaire_dh']).sum() / vol if vol > 0 else 0

    prix_df = df_sub.groupby('mois').apply(weighted_price).reset_index()
    prix_df.columns = ['mois', 'prix_moy']

    monthly = monthly.merge(prix_df, on='mois')

    # S'assurer que tous les mois 1-12 sont présents
    all_months = pd.DataFrame({'mois': range(1, 13)})
    monthly = all_months.merge(monthly, on='mois', how='left').fillna(0)

    return monthly


def get_fuel_series(annee: int) -> list:
    """Retourne la série du prix du carburant pour l'année donnée."""
    return FUEL_PRICES_2024 if annee == 2024 else FUEL_PRICES_2025


def get_sst_series(annee: int) -> list:
    """Retourne les températures de surface de la mer pour l'année."""
    return SEA_TEMP_2024 if annee == 2024 else SEA_TEMP_2025


def compute_fuel_correlation(prix_serie: list, fuel_serie: list) -> float:
    """Corrélation de Pearson entre prix pêche et carburant."""
    p = np.array(prix_serie)
    f = np.array(fuel_serie)
    if p.std() == 0 or f.std() == 0:
        return 0.0
    return float(np.corrcoef(p, f)[0, 1])


# ═══════════════════════════════════════════════════════════════════
# 3. CONSTRUCTION DU DASHBOARD 4-PANNEAUX
# ═══════════════════════════════════════════════════════════════════

def build_seasonality_dashboard(df: pd.DataFrame, espece_list: list, annees: list) -> go.Figure:
    """
    Génère le dashboard de saisonnalité interactif en Plotly.
    
    Panneau 1 (haut) : Volume (barres) + Prix moyen pondéré (ligne) — 12 mois
    Panneau 2 (milieu haut) : Zones repos biologique + Volume normalisé
    Panneau 3 (milieu bas) : Corrélation prix-carburant (scatter + régression)
    Panneau 4 (bas) : Températures SST vs Norme + Anomalies
    """

    # Couleurs par année
    PALETTE = {2024: '#0EA5E9', 2025: '#10B981', 'both': '#F59E0B'}
    BAR_PALETTE = {2024: 'rgba(14,165,233,0.6)', 2025: 'rgba(16,185,129,0.6)'}

    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=False,
        row_heights=[0.30, 0.25, 0.25, 0.20],
        vertical_spacing=0.06,
        subplot_titles=[
            "1. Volume de captures & Prix moyen mensuel",
            "2. Calendrier Biologique (Périodes de repos)",
            "3. Corrélation Prix de pêche / Prix du carburant",
            "4. Température de surface de la mer (SST) & Anomalies"
        ]
    )

    # Déterminer les repos biologiques (union des espèces sélectionnées)
    mois_repos_union = set()
    couleur_repos = 'rgba(239, 68, 68, 0.12)'
    motif_repos = "Repos biologique"
    for esp in espece_list:
        cal = get_biocalendar_for_species(esp)
        mois_repos_union.update(cal.get('mois_repos', []))
        if 'motif' in cal:
            motif_repos = cal['motif']
        if 'couleur' in cal:
            couleur_repos = cal['couleur']

    for annee in annees:
        monthly = get_monthly_stats(df, espece_list, annee)
        fuel = get_fuel_series(annee)
        sst = get_sst_series(annee)

        col = PALETTE.get(annee, '#64748B')
        bar_col = BAR_PALETTE.get(annee, 'rgba(100,116,139,0.5)')

        # ── PANNEAU 1 : Volume (barres) + Prix (ligne) ──────────────────
        fig.add_trace(go.Bar(
            x=MOIS_LABELS,
            y=monthly['vol_t'],
            name=f'Volume {annee} (T)',
            marker_color=bar_col,
            opacity=0.85,
            showlegend=True
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=MOIS_LABELS,
            y=monthly['prix_moy'],
            name=f'Prix moyen {annee} (DH/kg)',
            mode='lines+markers',
            line=dict(color=col, width=2.5),
            marker=dict(size=7, symbol='circle'),
            yaxis='y2',
            showlegend=True
        ), row=1, col=1)

        # ── PANNEAU 2 : Zones repos + Volume normalisé ───────────────────
        max_vol = monthly['vol_t'].max() or 1
        vol_norm = (monthly['vol_t'] / max_vol * 100).tolist()

        fig.add_trace(go.Scatter(
            x=MOIS_LABELS,
            y=vol_norm,
            name=f'Volume normalisé {annee} (%)',
            mode='lines+markers',
            line=dict(color=col, width=2, dash='dot'),
            fill='tozeroy',
            fillcolor=f'rgba({14 if annee==2024 else 16},{165 if annee==2024 else 185},{233 if annee==2024 else 129},0.08)',
            showlegend=True
        ), row=2, col=1)

        # ── PANNEAU 3 : Scatter prix / carburant ────────────────────────
        prix_list = monthly['prix_moy'].tolist()
        corr = compute_fuel_correlation(prix_list, fuel)

        fig.add_trace(go.Scatter(
            x=fuel,
            y=prix_list,
            mode='markers+text',
            text=[m[:3] for m in MOIS_LABELS],
            textposition='top center',
            name=f'Prix vs Carburant {annee} (r={corr:+.2f})',
            marker=dict(
                color=list(range(1, 13)),
                colorscale='Plasma',
                size=10,
                colorbar=dict(title='Mois', len=0.25, y=0.35) if annee == annees[-1] else None,
                showscale=(annee == annees[-1])
            ),
            showlegend=True
        ), row=3, col=1)

        # Ligne régression
        if len(fuel) == len(prix_list) and np.std(fuel) > 0:
            m_coef = np.polyfit(fuel, prix_list, 1)
            x_reg = np.linspace(min(fuel), max(fuel), 50)
            y_reg = np.polyval(m_coef, x_reg)
            fig.add_trace(go.Scatter(
                x=x_reg, y=y_reg,
                mode='lines',
                name=f'Régression {annee}',
                line=dict(color=col, width=1.5, dash='dash'),
                showlegend=False
            ), row=3, col=1)

        # ── PANNEAU 4 : SST ──────────────────────────────────────────────
        fig.add_trace(go.Scatter(
            x=MOIS_LABELS,
            y=sst,
            name=f'SST {annee} (°C)',
            mode='lines+markers',
            line=dict(color=col, width=2),
            marker=dict(size=6),
            fill='tonexty' if annee == annees[-1] and len(annees) > 1 else 'none',
            showlegend=True
        ), row=4, col=1)

    # Norme climatique (tracé une seule fois)
    fig.add_trace(go.Scatter(
        x=MOIS_LABELS,
        y=SEA_TEMP_NORME,
        name='Norme SST 1991-2020 (°C)',
        mode='lines',
        line=dict(color='#94A3B8', width=1.5, dash='dot'),
        showlegend=True
    ), row=4, col=1)

    # ── Zones de repos biologique (panneaux 1 et 2) ───────────────────
    for m_idx in sorted(mois_repos_union):
        m_label = MOIS_LABELS[m_idx - 1]
        m_prev = MOIS_LABELS[m_idx - 2] if m_idx > 1 else MOIS_LABELS[0]

        for row_n in [1, 2]:
            fig.add_vrect(
                x0=m_prev, x1=m_label,
                fillcolor=couleur_repos,
                opacity=1,
                layer="below",
                line_width=0,
                row=row_n, col=1
            )

    # Annotation repos biologique (panneau 2)
    if mois_repos_union:
        first_repos = MOIS_LABELS[min(mois_repos_union) - 1]
        fig.add_annotation(
            x=first_repos,
            y=110,
            text=f"Arrêt: {motif_repos.split(chr(10))[0]}",
            showarrow=False,
            font=dict(size=9, color='#DC2626'),
            bgcolor='rgba(254,226,226,0.9)',
            bordercolor='#DC2626',
            borderwidth=1,
            row=2, col=1,
            yref='y2'
        )

    # ── Axes secondaires (prix DH/kg sur panneau 1) ──────────────────
    fig.update_layout(
        yaxis2=dict(
            title='Prix moyen (DH/kg)',
            overlaying='y',
            side='right',
            showgrid=False
        )
    )

    # ── Mise en page globale premium ─────────────────────────────────
    fig.update_layout(
        height=950,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(248,250,252,0.8)',
        font=dict(family='Outfit, sans-serif', size=11, color='#1E293B'),
        legend=dict(
            orientation='h',
            yanchor='bottom', y=-0.06,
            xanchor='center', x=0.5,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#E2E8F0',
            borderwidth=1
        ),
        barmode='group',
        margin=dict(t=60, b=40, l=60, r=60),
        hoverlabel=dict(bgcolor='white', font_size=12, font_family='Outfit'),
    )

    # Axes labels
    fig.update_yaxes(title_text='Volume (Tonnes)', row=1, col=1)
    fig.update_yaxes(title_text='Volume normalisé (%)', row=2, col=1)
    fig.update_xaxes(title_text='Prix carburant (DH/L)', row=3, col=1)
    fig.update_yaxes(title_text='Prix pêche (DH/kg)', row=3, col=1)
    fig.update_yaxes(title_text='Température (°C)', row=4, col=1)

    # Grille légère
    for r in [1, 2, 3, 4]:
        fig.update_yaxes(gridcolor='rgba(226,232,240,0.8)', row=r, col=1)
        fig.update_xaxes(gridcolor='rgba(226,232,240,0.8)', row=r, col=1)

    return fig


# ═══════════════════════════════════════════════════════════════════
# 4. TABLE SYNTHÈSE
# ═══════════════════════════════════════════════════════════════════

def build_summary_table(df: pd.DataFrame, espece_list: list, annees: list) -> pd.DataFrame:
    """
    Génère une table de synthèse mensuelle avec variation N/N-1.
    Colonnes : Mois, Vol 2024 (T), Vol 2025 (T), Δ Vol %, Prix 2024, Prix 2025, Δ Prix %,
               Carburant (DH/L), SST (°C), Repos Biologique.
    """
    rows = []
    all_mois_repos = set()
    for esp in espece_list:
        all_mois_repos.update(get_biocalendar_for_species(esp).get('mois_repos', []))

    monthly_data = {}
    for annee in [2024, 2025]:
        monthly_data[annee] = get_monthly_stats(df, espece_list, annee)

    for m in range(1, 13):
        m_label = MOIS_LABELS[m - 1]

        row = {'Mois': m_label}

        for annee in [2024, 2025]:
            md = monthly_data[annee]
            r = md[md['mois'] == m]
            row[f'Vol {annee} (T)'] = round(r['vol_t'].values[0], 1) if len(r) else 0
            row[f'Prix {annee} (DH/kg)'] = round(r['prix_moy'].values[0], 2) if len(r) else 0

        # Variation
        v24 = row.get('Vol 2024 (T)', 0)
        v25 = row.get('Vol 2025 (T)', 0)
        p24 = row.get('Prix 2024 (DH/kg)', 0)
        p25 = row.get('Prix 2025 (DH/kg)', 0)
        row['Δ Vol %'] = f"{(v25-v24)/v24*100:+.1f}%" if v24 > 0 else "—"
        row['Δ Prix %'] = f"{(p25-p24)/p24*100:+.1f}%" if p24 > 0 else "—"

        row['Carburant 2024 (DH/L)'] = FUEL_PRICES_2024[m - 1]
        row['Carburant 2025 (DH/L)'] = FUEL_PRICES_2025[m - 1]
        row['SST 2024 (°C)'] = SEA_TEMP_2024[m - 1]
        row['SST 2025 (°C)'] = SEA_TEMP_2025[m - 1]
        row['Anomalie SST (°C)'] = round(SEA_TEMP_2024[m-1] - SEA_TEMP_NORME[m-1], 2)
        row['Repos Biologique'] = 'Oui' if m in all_mois_repos else 'Non'

        rows.append(row)

    return pd.DataFrame(rows)
