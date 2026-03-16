import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from typing import List, Dict, Any, Optional

class DataVisualizer:
    """Composants de visualisation réutilisables pour le frontend HDI."""

    @staticmethod
    def render_time_series(df: pd.DataFrame, title: str, unit: str, source: str, note: Optional[str] = None):
        """Affiche une courbe temporelle avec métadonnées enrichies."""
        fig = px.line(
            df, 
            x="date", 
            y="value", 
            title=f"<b>{title}</b>",
            labels={"value": unit, "date": "Période"},
            template="plotly_white"
        )
        fig.update_traces(line_color="#1e293b", line_width=2)
        fig.update_layout(
            hovermode="x unified",
            xaxis_title="",
            yaxis_title=unit,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Pied de graphique (Métadonnées)
        st.caption(f"**Source :** {source} | **Unité :** {unit}")
        if note:
            with st.expander("Note méthodologique"):
                st.write(note)

    @staticmethod
    def render_comparison(df: pd.DataFrame, title: str, unit: str, source: str):
        """Affiche une comparaison multi-pays."""
        fig = px.line(
            df, 
            x="Date", 
            y="Valeur", 
            color="Pays",
            title=f"<b>{title}</b>",
            labels={"Valeur": unit, "Date": "Période"},
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig.update_layout(hovermode="x unified", legend_title="")
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"**Source :** {source} | **Comparaison régionale**")

    @staticmethod
    def render_summary_table(df: pd.DataFrame):
        """Affiche un tableau synthétique stylisé."""
        st.dataframe(
            df, 
            use_container_width=True,
            column_config={
                "date": "Période",
                "value": st.column_config.NumberColumn("Valeur", format="%.2f"),
                "status": "Statut"
            },
            hide_index=True
        )

    @staticmethod
    def render_map_placeholder():
        """Affiche un placeholder pour les futures cartes géographiques."""
        st.info("📍 Les visualisations géographiques (Heatmaps départementales) seront disponibles dès l'intégration des données IHSI.")
        # Simulation d'une zone vide stylisée
        st.image("https://via.placeholder.com/800x400.png?text=Carte+D%C3%A9partementale+Haiti+(Placeholder)", use_container_width=True)
