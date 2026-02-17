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


# Template Plotly professionnel (couleurs ONP)
ONP_TEMPLATE = go.layout.Template()
ONP_TEMPLATE.layout.plot_bgcolor = 'rgba(0,0,0,0)'
ONP_TEMPLATE.layout.paper_bgcolor = 'rgba(0,0,0,0)'
ONP_TEMPLATE.layout.font = {'family': "Inter, sans-serif", 'color': "#1e293b"}
ONP_TEMPLATE.layout.colorway = ["#1e40af", "#059669", "#d97706", "#dc2626", "#7c3aed"]  # Bleu, Vert, Orange, Rouge, Violet


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
        title='Prix moyen par port',
        labels={'port': 'Port', 'prix_unitaire_dh': 'Prix Moyen (DH/kg)'},
        color='prix_unitaire_dh',
        color_continuous_scale='Blues'
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
    # Échantillonner si trop de points
    if len(df) > 2000:
        df_sample = df.sample(n=2000, random_state=42)
    else:
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
    
    prix_mensuel = df.groupby('mois')['prix_unitaire_dh'].mean()
    
    mois_noms = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 
                 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=mois_noms,
        y=prix_mensuel.values,
        mode='lines+markers',
        name='Prix Moyen',
        line=dict(color='#1e40af', width=3),
        marker=dict(size=10, color='#059669')
    ))
    
    fig.update_layout(
        title='Saisonnalité des prix',
        xaxis_title='Mois',
        yaxis_title='Prix Moyen (DH/kg)',
        template=ONP_TEMPLATE,
        height=450
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
    top_species = df.groupby('espece')['volume_kg'].sum().reset_index().sort_values('volume_kg', ascending=False).head(top_n)
    top_species['volume_tonnes'] = top_species['volume_kg'] / 1000
    
    fig = px.bar(
        top_species,
        x='volume_tonnes',
        y='espece',
        orientation='h',
        title=f'Top {top_n} espèces par volume',
        labels={'volume_tonnes': 'Volume Total (Tonnes)', 'espece': 'Espèce'},
        color='volume_kg',
        color_continuous_scale='Greens'
    )
    
    fig.update_layout(
        template=ONP_TEMPLATE,
        height=500,
        showlegend=False
    )
    
    return fig


def plot_port_activity_heatmap(df):
    """
    Crée une heatmap de l'activité par port et mois.
    
    Args:
        df (pd.DataFrame): DataFrame avec 'port', 'date_vente', 'volume_kg'
        
    Returns:
        plotly.graph_objects.Figure: Graphique interactif
    """
    # Créer la colonne mois si elle n'existe pas
    if 'mois' not in df.columns:
        df['mois'] = pd.to_datetime(df['date_vente']).dt.month
    
    # Créer le pivot table
    heatmap_data = df.pivot_table(
        values='volume_kg',
        index='port',
        columns='mois',
        aggfunc='sum',
        fill_value=0
    )
    
    mois_noms = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 
                 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=mois_noms,
        y=heatmap_data.index,
        colorscale='Blues',
        text=np.round(heatmap_data.values / 1000, 1),  # En tonnes
        texttemplate='%{text}T',
        textfont={"size": 10},
        colorbar=dict(title="Volume (kg)")
    ))
    
    fig.update_layout(
        title='Activité des ports par mois',
        xaxis_title='Mois',
        yaxis_title='Port',
        template=ONP_TEMPLATE,
        height=400
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
