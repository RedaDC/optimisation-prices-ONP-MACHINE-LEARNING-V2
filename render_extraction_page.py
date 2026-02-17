"""
Fonction de rendu pour la page Extraction 2024-2025
À ajouter dans app_premium.py
"""

def render_page_extraction_2024_2025():
    """Page d'analyse de l'extraction 2024-2025"""
    from extraction_2024_2025 import extract_summary_data, calculate_global_kpis
    from extraction_report_generator import create_extraction_word_report
    import plotly.express as px
    import plotly.graph_objects as go
    
    render_header()
    PremiumComponents.section_header(
        "Analyse Extraction 2024-2025",
        "Analyse Comparative Détaillée des Performances par DR et Espèce",
        "database"
    )
    
    # Charger les données
    with st.spinner("Chargement des données d'extraction..."):
        try:
            df_summary = extract_summary_data()
            kpis = calculate_global_kpis()
        except Exception as e:
            st.error(f"Erreur lors du chargement: {e}")
            return
    
    # KPIs Globaux
    st.markdown("### 📊 Indicateurs Clés")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        PremiumComponents.metric_card(
            "CA 2024",
            f"{kpis['ca_2024_total_mdh']:,.1f} MDH",
            "finance",
            "",
            "blue"
        )
    
    with col2:
        PremiumComponents.metric_card(
            "CA 2025",
            f"{kpis['ca_2025_total_mdh']:,.1f} MDH",
            "finance",
            "",
            "blue"
        )
    
    with col3:
        color = "green" if kpis['var_ca_mdh'] >= 0 else "red"
        PremiumComponents.metric_card(
            "Variation CA",
            f"{kpis['var_ca_mdh']:+,.1f} MDH",
            "trending-up" if kpis['var_ca_mdh'] >= 0 else "trending-down",
            f"{kpis['var_ca_pct']:+.2f}%",
            color
        )
    
    with col4:
        PremiumComponents.metric_card(
            "Espèces",
            f"{int(kpis['nb_especes'])}",
            "fish",
            f"{int(kpis['nb_dr'])} DR",
            "blue"
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Bouton Export Word
    col_export1, col_export2 = st.columns([3, 1])
    with col_export2:
        if st.button("📤 Générer Rapport Word", use_container_width=True):
            with st.spinner("Génération du rapport Word..."):
                try:
                    output_path = create_extraction_word_report()
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="📥 Télécharger le Rapport",
                            data=f,
                            file_name="Rapport_Extraction_2024_2025.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                    st.success("✓ Rapport généré avec succès!")
                except Exception as e:
                    st.error(f"Erreur: {e}")
    
    # Tabs pour différentes analyses
    tab1, tab2, tab3 = st.tabs([
        "📊 Vue d'Ensemble",
        "🏢 Analyse par DR",
        "🐟 Analyse par Espèce"
    ])
    
    with tab1:
        st.markdown("#### Évolution Globale du Chiffre d'Affaires")
        
        # Graphique comparatif CA
        fig_ca = go.Figure(data=[
            go.Bar(
                name='2024',
                x=['CA Total'],
                y=[kpis['ca_2024_total_mdh']],
                marker_color='#3B82F6',
                text=[f"{kpis['ca_2024_total_mdh']:,.1f} MDH"],
                textposition='auto'
            ),
            go.Bar(
                name='2025',
                x=['CA Total'],
                y=[kpis['ca_2025_total_mdh']],
                marker_color='#10B981',
                text=[f"{kpis['ca_2025_total_mdh']:,.1f} MDH"],
                textposition='auto'
            )
        ])
        fig_ca.update_layout(
            title='Comparaison CA 2024 vs 2025',
            yaxis_title='Chiffre d\'Affaires (MDH)',
            barmode='group',
            height=400,
            showlegend=True
        )
        st.plotly_chart(fig_ca, use_container_width=True)
        
        # Graphique volumes
        st.markdown("#### Évolution des Volumes")
        fig_vol = go.Figure(data=[
            go.Bar(
                name='2024',
                x=['Volume Total'],
                y=[kpis['volume_2024_total_t']],
                marker_color='#3B82F6',
                text=[f"{kpis['volume_2024_total_t']:,.0f} T"],
                textposition='auto'
            ),
            go.Bar(
                name='2025',
                x=['Volume Total'],
                y=[kpis['volume_2025_total_t']],
                marker_color='#10B981',
                text=[f"{kpis['volume_2025_total_t']:,.0f} T"],
                textposition='auto'
            )
        ])
        fig_vol.update_layout(
            title='Comparaison Volumes 2024 vs 2025',
            yaxis_title='Volume (Tonnes)',
            barmode='group',
            height=400
        )
        st.plotly_chart(fig_vol, use_container_width=True)
    
    with tab2:
        st.markdown("#### Analyse par Délégation Régionale")
        
        # Agrégation par DR
        df_by_dr = df_summary.groupby('dr').agg({
            'ca_2024_kdh': 'sum',
            'ca_2025_kdh': 'sum',
            'var_ca_kdh': 'sum',
            'volume_2024_t': 'sum',
            'volume_2025_t': 'sum'
        }).reset_index()
        df_by_dr['var_ca_pct'] = (df_by_dr['var_ca_kdh'] / df_by_dr['ca_2024_kdh'] * 100).fillna(0)
        df_by_dr = df_by_dr.sort_values('var_ca_kdh', ascending=False)
        
        # Graphique variations par DR
        fig_dr = px.bar(
            df_by_dr.head(15),
            x='dr',
            y='var_ca_kdh',
            title='Top 15 DR - Variation du CA (KDh)',
            labels={'var_ca_kdh': 'Variation CA (KDh)', 'dr': 'Délégation Régionale'},
            color='var_ca_kdh',
            color_continuous_scale='RdYlGn'
        )
        fig_dr.update_layout(height=500)
        st.plotly_chart(fig_dr, use_container_width=True)
        
        # Tableau détaillé
        st.markdown("#### Tableau Détaillé par DR")
        df_display_dr = df_by_dr.copy()
        df_display_dr['CA 2024 (MDH)'] = df_display_dr['ca_2024_kdh'] / 1000
        df_display_dr['CA 2025 (MDH)'] = df_display_dr['ca_2025_kdh'] / 1000
        df_display_dr['Variation (MDH)'] = df_display_dr['var_ca_kdh'] / 1000
        df_display_dr['Variation (%)'] = df_display_dr['var_ca_pct']
        
        st.dataframe(
            df_display_dr[['dr', 'CA 2024 (MDH)', 'CA 2025 (MDH)', 'Variation (MDH)', 'Variation (%)']].head(20),
            use_container_width=True
        )
    
    with tab3:
        st.markdown("#### Analyse par Espèce")
        
        # Agrégation par espèce
        df_by_espece = df_summary.groupby('espece').agg({
            'ca_2024_kdh': 'sum',
            'ca_2025_kdh': 'sum',
            'var_ca_kdh': 'sum',
            'volume_2024_t': 'sum',
            'volume_2025_t': 'sum'
        }).reset_index()
        df_by_espece['var_ca_pct'] = (df_by_espece['var_ca_kdh'] / df_by_espece['ca_2024_kdh'] * 100).fillna(0)
        df_by_espece = df_by_espece.sort_values('ca_2025_kdh', ascending=False)
        
        # Graphique Top 15 espèces
        fig_esp = px.bar(
            df_by_espece.head(15),
            x='espece',
            y='var_ca_kdh',
            title='Top 15 Espèces - Variation du CA (KDh)',
            labels={'var_ca_kdh': 'Variation CA (KDh)', 'espece': 'Espèce'},
            color='var_ca_kdh',
            color_continuous_scale='RdYlGn'
        )
        fig_esp.update_layout(height=500)
        st.plotly_chart(fig_esp, use_container_width=True)
        
        # Tableau détaillé
        st.markdown("#### Top 20 Espèces par CA 2025")
        df_display_esp = df_by_espece.copy()
        df_display_esp['CA 2024 (MDH)'] = df_display_esp['ca_2024_kdh'] / 1000
        df_display_esp['CA 2025 (MDH)'] = df_display_esp['ca_2025_kdh'] / 1000
        df_display_esp['Variation (MDH)'] = df_display_esp['var_ca_kdh'] / 1000
        df_display_esp['Variation (%)'] = df_display_esp['var_ca_pct']
        
        st.dataframe(
            df_display_esp[['espece', 'CA 2024 (MDH)', 'CA 2025 (MDH)', 'Variation (MDH)', 'Variation (%)']].head(20),
            use_container_width=True
        )
