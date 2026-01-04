# IA de détection des pannes électriques – Sonelgaz

## Objectif
Simulation IA pour :
- détecter anomalies électriques
- classifier types de pannes
- visualiser réseau

## Structure
- `data/` : données simulées
- `models/` : modèles IA (générés automatiquement)
- `scripts/` : génération + entraînement
- `app.py` : dashboard Streamlit

## Déploiement Streamlit
1. Pousser le projet sur GitHub
2. Créer une app sur [Streamlit Cloud](https://streamlit.io/cloud)
3. Fichier principal : `app.py`
4. Branche : `main`
5. Déploiement automatique : les modèles seront générés dans le cloud

## Passage au réel
- Remplacer `generate_data()` par lecture flux SCADA/IoT
- Réentraîner modèles si besoin
- Dashboard reste identique