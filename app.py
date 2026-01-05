# ============================================
# Fix imports Streamlit Cloud / Python path
# ============================================
import sys
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# ============================================
# Imports standards
# ============================================
import streamlit as st
import pandas as pd
import yaml
import joblib

# ============================================
# Imports projet
# ============================================
from scripts.generate_data import generate_data
from scripts.train_models import train_models
from services.data_preprocessing import preprocess
from services.alert_engine import generate_alerts
from services.scada_connector import get_scada_data
from security.auth import authenticate
from security.audit_log import log_event

# ============================================
# Constantes
# ============================================
FEATURES = ["tension", "courant", "puissance"]

# ============================================
# Chargement configuration
# ============================================
with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

# ============================================
# Configuration Streamlit
# ============================================
st.set_page_config(
    page_title="Détection intelligente des pannes – Sonelgaz",
    layout="wide"
)

st.title("Détection intelligente des pannes – Sonelgaz")
st.caption("Plateforme IA – Aide à la décision – Lecture seule sécurisée")

# ============================================
# Authentification & audit
# ============================================
if not authenticate():
    st.stop()

log_event(
    st.session_state.user,
    "Connexion à la plateforme"
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"👤 **Utilisateur :** {st.session_state.user}")
st.sidebar.markdown(f"🎭 **Rôle :** {st.session_state.role}")

# ============================================
# Chargement des données
# ============================================
def load_data():
    # Sécurité : seul l'admin peut activer le mode réel
    if CONFIG["mode"] == "realtime":
        if st.session_state.role != "admin":
            st.warning("🔒 Mode réel réservé à l’administrateur")
            return pd.DataFrame()
        st.success("Mode réel – Données SCADA (lecture seule)")
        log_event(st.session_state.user, "Accès données SCADA")
        return get_scada_data()

    # Mode démonstration (autorisé à tous)
    st.info("Mode démonstration – Données simulées")
    if not os.path.exists("data/data.csv"):
        return generate_data()
    return pd.read_csv("data/data.csv")

raw_df = load_data()

if raw_df.empty:
    st.warning("Aucune donnée disponible")
    st.stop()

df = preprocess(raw_df)

# ============================================
# Chargement / entraînement modèles (ROBUSTE)
# ============================================
def load_or_train_models(dataframe):
    try:
        iso = joblib.load("models/anomaly_detector.pkl")
        clf = joblib.load("models/classifier.pkl")
        return iso, clf
    except Exception:
        st.warning("⚠️ Modèles IA absents ou corrompus – Réentraînement automatique")
        log_event(st.session_state.user, "Réentraînement modèles IA")
        return train_models(dataframe)

iso, clf = load_or_train_models(df)

# ============================================
# IA – Détection anomalies
# ============================================
df["anomalie"] = iso.predict(df[FEATURES])
df["anomalie"] = df["anomalie"].apply(lambda x: 1 if x == -1 else 0)

# ============================================
# IA – Classification des pannes
# ============================================
df["panne_predite"] = "OK"
mask = df["anomalie"] == 1

if mask.any():
    df.loc[mask, "panne_predite"] = clf.predict(
        df.loc[mask, FEATURES]
    )

# ============================================
# Génération alertes métier
# ============================================
alerts = generate_alerts(df)

# ============================================
# Dashboard – Affichage
# ============================================
st.subheader("📊 Dernières mesures analysées")
st.dataframe(df.tail(20), use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Répartition par zone")
    st.bar_chart(df["zone"].value_counts())

with col2:
    st.subheader("🚨 Anomalies détectées")
    st.metric(
        label="Nombre d'anomalies",
        value=int(df["anomalie"].sum())
    )

st.subheader("🔔 Alertes actives")

if alerts.empty:
    st.success("Aucune panne critique détectée")
else:
    st.error("Pannes détectées – Intervention recommandée")
    st.dataframe(alerts, use_container_width=True)

# ============================================
# Footer institutionnel
# ============================================
st.markdown("---")
st.caption(
    "© Sonelgaz – Plateforme IA de supervision du réseau électrique | "
    "Accès sécurisé – Lecture seule – Traçabilité activée"
)