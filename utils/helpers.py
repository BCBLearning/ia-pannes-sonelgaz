"""
Fonctions utilitaires générales
"""
import json
import yaml
import pickle
import hashlib
from datetime import datetime
import pandas as pd

def load_config(config_path="config.yaml"):
    """
    Charger la configuration YAML
    """
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def save_config(config, config_path="config.yaml"):
    """
    Sauvegarder la configuration
    """
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

def generate_data_hash(df):
    """
    Générer un hash des données pour vérifier l'intégrité
    """
    data_str = df.to_json()
    return hashlib.md5(data_str.encode()).hexdigest()

def format_timestamp(timestamp=None):
    """
    Formater un timestamp pour l'affichage
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def calculate_statistics(df, columns=None):
    """
    Calculer les statistiques descriptives
    """
    if columns is None:
        columns = ["tension", "courant", "puissance"]
    
    stats = {}
    for col in columns:
        if col in df.columns:
            stats[col] = {
                "mean": df[col].mean(),
                "std": df[col].std(),
                "min": df[col].min(),
                "max": df[col].max(),
                "median": df[col].median()
            }
    
    return stats

def export_to_csv(df, filename):
    """
    Exporter un DataFrame en CSV avec timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_with_ts = f"{filename}_{timestamp}.csv"
    df.to_csv(filename_with_ts, index=False)
    return filename_with_ts