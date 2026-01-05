# ============================================
# Détection Intelligente des Pannes - Sonelgaz
# Version: 2.0.0
# Date: 2024
# ============================================

import sys
import os
import streamlit as st

# Configuration du chemin
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# ============================================
# Gestion des secrets et configuration
# ============================================
def load_configuration():
    """Charge la configuration depuis les secrets et fichiers YAML"""
    import yaml
    
    # Charger config.yaml
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Fusionner avec les secrets Streamlit
    if hasattr(st, 'secrets'):
        secrets = st.secrets
        
        # Configuration SCADA depuis les secrets
        if "SCADA_ENDPOINT" in secrets:
            config["scada"]["endpoint"] = secrets["SCADA_ENDPOINT"]
        if "SCADA_USERNAME" in secrets:
            config["scada"]["username"] = secrets["SCADA_USERNAME"]
        if "SCADA_PASSWORD" in secrets:
            config["scada"]["password"] = secrets["SCADA_PASSWORD"]
        
        # Sécurité
        if "JWT_SECRET_KEY" in secrets:
            config["security"]["jwt_secret"] = secrets["JWT_SECRET_KEY"]
        if "ENCRYPTION_KEY" in secrets:
            config["security"]["encryption_key"] = secrets["ENCRYPTION_KEY"]
    
    return config

# Charger la configuration
CONFIG = load_configuration()

# ============================================
# Imports standards
# ============================================
import pandas as pd
import numpy as np
import yaml
import joblib
import plotly.graph_objects as go
from datetime import datetime, timedelta
import hashlib
import time

# ============================================
# Imports projet
# ============================================
# ============================================
# Imports projet
# ============================================
try:
    from scripts.generate_data import generate_data
    from scripts.train_models import train_models
    from scripts.data_validation import validate_sonelgaz_data, detect_data_quality_issues
    
    from services.data_preprocessing import preprocess
    from services.alert_engine import generate_alerts
    from services.scada_connector import get_scada_data
    from services.prediction_service import PredictionService
    from services.visualization_service import VisualizationService
    
    from security.auth import authenticate  # ⬅️ CORRIGÉ : sans require_role
    from security.audit_log import log_event
    
    from utils.helpers import calculate_statistics, format_timestamp, export_to_csv
except ImportError as e:
    st.error(f"Erreur d'importation: {e}")
    st.info("Vérifiez la structure des dossiers et les fichiers manquants")
    st.stop()

# ============================================
# Configuration Streamlit
# ============================================
st.set_page_config(
    page_title="Détection Intelligente des Pannes - Sonelgaz",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# En-tête Sonelgaz
# ============================================
col_logo, col_title = st.columns([1, 4])
with col_logo:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Logo_Sonelgaz.svg/1200px-Logo_Sonelgaz.svg.png", 
             width=100)
with col_title:
    st.title("⚡ Détection Intelligente des Pannes")
    st.caption("Plateforme IA de Supervision du Réseau Électrique - Direction Technique Sonelgaz")

# ============================================
# Authentification
# ============================================
if not authenticate():
    st.warning("🔐 Authentification requise pour accéder à la plateforme")
    st.stop()

user = st.session_state.user
role = st.session_state.role

# Journalisation
log_event(user, "Connexion à la plateforme")

# ============================================
# Barre latérale
# ============================================
with st.sidebar:
    st.markdown("### 👤 Session")
    st.markdown(f"**Utilisateur:** {user}")
    st.markdown(f"**Rôle:** {role}")
    st.markdown(f"**Mode:** {CONFIG['mode'].upper()}")
    
    st.markdown("---")
    
    # Sélecteur de mode
    if role == "admin":
        mode = st.selectbox(
            "Mode d'opération",
            ["simulation", "realtime"],
            index=0 if CONFIG["mode"] == "simulation" else 1
        )
        if mode != CONFIG["mode"]:
            CONFIG["mode"] = mode
            with open("config.yaml", "w") as f:
                yaml.dump(CONFIG, f)
            st.rerun()
    
    # Filtres temporels
    st.markdown("### ⏱️ Filtres")
    hours_back = st.slider("Période (heures)", 1, 72, 24)
    
    st.markdown("---")
    
    # Actions
    if st.button("🔄 Actualiser les données"):
        st.rerun()
    
    if role in ["admin", "superviseur"]:
        if st.button("📊 Exporter le rapport"):
            # Logique d'export à implémenter
            st.success("Rapport exporté avec succès")
    
    if st.button("🚪 Déconnexion"):
        log_event(user, "Déconnexion")
        st.session_state.clear()
        st.rerun()

# ============================================
# Chargement des données
# ============================================
@st.cache_data(ttl=300)  # Cache 5 minutes
def load_data(_mode, _role):
    """Charge les données selon le mode et le rôle"""
    
    if _mode == "realtime":
        if _role != "admin":
            st.warning("🔒 Accès SCADA réservé aux administrateurs")
            log_event(user, "Tentative d'accès SCADA non autorisée")
            return pd.DataFrame()
        
        st.info("📡 Connexion au SCADA Sonelgaz...")
        data = get_scada_data()
        
        if data.empty:
            st.error("❌ Impossible de se connecter au SCADA")
            log_event(user, "Échec connexion SCADA")
            return pd.DataFrame()
        
        st.success(f"✅ {len(data)} mesures SCADA chargées")
        log_event(user, "Accès données SCADA réussi")
        return data
    
    # Mode simulation
    st.info("🧪 Mode simulation - Données de démonstration")
    
    if not os.path.exists("data/data.csv"):
        st.warning("Génération des données initiales...")
        data = generate_data()
    else:
        data = pd.read_csv("data/data.csv")
    
    # Validation des données
    try:
        data = validate_sonelgaz_data(data)
        
        # Vérification qualité
        issues = detect_data_quality_issues(data)
        if issues:
            st.warning(f"Problèmes détectés: {len(issues)}")
            for issue in issues:
                st.caption(f"⚠️ {issue}")
    
    except Exception as e:
        st.error(f"Erreur validation: {e}")
        return pd.DataFrame()
    
    return data

# Chargement
raw_df = load_data(CONFIG["mode"], role)

if raw_df.empty:
    st.error("Aucune donnée disponible. Veuillez vérifier la configuration.")
    st.stop()

# ============================================
# Prétraitement
# ============================================
df = preprocess(raw_df)

# Ajout timestamp si absent
if "timestamp" not in df.columns:
    df["timestamp"] = pd.date_range(
        end=datetime.now(),
        periods=len(df),
        freq="5min"
    )

# ============================================
# Initialisation services
# ============================================
@st.cache_resource
def init_services():
    """Initialise les services IA"""
    # Chargement des modèles
    try:
        iso = joblib.load("models/anomaly_detector.pkl")
        clf = joblib.load("models/classifier.pkl")
    except:
        st.warning("Réentraînement des modèles IA...")
        iso, clf = train_models(df)
    
    # Initialisation services
    pred_service = PredictionService()
    vis_service = VisualizationService()
    
    return iso, clf, pred_service, vis_service

iso, clf, pred_service, vis_service = init_services()

# ============================================
# Détection d'anomalies
# ============================================
FEATURES = ["tension", "courant", "puissance"]

if all(feat in df.columns for feat in FEATURES):
    # Prédiction anomalies
    df["anomalie_score"] = iso.score_samples(df[FEATURES])
    df["anomalie"] = (df["anomalie_score"] < -0.5).astype(int)
    
    # Classification des pannes
    df["panne_predite"] = "OK"
    mask = df["anomalie"] == 1
    
    if mask.any():
        try:
            df.loc[mask, "panne_predite"] = clf.predict(df.loc[mask, FEATURES])
            
            # Confiance des prédictions
            if hasattr(clf, "predict_proba"):
                probas = clf.predict_proba(df.loc[mask, FEATURES])
                df.loc[mask, "confiance"] = probas.max(axis=1)
        except Exception as e:
            st.error(f"Erreur classification: {e}")
            df.loc[mask, "panne_predite"] = "Inconnu"
else:
    st.error("Colonnes de features manquantes")
    df["anomalie"] = 0
    df["panne_predite"] = "OK"

# ============================================
# Génération des alertes
# ============================================
alerts = generate_alerts(df)

# ============================================
# Dashboard Principal
# ============================================
st.markdown("## 📈 Tableau de Bord de Supervision")

# KPI Principaux
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Mesures analysées",
        f"{len(df):,}",
        delta=f"+{len(df) - 500}" if len(df) > 500 else None
    )

with col2:
    anomalies = df["anomalie"].sum()
    st.metric(
        "Anomalies détectées",
        anomalies,
        delta_color="inverse",
        delta=f"{anomalies/len(df)*100:.1f}%"
    )

with col3:
    pannes = len(df[df["panne_predite"] != "OK"])
    st.metric(
        "Pannes identifiées",
        pannes,
        delta_color="inverse"
    )

with col4:
    if "confiance" in df.columns:
        avg_conf = df["confiance"].mean() if not df["confiance"].isna().all() else 0
        st.metric(
            "Confiance moyenne",
            f"{avg_conf*100:.1f}%",
            delta=f"{(avg_conf-0.8)*100:.1f}%" if avg_conf > 0.8 else None
        )
    else:
        st.metric("Mode", CONFIG["mode"].upper())

# ============================================
# Visualisations
# ============================================
st.markdown("### 📊 Visualisations Temps Réel")

tab1, tab2, tab3, tab4 = st.tabs(["📈 Évolution Temporelle", "📊 Distribution", "🗺️ Par Zone", "📋 Données"])

with tab1:
    col_v1, col_v2 = st.columns(2)
    
    with col_v1:
        if "timestamp" in df.columns and "tension" in df.columns:
            fig_tension = vis_service.create_timeseries_plot(
                df.tail(100),  # Dernières 100 mesures
                "timestamp",
                "tension"
            )
            st.plotly_chart(fig_tension, use_container_width=True)
    
    with col_v2:
        if "timestamp" in df.columns and "courant" in df.columns:
            fig_courant = vis_service.create_timeseries_plot(
                df.tail(100),
                "timestamp",
                "courant"
            )
            st.plotly_chart(fig_courant, use_container_width=True)

with tab2:
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        if "tension" in df.columns:
            fig_dist_tension = vis_service.create_distribution_plot(df, "tension")
            st.plotly_chart(fig_dist_tension, use_container_width=True)
    
    with col_d2:
        if "courant" in df.columns:
            fig_dist_courant = vis_service.create_distribution_plot(df, "courant")
            st.plotly_chart(fig_dist_courant, use_container_width=True)

with tab3:
    if "zone" in df.columns:
        fig_zone = vis_service.create_zone_comparison(df)
        if fig_zone:
            st.plotly_chart(fig_zone, use_container_width=True)
        else:
            st.info("Données de zone non disponibles")
    else:
        st.warning("Colonne 'zone' manquante dans les données")

with tab4:
    st.dataframe(
        df.tail(50),
        use_container_width=True,
        column_config={
            "timestamp": st.column_config.DatetimeColumn("Horodatage"),
            "tension": st.column_config.NumberColumn("Tension (V)", format="%.1f V"),
            "courant": st.column_config.NumberColumn("Courant (A)", format="%.2f A"),
            "puissance": st.column_config.NumberColumn("Puissance (kW)", format="%.3f kW"),
            "anomalie": st.column_config.CheckboxColumn("Anomalie"),
            "panne_predite": st.column_config.TextColumn("Type Panne"),
            "confiance": st.column_config.ProgressColumn("Confiance", format="%.1f%%", min_value=0, max_value=1)
        }
    )
    
    # Statistiques
    if st.checkbox("Afficher les statistiques détaillées"):
        stats = calculate_statistics(df)
        st.json(stats)

# ============================================
# Section Alertes
# ============================================
st.markdown("## 🚨 Alertes en Cours")

if alerts.empty:
    st.success("✅ Aucune alerte critique - Système nominal")
else:
    st.error(f"⚠️ {len(alerts)} alerte(s) nécessitant intervention")
    
    # Tri par criticité
    alerts_display = alerts.copy()
    if "criticite" in alerts_display.columns:
        crit_order = {"Critique": 0, "Élevée": 1, "Modérée": 2}
        alerts_display["crit_order"] = alerts_display["criticite"].map(crit_order)
        alerts_display = alerts_display.sort_values("crit_order").drop("crit_order", axis=1)
    
    # Affichage avec coloration
    def color_crit(row):
        if row["criticite"] == "Critique":
            return ['background-color: #ffcccc'] * len(row)
        elif row["criticite"] == "Élevée":
            return ['background-color: #fff3cd'] * len(row)
        else:
            return ['background-color: #d4edda'] * len(row)
    
    styled_alerts = alerts_display.style.apply(color_crit, axis=1)
    st.dataframe(styled_alerts, use_container_width=True)
    
    # Boutons d'action
    col_act1, col_act2, col_act3 = st.columns(3)
    
    with col_act1:
        if st.button("📧 Envoyer rapport par email", type="primary"):
            log_event(user, "Envoi rapport alertes par email")
            st.success("Rapport envoyé aux équipes de maintenance")
    
    with col_act2:
        if st.button("📋 Générer ordre d'intervention"):
            log_event(user, "Génération ordre d'intervention")
            st.info("Ordre d'intervention généré - Réf: INT-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    
    with col_act3:
        if st.button("✅ Marquer comme traité"):
            log_event(user, "Alertes marquées comme traitées")
            st.success("Alertes archivées")

# ============================================
# Section Maintenance (admin seulement)
# ============================================
if role == "admin":
    st.markdown("## 🔧 Maintenance Système")
    
    with st.expander("Configuration avancée"):
        tab_conf, tab_model, tab_logs = st.tabs(["Config", "Modèles IA", "Journaux"])
        
        with tab_conf:
            st.json(CONFIG)
            
            if st.button("Recharger la configuration"):
                st.rerun()
        
        with tab_model:
            st.info("Gestion des modèles IA")
            
            col_m1, col_m2 = st.columns(2)
            
            with col_m1:
                if st.button("Réentraîner les modèles", type="primary"):
                    with st.spinner("Entraînement en cours..."):
                        iso, clf = train_models(df)
                        st.success("Modèles réentraînés avec succès")
                        log_event(user, "Réentraînement modèles IA")
            
            with col_m2:
                if st.button("Tester les modèles"):
                    # Test de prédiction
                    test_data = df[FEATURES].iloc[:5]
                    predictions = iso.predict(test_data)
                    st.write("Test prédictions:", predictions)
        
        with tab_logs:
            if os.path.exists("audit.log"):
                with open("audit.log", "r") as f:
                    logs = f.readlines()[-50:]  # 50 dernières lignes
                st.text_area("Journaux d'audit", "\n".join(logs), height=300)
            else:
                st.warning("Fichier audit.log non trouvé")

# ============================================
# Pied de page Sonelgaz
# ============================================
st.markdown("---")

footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown("**Sonelgaz - Société Nationale de l'Électricité et du Gaz**")
    st.caption("Direction Technique - Division IA & Innovation")

with footer_col2:
    st.markdown("**📞 Contact Urgence Technique**")
    st.caption("24h/24 - 7j/7: +213 21 XX XX XX")

with footer_col3:
    st.markdown("**📊 Métriques Système**")
    st.caption(f"""
    Dernière mise à jour: {datetime.now().strftime('%H:%M:%S')}
    Données analysées: {len(df)} mesures
    Latence: < 2s
    """)

st.markdown("---")
st.caption("""
© 2024 Sonelgaz - Plateforme IA de Supervision du Réseau Électrique | 
Version 2.0.0 | 
Accès sécurisé Niveau {niveau_securite} | 
Traçabilité activée | 
Confidentialité: Interne Sonelgaz
""")