import streamlit as st
import pandas as pd
import yaml
import os
import joblib

from scripts.generate_data import generate_data
from scripts.train_models import train_models
from services.data_preprocessing import preprocess
from services.alert_engine import generate_alerts
from services.scada_connector import get_scada_data

FEATURES = ["tension", "courant", "puissance"]

with open("config.yaml") as f:
    CONFIG = yaml.safe_load(f)

st.set_page_config(
    page_title="IA Pannes Sonelgaz",
    layout="wide"
)

st.title("Détection intelligente des pannes – Sonelgaz")
st.caption("Plateforme IA – Aide à la décision – Lecture seule")

# -------------------------------
# Chargement des données
# -------------------------------
if CONFIG["mode"] == "realtime":
    df = get_scada_data()
    st.success("Mode réel – Données SCADA")
else:
    if not os.path.exists("data/data.csv"):
        df = generate_data()
    else:
        df = pd.read_csv("data/data.csv")
    st.info("Mode démonstration – Données simulées")

df = preprocess(df)

# -------------------------------
# Modèles IA
# -------------------------------
if not os.path.exists("models/anomaly_detector.pkl"):
    iso, clf = train_models(df)
else:
    iso = joblib.load("models/anomaly_detector.pkl")
    clf = joblib.load("models/classifier.pkl")

df["anomalie"] = iso.predict(df[FEATURES])
df["anomalie"] = df["anomalie"].apply(lambda x: 1 if x == -1 else 0)

df["panne_predite"] = "OK"
mask = df["anomalie"] == 1
if mask.any():
    df.loc[mask, "panne_predite"] = clf.predict(df.loc[mask, FEATURES])

# -------------------------------
# Dashboard
# -------------------------------
st.subheader("📊 Dernières mesures")
st.dataframe(df.tail(20), use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.subheader("📍 Répartition par zone")
    st.bar_chart(df["zone"].value_counts())

with col2:
    st.subheader("🚨 Anomalies détectées")
    st.metric("Nombre", int(df["anomalie"].sum()))

st.subheader("🔔 Alertes actives")
alerts = generate_alerts(df)

if alerts.empty:
    st.success("Aucune panne critique détectée")
else:
    st.error("Intervention recommandée")
    st.dataframe(alerts, use_container_width=True)