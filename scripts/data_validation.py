"""
Module de validation des données métiers Sonelgaz
"""
import pandas as pd
import numpy as np
from datetime import datetime

def validate_sonelgaz_data(df):
    """
    Validation des données selon les normes Sonelgaz
    """
    if df.empty:
        raise ValueError("DataFrame vide")
    
    # Vérification des colonnes obligatoires
    required_cols = ["tension", "courant", "zone"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Colonne manquante: {col}")
    
    # Validation des plages de valeurs
    df_valid = df.copy()
    
    # Tension : 180-250V (tolérance réseau)
    mask_tension = (df_valid["tension"] >= 180) & (df_valid["tension"] <= 250)
    if not mask_tension.all():
        df_valid.loc[~mask_tension, "tension"] = np.nan
    
    # Courant : 0-30A (selon disjoncteurs standards)
    mask_courant = (df_valid["courant"] >= 0) & (df_valid["courant"] <= 30)
    if not mask_courant.all():
        df_valid.loc[~mask_courant, "courant"] = np.nan
    
    # Calcul de la puissance
    if "puissance" not in df_valid.columns:
        df_valid["puissance"] = df_valid["tension"] * df_valid["courant"] / 1000
    
    # Ajout timestamp si absent
    if "timestamp" not in df_valid.columns:
        df_valid["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Nettoyage des NaN
    df_valid = df_valid.dropna(subset=["tension", "courant"])
    
    return df_valid

def detect_data_quality_issues(df):
    """
    Détection des problèmes de qualité des données
    """
    issues = []
    
    if df.empty:
        issues.append("Aucune donnée disponible")
        return issues
    
    # Vérification des valeurs manquantes
    missing = df.isnull().sum()
    for col, count in missing.items():
        if count > 0:
            issues.append(f"{col}: {count} valeurs manquantes")
    
    # Vérification de la variance (données constantes ?)
    for col in ["tension", "courant"]:
        if col in df.columns:
            if df[col].std() < 0.1:
                issues.append(f"{col}: variance trop faible ({df[col].std():.2f})")
    
    return issues