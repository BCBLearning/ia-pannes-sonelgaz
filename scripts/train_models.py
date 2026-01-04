import pandas as pd
import joblib
import os
from sklearn.ensemble import IsolationForest, RandomForestClassifier

os.makedirs("models", exist_ok=True)

# Charger données simulées
df = pd.read_csv("data/data.csv")
features = ["tension","courant","puissance"]

# Isolation Forest pour anomalies
iso = IsolationForest(contamination=0.08, random_state=42)
iso.fit(df[features])
joblib.dump(iso, "models/anomaly_detector.pkl")

# Random Forest pour classification des pannes
df_pannes = df[df["panne"]==1]
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(df_pannes[features], df_pannes["type_panne"])
joblib.dump(clf, "models/classifier.pkl")

print("✔ Modèles entraînés et sauvegardés")