"""
Service de prédiction IA en temps réel pour Sonelgaz
"""
import pandas as pd
import joblib
import numpy as np
from datetime import datetime, timedelta
import os

class PredictionService:
    def __init__(self, model_path=None, classifier_path=None):
        """
        Initialisation du service de prédiction
        
        Args:
            model_path (str): Chemin vers le modèle d'anomalies
            classifier_path (str): Chemin vers le modèle de classification
        """
        # Chemins par défaut
        self.anomaly_model_path = model_path or "models/anomaly_detector.pkl"
        self.classifier_path = classifier_path or "models/classifier.pkl"
        
        # Charger les modèles
        self.anomaly_detector = self.load_model(self.anomaly_model_path)
        self.classifier = self.load_model(self.classifier_path)
        
        # Historique des prédictions
        self.predictions_history = []
        self.max_history_size = 1000
        
        # Features utilisées
        self.features = ["tension", "courant", "puissance"]
    
    def load_model(self, model_path):
        """
        Charge un modèle depuis le disque
        """
        try:
            if os.path.exists(model_path):
                return joblib.load(model_path)
            else:
                raise FileNotFoundError(f"Modèle non trouvé: {model_path}")
        except Exception as e:
            print(f"Erreur chargement modèle {model_path}: {e}")
            return None
    
    def predict(self, data_point):
        """
        Effectue une prédiction complète sur un point de données
        
        Args:
            data_point (dict): Point de données avec tension, courant
            
        Returns:
            dict: Résultats de la prédiction
        """
        try:
            # Préparer les features
            features_df = self.prepare_features(data_point)
            
            if features_df is None or self.anomaly_detector is None:
                return self.create_error_result("Modèle non disponible")
            
            # Détection d'anomalie
            anomaly_score = self.anomaly_detector.score_samples(features_df)[0]
            is_anomaly = anomaly_score < -0.5  # Seuil ajustable
            
            # Classification si anomalie
            panne_type = "OK"
            confidence = 0.0
            
            if is_anomaly and self.classifier is not None:
                try:
                    panne_type = self.classifier.predict(features_df)[0]
                    
                    # Calculer la confiance
                    if hasattr(self.classifier, "predict_proba"):
                        probas = self.classifier.predict_proba(features_df)
                        confidence = np.max(probas[0])
                    else:
                        confidence = 0.8  # Valeur par défaut
                except Exception as e:
                    panne_type = "Inconnu"
                    confidence = 0.5
            
            # Créer le résultat
            result = {
                "timestamp": datetime.now(),
                "data_point": data_point,
                "anomaly_score": float(anomaly_score),
                "is_anomaly": bool(is_anomaly),
                "panne_type": panne_type,
                "confidence": float(confidence),
                "status": "success"
            }
            
            # Ajouter à l'historique
            self.add_to_history(result)
            
            return result
            
        except Exception as e:
            return self.create_error_result(f"Erreur prédiction: {str(e)}")
    
    def prepare_features(self, data_point):
        """
        Prépare les features pour la prédiction
        """
        try:
            # Extraire tension et courant
            tension = float(data_point.get("tension", 0))
            courant = float(data_point.get("courant", 0))
            
            # Calculer la puissance
            puissance = tension * courant / 1000
            
            # Créer le DataFrame
            features = pd.DataFrame([{
                "tension": tension,
                "courant": courant,
                "puissance": puissance
            }])
            
            return features[self.features]
            
        except Exception as e:
            print(f"Erreur préparation features: {e}")
            return None
    
    def create_error_result(self, error_message):
        """Crée un résultat d'erreur"""
        return {
            "timestamp": datetime.now(),
            "data_point": {},
            "anomaly_score": 0.0,
            "is_anomaly": False,
            "panne_type": "Erreur",
            "confidence": 0.0,
            "status": "error",
            "error_message": error_message
        }
    
    def add_to_history(self, prediction):
        """Ajoute une prédiction à l'historique"""
        self.predictions_history.append(prediction)
        
        # Limiter la taille de l'historique
        if len(self.predictions_history) > self.max_history_size:
            self.predictions_history = self.predictions_history[-self.max_history_size:]
    
    def get_recent_predictions(self, minutes=60):
        """
        Récupère les prédictions des N dernières minutes
        """
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent = [p for p in self.predictions_history 
                 if p["timestamp"] > cutoff_time and p["status"] == "success"]
        return recent
    
    def get_statistics(self, hours=24):
        """
        Calcule les statistiques sur les prédictions
        """
        recent = self.get_recent_predictions(hours * 60)
        
        if not recent:
            return {
                "total_predictions": 0,
                "anomalies_detected": 0,
                "anomaly_rate": 0.0,
                "panne_types": {},
                "avg_confidence": 0.0
            }
        
        df = pd.DataFrame(recent)
        
        # Compter les types de panne
        panne_counts = df["panne_type"].value_counts().to_dict()
        
        # Calculer les statistiques
        stats = {
            "total_predictions": len(df),
            "anomalies_detected": df["is_anomaly"].sum(),
            "anomaly_rate": df["is_anomaly"].mean(),
            "panne_types": panne_counts,
            "avg_confidence": df["confidence"].mean(),
            "avg_anomaly_score": df["anomaly_score"].mean(),
            "period_hours": hours
        }
        
        return stats
    
    def predict_batch(self, data_frame):
        """
        Prédiction sur un batch de données
        """
        results = []
        
        for _, row in data_frame.iterrows():
            data_point = row.to_dict()
            result = self.predict(data_point)
            results.append(result)
        
        return results