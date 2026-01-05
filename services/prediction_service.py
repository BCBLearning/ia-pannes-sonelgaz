"""
Service de prédiction IA en temps réel
"""
import pandas as pd
import joblib
import numpy as np
from datetime import datetime, timedelta

class PredictionService:
    def __init__(self, model_path="models/anomaly_detector.pkl", classifier_path="models/classifier.pkl"):
        """
        Initialisation du service de prédiction
        """
        self.anomaly_detector = joblib.load(model_path)
        self.classifier = joblib.load(classifier_path)
        self.predictions_history = []
        self.features = ["tension", "courant", "puissance"]
        
    def predict_anomaly(self, data_point):
        """
        Prédire si un point de données est une anomalie
        """
        # Préparation des features
        features_df = pd.DataFrame([data_point])[self.features]
        
        # Détection d'anomalie
        anomaly_pred = self.anomaly_detector.predict(features_df)
        
        # Classification si anomalie
        panne_type = "OK"
        if anomaly_pred[0] == -1:
            panne_type = self.classifier.predict(features_df)[0]
        
        # Stockage de la prédiction
        prediction_record = {
            "timestamp": datetime.now(),
            "data": data_point,
            "anomaly": 1 if anomaly_pred[0] == -1 else 0,
            "panne_type": panne_type,
            "confidence": self._calculate_confidence(features_df, panne_type)
        }
        
        self.predictions_history.append(prediction_record)
        
        return prediction_record
    
    def _calculate_confidence(self, features_df, panne_type):
        """
        Calcul de la confiance de la prédiction
        """
        if panne_type == "OK":
            return 0.95
        
        # Pour les pannes, utiliser les probabilités du classifieur
        try:
            probas = self.classifier.predict_proba(features_df)
            class_idx = list(self.classifier.classes_).index(panne_type)
            return probas[0][class_idx]
        except:
            return 0.7
    
    def get_recent_predictions(self, minutes=60):
        """
        Récupérer les prédictions des dernières minutes
        """
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent = [p for p in self.predictions_history if p["timestamp"] > cutoff_time]
        return recent
    
    def get_statistics(self):
        """
        Statistiques des prédictions
        """
        if not self.predictions_history:
            return {}
        
        df = pd.DataFrame(self.predictions_history)
        
        stats = {
            "total_predictions": len(df),
            "anomalies_detected": df["anomaly"].sum(),
            "anomaly_rate": df["anomaly"].mean(),
            "panne_types": df["panne_type"].value_counts().to_dict(),
            "avg_confidence": df["confidence"].mean()
        }
        
        return stats