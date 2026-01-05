"""
Service de visualisation des données
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

class VisualizationService:
    def __init__(self):
        self.colors = {
            "OK": "#2ecc71",
            "Court-circuit": "#e74c3c",
            "Surcharge": "#f39c12",
            "Ligne coupée": "#9b59b6"
        }
    
    def create_timeseries_plot(self, df, time_col="timestamp", value_col="tension"):
        """
        Créer un graphique temporel
        """
        fig = go.Figure()
        
        # Ajouter la courbe principale
        fig.add_trace(go.Scatter(
            x=df[time_col],
            y=df[value_col],
            mode='lines+markers',
            name=value_col,
            line=dict(color='#3498db', width=2)
        ))
        
        # Ajouter les zones d'anomalies
        if "anomalie" in df.columns:
            anomalies = df[df["anomalie"] == 1]
            if not anomalies.empty:
                fig.add_trace(go.Scatter(
                    x=anomalies[time_col],
                    y=anomalies[value_col],
                    mode='markers',
                    name='Anomalies',
                    marker=dict(color='red', size=10, symbol='x')
                ))
        
        fig.update_layout(
            title=f"Évolution de la {value_col} dans le temps",
            xaxis_title="Temps",
            yaxis_title=value_col,
            template="plotly_white",
            hovermode="x unified"
        )
        
        return fig
    
    def create_distribution_plot(self, df, column="tension"):
        """
        Créer un histogramme de distribution
        """
        fig = px.histogram(
            df, 
            x=column,
            nbins=30,
            title=f"Distribution de la {column}",
            color_discrete_sequence=['#3498db']
        )
        
        fig.update_layout(
            xaxis_title=column,
            yaxis_title="Fréquence",
            template="plotly_white"
        )
        
        return fig
    
    def create_zone_comparison(self, df):
        """
        Comparaison entre les zones géographiques
        """
        if "zone" not in df.columns:
            return None
            
        zone_stats = df.groupby("zone").agg({
            "tension": "mean",
            "courant": "mean",
            "anomalie": "sum"
        }).reset_index()
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=zone_stats["zone"],
            y=zone_stats["anomalie"],
            name="Anomalies",
            marker_color="#e74c3c"
        ))
        
        fig.update_layout(
            title="Nombre d'anomalies par zone",
            xaxis_title="Zone",
            yaxis_title="Nombre d'anomalies",
            template="plotly_white"
        )
        
        return fig
    
    def create_panne_type_pie(self, df):
        """
        Diagramme circulaire des types de panne
        """
        if "panne_predite" not in df.columns:
            return None
            
        panne_counts = df["panne_predite"].value_counts()
        
        # Préparation des couleurs
        colors = [self.colors.get(panne_type, "#95a5a6") for panne_type in panne_counts.index]
        
        fig = go.Figure(data=[go.Pie(
            labels=panne_counts.index,
            values=panne_counts.values,
            hole=.3,
            marker_colors=colors
        )])
        
        fig.update_layout(
            title="Répartition des types de panne détectés",
            template="plotly_white"
        )
        
        return fig