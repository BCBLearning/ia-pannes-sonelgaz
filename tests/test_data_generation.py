"""
Tests pour la génération de données
"""
import pytest
import pandas as pd
from scripts.generate_data import generate_data

def test_generate_data():
    """Test de génération de données"""
    df = generate_data(n_samples=100)
    
    # Vérifier la taille
    assert len(df) == 100
    
    # Vérifier les colonnes
    expected_columns = ["zone", "tension", "courant", "puissance", "panne", "type_panne"]
    for col in expected_columns:
        assert col in df.columns
    
    # Vérifier les plages de valeurs
    assert df["tension"].between(150, 250).all()  # Avec tolérance pour les pannes
    assert df["courant"].between(0, 30).all()
    assert df["puissance"].between(0, 7.5).all()  # 250V * 30A / 1000 = 7.5kW
    
    # Vérifier les types de panne
    valid_panne_types = ["OK", "Court-circuit", "Surcharge", "Ligne coupée"]
    assert df["type_panne"].isin(valid_panne_types).all()

def test_data_distribution():
    """Test de distribution des données"""
    df = generate_data(n_samples=1000)
    
    # Vérifier que nous avons des pannes (probabilité ~8%)
    panne_count = df["panne"].sum()
    assert panne_count > 0
    
    # Vérifier la répartition des zones
    zones = df["zone"].unique()
    assert len(zones) > 0

if __name__ == "__main__":
    test_generate_data()
    test_data_distribution()
    print("✅ Tous les tests passent!")