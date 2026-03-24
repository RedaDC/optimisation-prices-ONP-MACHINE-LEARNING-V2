"""
Module d'Analyse Exploratoire des Données (EDA) - Application ONP
==================================================================

Ce module génère des visualisations interactives pour:
- Distribution des prix par espèce
- Prix par port (analyse géographique)
- Relation Volume ↔ Prix
- Analyse de saisonnalité
- Tendances temporelles

Auteur: PFE Master Finance & Data Science
Contexte: Office National des Pêches (ONP) - Maroc
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from utils import REGION_MAP


# Template Plotly professionnel (couleurs ONP Premium - Dark Mode Ready)
ONP_TEMPLATE = go.layout.Template()
ONP_TEMPLATE.layout.plot_bgcolor = 'rgba(15, 23, 42, 0.5)'
ONP_TEMPLATE.layout.paper_bgcolor = 'rgba(0,0,0,0)'
ONP_TEMPLATE.layout.font = {'family': "Outfit, sans-serif", 'color': "#FFFFFF"}
# Palette Halieutis Excellence: Bright Blue, Emerald, Gold, Azure
ONP_TEMPLATE.layout.colorway = ["#38BDF8", "#10B981", "#FFD700", "#6366F1", "#F472B6"]


def plot_price_distribution_by_species(df):
    """
    Crée un graphique de distribution des prix par espèce.
    
    Args:
        df (pd.DataFrame): DataFrame avec colonnes 'espece' et 'prix_unitaire_dh'
        
    Returns:
        plotly.graph_objects.Figure: Graphique interactif
    """
    fig = px.box(
        df,
        x='espece',
        y='prix_unitaire_dh',
        color='espece',
        title='Distribution des prix par espèce',
        labels={
            'espece': 'Espèce',
            'prix_unitaire_dh': 'Prix (DH/kg)'
        },
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    
    fig.update_layout(
        template=ONP_TEMPLATE,
        showlegend=False,
        height=500,
        xaxis_tickangle=-45
    )
    
    return fig


def plot_price_by_port(df):
    """
    Compare les prix moyens par port.
    """
    prix_moyen = df.groupby('port')['prix_unitaire_dh'].mean().reset_index().sort_values('prix_unitaire_dh', ascending=False)
    
    fig = px.bar(
        prix_moyen,
        x='port',
        y='prix_unitaire_dh',
        title='Top 10 Ports : Analyse des Prix Moyens',
        labels={'port': 'Port', 'prix_unitaire_dh': 'Prix Moyen (DH/kg)'},
        color_continuous_scale='Solar',
        template=ONP_TEMPLATE,
        text='prix_unitaire_dh'
    )
    
    fig.update_traces(
        texttemplate='%{text:.1f} DH', 
        textposition='outside',
        textfont=dict(size=11, color="white")
    )
    
    fig.update_layout(
        template=ONP_TEMPLATE,
        showlegend=False,
        height=450
    )
    
    return fig


def plot_volume_price_relationship(df):
    """
    Analyse la relation entre volume et prix (scatter plot).
    
    Args:
        df (pd.DataFrame): DataFrame avec 'volume_kg' et 'prix_unitaire_dh'
        
    Returns:
        plotly.graph_objects.Figure: Graphique interactif
    """
    # Utiliser toutes les données pour afficher toutes les espèces
    df_sample = df
    
    fig = px.scatter(
        df_sample,
        x='volume_kg',
        y='prix_unitaire_dh',
        color='espece',
        size='volume_kg',
        title='Relation volume / prix',
        labels={
            'volume_kg': 'Volume (kg)',
            'prix_unitaire_dh': 'Prix (DH/kg)',
            'espece': 'Espèce'
        },
        opacity=0.6,
        hover_data=['port']
    )
    
    fig.update_layout(
        template=ONP_TEMPLATE,
        height=500
    )
    
    return fig


def plot_seasonal_analysis(df):
    """
    Analyse la saisonnalité des prix.
    
    Args:
        df (pd.DataFrame): DataFrame avec 'date_vente' et 'prix_unitaire_dh'
        
    Returns:
        plotly.graph_objects.Figure: Graphique interactif
    """
    # Créer la colonne mois si elle n'existe pas
    if 'mois' not in df.columns:
        df['mois'] = pd.to_datetime(df['date_vente']).dt.month
    
    # Calculer le prix moyen par mois et assurer la présence des 12 mois
    prix_mensuel = df.groupby('mois')['prix_unitaire_dh'].mean()
    prix_mensuel = prix_mensuel.reindex(range(1, 13))
    
    mois_noms = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 
                 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
    
    fig = go.Figure()
    
    # Masquer les marqueurs pour les mois sans données (NaN)
    fig.add_trace(go.Scatter(
        x=mois_noms,
        y=prix_mensuel.values,
        mode='lines+markers',
        name='Prix Moyen (DH/kg)',
        line=dict(color='#0EA5E9', width=4, shape='spline'),
        marker=dict(size=10, color='#0B1120', line=dict(width=2, color='white')),
        connectgaps=True,
        hovertemplate="Mois: %{x}<br>Prix: %{y:.2f} DH/kg<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(
            text='Saisonnalité des Prix Moyens',
            font=dict(size=18, family="Outfit", color="#FFFFFF")
        ),
        xaxis=dict(title=None, showgrid=False),
        yaxis=dict(title='Prix (DH/kg)', gridcolor='rgba(226, 232, 240, 0.4)'),
        template=ONP_TEMPLATE,
        height=450,
        margin=dict(l=40, r=40, t=60, b=40),
        hovermode="x unified"
    )
    
    return fig


def plot_price_trends(df, espece=None):
    """
    Affiche les tendances de prix dans le temps.
    
    Args:
        df (pd.DataFrame): DataFrame avec 'date_vente' et 'prix_unitaire_dh'
        espece (str, optional): Filtrer par espèce
        
    Returns:
        plotly.graph_objects.Figure: Graphique interactif
    """
    if espece:
        df_filtered = df[df['espece'] == espece].copy()
        title = f'Évolution du prix — {espece}'
    else:
        df_filtered = df.copy()
        title = 'Évolution globale des prix'
    
    # Grouper par date
    df_trend = df_filtered.groupby('date_vente')['prix_unitaire_dh'].mean().reset_index()
    
    fig = px.line(
        df_trend,
        x='date_vente',
        y='prix_unitaire_dh',
        title=title,
        labels={
            'date_vente': 'Date',
            'prix_unitaire_dh': 'Prix Moyen (DH/kg)'
        }
    )
    
    fig.update_traces(line_color='#1e40af', line_width=2)
    
    fig.update_layout(
        template=ONP_TEMPLATE,
        height=450
    )
    
    return fig


def plot_top_species_by_volume(df, top_n=10):
    """
    Affiche les espèces les plus pêchées.
    """
    if df is None or df.empty:
        return go.Figure().update_layout(title="Aucune donnée disponible pour le Top Espèces")
    
    top_species = df.groupby('espece')['volume_kg'].sum().reset_index().sort_values('volume_kg', ascending=False).head(top_n)
    top_species['volume_tonnes'] = top_species['volume_kg'] / 1000
    
    fig = px.bar(
        top_species,
        x='volume_tonnes',
        y='espece',
        orientation='h',
        title=f'Top {top_n} espèces par volume',
        labels={'volume_tonnes': 'Volume Total (Tonnes)', 'espece': 'Espèce'},
        color_continuous_scale='Plasma',
        template=ONP_TEMPLATE,
        text='volume_tonnes'
    )
    
    fig.update_traces(
        textposition='inside',
        texttemplate='%{text:.1f} T',
        textfont=dict(size=12, color="white", family="Outfit"),
        marker=dict(line=dict(color='#0F172A', width=2))
    )
    
    fig.update_layout(
        template=ONP_TEMPLATE,
        height=500,
        showlegend=False
    )
    
    return fig


def plot_regional_activity_heatmap(df):
    """
    Crée une heatmap de l'activité agrégée par région et par mois.
    """
    if df is None or df.empty:
        return go.Figure().update_layout(title="Aucune donnée disponible pour l'Analyse Régionale")
    
    df_reg = df.copy()
    
    # Créer la colonne mois si elle n'existe pas
    if 'mois' not in df_reg.columns:
        df_reg['mois'] = pd.to_datetime(df_reg['date_vente']).dt.month
        
    # Mapper les ports aux régions
    df_reg['region'] = df_reg['port'].str.upper().map(REGION_MAP).fillna('AUTRE')
    
    # Créer le pivot table par région
    heatmap_data = df_reg.pivot_table(
        values='volume_kg',
        index='region',
        columns='mois',
        aggfunc='sum',
        fill_value=0
    )
    
    # Assurer que tous les mois sont présents (1-12)
    heatmap_data = heatmap_data.reindex(columns=range(1, 13), fill_value=0)
    
    mois_noms = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 
                 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
    
    # Conversion en tonnes
    z_tonnes = heatmap_data.values / 1000
    
    fig = go.Figure(data=go.Heatmap(
        z=z_tonnes,
        x=mois_noms,
        y=heatmap_data.index,
        colorscale='Viridis',
        text=np.round(z_tonnes, 1),
        texttemplate='%{text}',
        textfont={"size": 11, "family": "Outfit", "color": "white"},
        colorbar=dict(
            title=dict(text="Vol (T)", font=dict(color="white")),
            thickness=15,
            tickfont=dict(color="white")
        ),
        hovertemplate="Région: %{y}<br>Mois: %{x}<br>Volume: %{z:.1f} T<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(
            text='Vue Régionale : Activité Halieutique (Tonnes)',
            font=dict(size=18, family="Outfit", color="#FFFFFF")
        ),
        xaxis=dict(title=None),
        yaxis=dict(title=None),
        margin=dict(l=40, r=40, t=60, b=40),
        height=400,
        template=ONP_TEMPLATE
    )
    
    return fig


def plot_port_activity_heatmap(df):
    """
    Crée une heatmap de l'activité par port et mois.
    
    Returns:
        plotly.graph_objects.Figure: Graphique interactif
    """
    if df is None or df.empty:
        return go.Figure().update_layout(title="Aucune donnée disponible pour l'Activité Portuaire")
    
    # Créer la colonne mois si elle n'existe pas
    if 'mois' not in df.columns:
        df['mois'] = pd.to_datetime(df['date_vente']).dt.month
    
    # Créer le pivot table
    pivot_total = df.pivot_table(
        values='volume_kg',
        index='port',
        aggfunc='sum'
    ).sort_values('volume_kg', ascending=False)
    
    # Garder uniquement le Top 10
    top_10_ports = pivot_total.head(10).index
    df_filtered = df[df['port'].isin(top_10_ports)]
    
    heatmap_data = df_filtered.pivot_table(
        values='volume_kg',
        index='port',
        columns='mois',
        aggfunc='sum',
        fill_value=0
    )
    
    # Trier par volume total (du plus haut au plus bas)
    heatmap_data = heatmap_data.reindex(top_10_ports)
    
    # Assurer que tous les mois sont présents (1-12) pour l'alignement correct de l'axe X
    heatmap_data = heatmap_data.reindex(columns=range(1, 13), fill_value=0)
    
    mois_noms = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 
                 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
    
    # Conversion en tonnes pour la lisibilité
    z_tonnes = heatmap_data.values / 1000
    
    fig = go.Figure(data=go.Heatmap(
        z=z_tonnes,
        x=mois_noms,
        y=heatmap_data.index,
        colorscale='Viridis',
        text=np.round(z_tonnes, 1),
        texttemplate='%{text}',
        textfont={"size": 10, "family": "Outfit", "color": "white"},
        colorbar=dict(
            title=dict(text="Volume (T)", font=dict(color="white")),
            thickness=15,
            len=0.8,
            tickfont=dict(color="white")
        ),
        hovertemplate="Port: %{y}<br>Mois: %{x}<br>Volume: %{z:.1f} T<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(
            text='Top 10 Ports : Activité Mensuelle (Tonnes)',
            font=dict(size=18, family="Outfit", color="#FFFFFF")
        ),
        xaxis=dict(
            title='Mois de l\'année', 
            titlefont=dict(color="white"),
            tickfont=dict(color="white", size=10)
        ),
        yaxis=dict(
            title='Ports', 
            titlefont=dict(color="white"),
            tickfont=dict(color="white", size=10)
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        height=500,
        template=ONP_TEMPLATE
    )
    
    return fig


def create_eda_dashboard(df):
    """
    Crée un dashboard complet d'analyse exploratoire.
    
    Args:
        df (pd.DataFrame): DataFrame complet
        
    Returns:
        dict: Dictionnaire de tous les graphiques
    """
    print("INFO: Generation du dashboard EDA...")
    
    dashboard = {
        'price_distribution': plot_price_distribution_by_species(df),
        'price_by_port': plot_price_by_port(df),
        'volume_price': plot_volume_price_relationship(df),
        'seasonal': plot_seasonal_analysis(df),
        'trends': plot_price_trends(df),
        'top_species': plot_top_species_by_volume(df),
        'heatmap': plot_port_activity_heatmap(df)
    }
    
    print("DONE: Dashboard EDA cree avec succes!")
    
    return dashboard


if __name__ == "__main__":
    # Test du module
    print("Module EDA charge avec succes!")
    print("\nFonctions disponibles:")
    print("- plot_price_distribution_by_species(df)")
    print("- plot_price_by_port(df)")
    print("- plot_volume_price_relationship(df)")
    print("- plot_seasonal_analysis(df)")
    print("- plot_price_trends(df, espece=None)")
    print("- plot_top_species_by_volume(df, top_n=10)")
    print("- plot_port_activity_heatmap(df)")
    print("- create_eda_dashboard(df)")
