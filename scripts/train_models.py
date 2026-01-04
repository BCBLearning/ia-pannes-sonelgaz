import pandas as pd
import joblib
import os
from sklearn.ensemble import IsolationForest, RandomForestClassifier

FEATURES = ["tension", "courant", "puissance"]

def train_models(df):
    os.makedirs("models", exist_ok=True)

    iso = IsolationForest(contamination=0.08, random_state=42)
    iso.fit(df[FEATURES])
    joblib.dump(iso, "models/anomaly_detector.pkl")

    df_pannes = df[df["panne"] == 1]
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(df_pannes[FEATURES], df_pannes["type_panne"])
    joblib.dump(clf, "models/classifier.pkl")

    return iso, clf