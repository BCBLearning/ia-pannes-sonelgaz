import pandas as pd
import joblib
import os
from sklearn.ensemble import IsolationForest, RandomForestClassifier

os.makedirs("models", exist_ok=True)

def train_models(df):
    FEATURES = ["tension","courant","puissance"]

    # Isolation Forest
    iso = IsolationForest(contamination=0.08, random_state=42)
    iso.fit(df[FEATURES])
    joblib.dump(iso, "models/anomaly_detector.pkl")

    # Random Forest pour classification pannes
    df_pannes = df[df["panne"]==1]
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(df_pannes[FEATURES], df_pannes["type_panne"])
    joblib.dump(clf, "models/classifier.pkl")

    return iso, clf

if __name__ == "__main__":
    df = pd.read_csv("data/data.csv")
    train_models(df)