"""
Tests pour les modèles IA
"""
import pytest
import pandas as pd
import numpy as np
from scripts.train_models import train_models
from sklearn.metrics import accuracy_score, f1_score

def test_model_training():
    """Test d'entraînement des modèles"""
    # Générer des données de test
    zones = ["Nord", "Sud", "Est", "Ouest", "Centre"]
    data = []
    
    for _ in range(500):
        tension = np.random.normal(230, 5)
        courant = np.random.normal(10, 2)
        panne = np.random.rand() < 0.08
        type_panne = "OK"
        
        if panne:
            type_panne = np.random.choice(["Court-circuit", "Surcharge", "Ligne coupée"])
        
        data.append({
            "zone": np.random.choice(zones),
            "tension": tension,
            "courant": courant,
            "puissance": tension * courant / 1000,
            "panne": int(panne),
            "type_panne": type_panne
        })
    
    df = pd.DataFrame(data)
    
    # Entraîner les modèles
    iso_model, clf_model = train_models(df)
    
    # Vérifier que les modèles sont entraînés
    assert iso_model is not None
    assert clf_model is not None
    
    # Tester les prédictions
    test_data = df[["tension", "courant", "puissance"]].head(10)
    predictions = iso_model.predict(test_data)
    
    # Vérifier la forme des prédictions
    assert len(predictions) == 10
    
    print("✅ Test d'entraînement réussi!")

if __name__ == "__main__":
    test_model_training()