# IA de détection des pannes électriques – Sonelgaz

## Objectif
Simulation IA pour :
- détecter anomalies électriques
- classifier types de pannes
- visualiser réseau

## Structure
- `data/` : données simulées
- `models/` : modèles IA
- `scripts/` : génération + entraînement
- `app.py` : dashboard Streamlit

## Déploiement Streamlit
1. Générer données : `python scripts/generate_data.py`
2. Entraîner modèles : `python scripts/train_models.py`
3. Lancer dashboard : `streamlit run app.py`

## Passage au réel
- Remplacer `generate_data` par flux SCADA
- Réentraîner modèles si besoin
- Dashboard reste identique