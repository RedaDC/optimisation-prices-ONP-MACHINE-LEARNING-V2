"""
Module d'Analyse Financière - Application ONP
==============================================

Ce module calcule et visualise:
- Recettes par port
- Contribution de chaque espèce au chiffre d'affaires
- Top espèces rentables
- Évolution temporelle des recettes
- Tableaux de bord financiers

Auteur: PFE Master Finance & Data Science
Contexte: Office National des Pêches (ONP) - Maroc
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Template Plotly professionnel
FINANCIAL_TEMPLATE = go.layout.Template()
FINANCIAL_TEMPLATE.layout.plot_bgcolor = 'rgba(0,0,0,0)'
FINANCIAL_TEMPLATE.layout.paper_bgcolor = 'rgba(0,0,0,0)'
FINANCIAL_TEMPLATE.layout.font = {'family': "Inter, sans-serif", 'color': "#1e293b"}
FINANCIAL_TEMPLATE.layout.colorway = ["#059669", "#1e40af", "#d97706", "#dc2626", "#7c3aed"]


def calculate_revenue_by_port(df):
    """
    Calcule la recette totale par port.
    
    Args:
        df (pd.DataFrame): DataFrame avec 'port', 'prix_unitaire_dh', 'volume_kg'
        
    Returns:
        pd.Series: Recettes par port (en DH)
    """
    df['recette'] = df['prix_unitaire_dh'] * df['volume_kg']
    recette_port = df.groupby('port')['recette'].sum().sort_values(ascending=False)
    return recette_port


def calculate_revenue_by_species(df):
    """
    Calcule la recette totale par espèce.
    
    Args:
        df (pd.DataFrame): DataFrame avec 'espece', 'prix_unitaire_dh', 'volume_kg'
        
    Returns:
        pd.Series: Recettes par espèce (en DH)
    """
    df['recette'] = df['prix_unitaire_dh'] * df['volume_kg']
    recette_espece = df.groupby('espece')['recette'].sum().sort_values(ascending=False)
    return recette_espece


def plot_revenue_by_port(df):
    """
    Graphique des recettes par port.
    """
    recette_port = calculate_revenue_by_port(df).reset_index()
    recette_port['recette_m'] = recette_port['recette'] / 1_000_000
    recette_port = recette_port.sort_values('recette', ascending=False)
    
    fig = px.bar(
        recette_port,
        x='port',
        y='recette_m',
        title='Recettes par port',
        labels={'port': 'Port', 'recette_m': 'Recette (Millions DH)'},
        color='recette_m',
        color_continuous_scale='Greens',
        text='recette_m'
    )
    
    fig.update_traces(texttemplate='%{text:.2f}M', textposition='outside')
    
    fig.update_layout(
        template=FINANCIAL_TEMPLATE,
        showlegend=False,
        height=500
    )
    
    return fig


def plot_revenue_contribution_by_species(df, top_n=10):
    """
    Graphique de contribution des espèces au CA (pie chart).
    """
    recette_espece = calculate_revenue_by_species(df).head(top_n).reset_index()
    
    fig = px.pie(
        recette_espece,
        values='recette',
        names='espece',
        title=f'Contribution au CA — Top {top_n} espèces',
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Greens_r
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        textfont_size=12
    )
    
    fig.update_layout(
        template=FINANCIAL_TEMPLATE,
        height=500
    )
    
    return fig


def plot_top_profitable_species(df, top_n=15):
    """
    Affiche les espèces les plus rentables.
    """
    recette_espece = calculate_revenue_by_species(df).head(top_n).reset_index()
    recette_espece['recette_m'] = recette_espece['recette'] / 1_000_000
    
    fig = px.bar(
        recette_espece,
        x='recette_m',
        y='espece',
        orientation='h',
        title=f'Top {top_n} espèces les plus rentables',
        labels={'recette_m': 'Recette (Millions DH)', 'espece': 'Espèce'},
        color='recette_m',
        color_continuous_scale='Greens',
        text='recette_m'
    )
    
    fig.update_traces(texttemplate='%{text:.2f}M', textposition='outside')
    
    fig.update_layout(
        template=FINANCIAL_TEMPLATE,
        height=600,
        showlegend=False
    )
    
    return fig


def plot_revenue_evolution(df, frequency='M'):
    """
    Évolution temporelle des recettes.
    
    Args:
        df (pd.DataFrame): DataFrame avec 'date_vente'
        frequency (str): Fréquence d'agrégation ('D', 'W', 'M')
        
    Returns:
        plotly.graph_objects.Figure: Graphique interactif
    """
    df['recette'] = df['prix_unitaire_dh'] * df['volume_kg']
    df['date_vente'] = pd.to_datetime(df['date_vente'])
    
    # Grouper par période
    df_grouped = df.set_index('date_vente').resample(frequency)['recette'].sum().reset_index()
    df_grouped['recette_mdh'] = df_grouped['recette'] / 1_000_000
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_grouped['date_vente'],
        y=df_grouped['recette_mdh'],
        mode='lines+markers',
        name='Recette',
        line=dict(color='#059669', width=3),
        marker=dict(size=8, color='#1e40af'),
        fill='tozeroy',
        fillcolor='rgba(5, 150, 105, 0.1)'
    ))
    
    freq_labels = {'D': 'Quotidienne', 'W': 'Hebdomadaire', 'M': 'Mensuelle'}
    
    fig.update_layout(
        title=f'Évolution {freq_labels.get(frequency, "")} des recettes',
        xaxis_title='Date',
        yaxis_title='Recette (Millions DH)',
        template=FINANCIAL_TEMPLATE,
        height=450,
        hovermode='x unified'
    )
    
    return fig


def plot_revenue_by_port_and_species(df, top_ports=5, top_species=5):
    """
    Graphique croisé: recettes par port et espèce.
    
    Args:
        df (pd.DataFrame): DataFrame avec données
        top_ports (int): Nombre de ports à afficher
        top_species (int): Nombre d'espèces à afficher
        
    Returns:
        plotly.graph_objects.Figure: Graphique interactif
    """
    df['recette'] = df['prix_unitaire_dh'] * df['volume_kg']
    
    # Sélectionner top ports et espèces
    top_ports_list = calculate_revenue_by_port(df).head(top_ports).index.tolist()
    top_species_list = calculate_revenue_by_species(df).head(top_species).index.tolist()
    
    # Filtrer
    df_filtered = df[
        (df['port'].isin(top_ports_list)) & 
        (df['espece'].isin(top_species_list))
    ]
    
    # Créer pivot table
    pivot = df_filtered.pivot_table(
        values='recette',
        index='espece',
        columns='port',
        aggfunc='sum',
        fill_value=0
    ) / 1_000_000  # En millions
    
    fig = go.Figure()
    
    for port in pivot.columns:
        fig.add_trace(go.Bar(
            name=port,
            x=pivot.index,
            y=pivot[port],
            text=pivot[port].round(2),
            texttemplate='%{text}M',
            textposition='auto'
        ))
    
    fig.update_layout(
        title=f'Recettes croisées : Top {top_ports} ports × Top {top_species} espèces',
        xaxis_title='Espèce',
        yaxis_title='Recette (Millions DH)',
        barmode='group',
        template=FINANCIAL_TEMPLATE,
        height=500,
        xaxis_tickangle=-45
    )
    
    return fig


def create_financial_summary_table(df):
    """
    Crée un tableau récapitulatif financier.
    
    Args:
        df (pd.DataFrame): DataFrame avec données
        
    Returns:
        pd.DataFrame: Tableau récapitulatif
    """
    df['recette'] = df['prix_unitaire_dh'] * df['volume_kg']
    
    summary = pd.DataFrame({
        'Indicateur': [
            'Recette Totale (MDH)',
            'Volume Total (Tonnes)',
            'Prix Moyen (DH/kg)',
            'Nombre de Transactions',
            'Recette Moyenne par Transaction (DH)',
            'Port le Plus Rentable',
            'Espèce la Plus Rentable'
        ],
        'Valeur': [
            f"{df['recette'].sum() / 1_000_000:.2f}",
            f"{df['volume_kg'].sum() / 1000:.2f}",
            f"{df['prix_unitaire_dh'].mean():.2f}",
            f"{len(df):,}",
            f"{df['recette'].mean():.2f}",
            calculate_revenue_by_port(df).idxmax(),
            calculate_revenue_by_species(df).idxmax()
        ]
    })
    
    return summary


def create_financial_dashboard(df):
    """
    Crée un dashboard financier complet.
    
    Args:
        df (pd.DataFrame): DataFrame complet
        
    Returns:
        dict: Dictionnaire de tous les graphiques et tableaux
    """
    print("INFO: Generation du dashboard financier...")
    
    dashboard = {
        'revenue_by_port': plot_revenue_by_port(df),
        'revenue_contribution': plot_revenue_contribution_by_species(df),
        'top_profitable': plot_top_profitable_species(df),
        'revenue_evolution': plot_revenue_evolution(df),
        'revenue_cross': plot_revenue_by_port_and_species(df),
        'summary_table': create_financial_summary_table(df)
    }
    
    print("DONE: Dashboard financier cree avec succes!")
    
    return dashboard


if __name__ == "__main__":
    # Test du module
    print("Module Analyse Financiere charge avec succes!")
    print("\nFonctions disponibles:")
    print("- calculate_revenue_by_port(df)")
    print("- calculate_revenue_by_species(df)")
    print("- plot_revenue_by_port(df)")
    print("- plot_revenue_contribution_by_species(df, top_n=10)")
    print("- plot_top_profitable_species(df, top_n=15)")
    print("- plot_revenue_evolution(df, frequency='M')")
    print("- plot_revenue_by_port_and_species(df)")
    print("- create_financial_summary_table(df)")
    print("- create_financial_dashboard(df)")

def calculate_price_volume_effect(df):
    """
    Calcule l'effet Prix et l'effet Volume pour la comparaison 2024-2025.
    
    Args:
        df (pd.DataFrame): DataFrame avec colonnes 'annee', 'espece', 'volume_kg', 'prix_unitaire_dh'
        
    Returns:
        pd.DataFrame: DataFrame avec les effets calculés par espèce
    """
    if 'annee' not in df.columns or df.empty:
        return pd.DataFrame()
        
    # S'assurer que les années sont bien présentes
    years = df['annee'].unique()
    if not (2024 in years and 2025 in years):
        # Essayer de trouver les deux années les plus récentes si 2024/2025 ne sont pas là
        sorted_years = sorted(years, reverse=True)
        if len(sorted_years) >= 2:
            y_curr, y_prev = sorted_years[0], sorted_years[1]
        else:
            return pd.DataFrame()
    else:
        y_curr, y_prev = 2025, 2024

    # Calcul de la recette ligne par ligne si elle n'existe pas
    if 'recette' not in df.columns:
        df['recette'] = df['prix_unitaire_dh'] * df['volume_kg']
    
    # 1. Agréger les données par année et espèce
    df_agg = df[df['annee'].isin([y_prev, y_curr])].groupby(['annee', 'espece']).agg({
        'volume_kg': 'sum',
        'recette': 'sum'
    }).reset_index()
    
    # 2. Calculer le Prix Moyen pondéré
    df_agg['prix_moyen'] = df_agg['recette'] / (df_agg['volume_kg'] + 1e-9)
    
    # 3. Pivoter
    df_pivot = df_agg.pivot(index='espece', columns='annee', values=['volume_kg', 'prix_moyen', 'recette'])
    
    # Aplatir les colonnes
    df_pivot.columns = [f'{col[0]}_{col[1]}' for col in df_pivot.columns]
    df_pivot = df_pivot.reset_index().fillna(0)
    
    # Mapper vers des noms génériques pour le calcul
    vol_prev = f'volume_kg_{y_prev}'
    vol_curr = f'volume_kg_{y_curr}'
    prix_prev = f'prix_moyen_{y_prev}'
    prix_curr = f'prix_moyen_{y_curr}'
    rec_prev = f'recette_{y_prev}'
    rec_curr = f'recette_{y_curr}'
    
    # 4. Calcul des Effets
    # Effet Volume = (V_curr - V_prev) * P_prev
    df_pivot['effet_volume'] = (df_pivot[vol_curr] - df_pivot[vol_prev]) * df_pivot[prix_prev]
    
    # Effet Prix = (P_curr - P_prev) * V_curr
    df_pivot['effet_prix'] = (df_pivot[prix_curr] - df_pivot[prix_prev]) * df_pivot[vol_curr]
    
    # Variation Totale
    df_pivot['variation_totale'] = df_pivot[rec_curr] - df_pivot[rec_prev]
    
    # Métriques d'affichage en Millions DH
    df_pivot['recette_2024_mdh'] = df_pivot[rec_prev] / 1_000_000
    df_pivot['recette_2025_mdh'] = df_pivot[rec_curr] / 1_000_000
    df_pivot['variation_mdh'] = df_pivot['variation_totale'] / 1_000_000
    df_pivot['effet_volume_mdh'] = df_pivot['effet_volume'] / 1_000_000
    df_pivot['effet_prix_mdh'] = df_pivot['effet_prix'] / 1_000_000
    
    return df_pivot.sort_values('variation_totale', ascending=False)


def plot_price_volume_analysis(df_effects, top_n=10):
    """
    Visualise l'effet prix-volume pour les top espèces (WaterFall ou Barres).
    """
    if df_effects.empty:
        return go.Figure()
        
    top_df = df_effects.head(top_n).copy()
    
    # Graphique en barres empilées pour montrer la contribution
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Effet Volume',
        x=top_df['espece'],
        y=top_df['effet_volume_mdh'],
        marker_color='#3b82f6' # Bleu
    ))
    
    fig.add_trace(go.Bar(
        name='Effet Prix',
        x=top_df['espece'],
        y=top_df['effet_prix_mdh'],
        marker_color='#ef4444' # Rouge
    ))
    
    fig.add_trace(go.Scatter(
        name='Variation Totale',
        x=top_df['espece'],
        y=top_df['variation_mdh'],
        mode='markers',
        marker=dict(color='black', size=10, symbol='diamond'),
        yaxis='y'
    ))
    
    fig.update_layout(
        title=f'Décomposition de la variation du CA (2024 vs 2025) - Top {top_n} espèces',
        xaxis_title='Espèce',
        yaxis_title='Impact (Millions DH)',
        barmode='relative',
        template=FINANCIAL_TEMPLATE,
        height=500
    )
    
    return fig
