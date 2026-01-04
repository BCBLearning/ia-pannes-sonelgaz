import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

st.set_page_config(page_title="IA Pannes Sonelgaz", layout="wide")
st.title("Détection intelligente des pannes électriques – Sonelgaz")

DATA_FILE = "data/data.csv"
MODEL_DIR = "models"
FEATURES = ["tension","courant","puissance"]

# --------------------------------------------------
# Charger ou générer données
# --------------------------------------------------
if not os.path.exists(DATA_FILE):
    from scripts.generate_data import generate_data
    generate_data()

df = pd.read_csv(DATA_FILE)

# --------------------------------------------------
# Charger modèles IA
# --------------------------------------------------
try:
    iso = joblib.load(f"{MODEL_DIR}/anomaly_detector.pkl")
    clf = joblib.load(f"{MODEL_DIR}/classifier.pkl")
except FileNotFoundError:
    st.error("❌ Modèles IA manquants. Lancez train_models.py.")
    st.stop()

# --------------------------------------------------
# Détection anomalies
# --------------------------------------------------
df["anomalie"] = iso.predict(df[FEATURES])
df["anomalie"] = df["anomalie"].apply(lambda x: 1 if x==-1 else 0)

df["panne_predite"] = "OK"
mask = df["anomalie"]==1
if mask.any():
    df.loc[mask,"panne_predite"] = clf.predict(df.loc[mask, FEATURES])

# --------------------------------------------------
# Interface Streamlit
# --------------------------------------------------
st.subheader("📊 Dernières mesures analysées")
st.dataframe(df.tail(20), use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Répartition par zone")
    st.bar_chart(df["zone"].value_counts())

with col2:
    st.subheader("🚨 Anomalies détectées")
    st.metric(label="Nombre d'anomalies", value=int(df["anomalie"].sum()))

st.subheader("🔔 Alertes actives")
alertes = df[df["anomalie"]==1][["zone","tension","courant","panne_predite"]]

if alertes.empty:
    st.success("Aucune panne critique détectée")
else:
    st.error("Pannes détectées – intervention recommandée")
    st.dataframe(alertes, use_container_width=True)

st.success("Simulation active – architecture prête pour intégration SCADA")