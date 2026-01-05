"""
Journalisation d'audit des activités Sonelgaz
"""
import datetime
import json
import os
from pathlib import Path

def log_event(user, action, level="INFO", details=None):
    """
    Journalise un événement d'audit
    
    Args:
        user (str): Nom d'utilisateur
        action (str): Action effectuée
        level (str): Niveau de log (INFO, WARNING, ERROR, CRITICAL)
        details (dict): Détails supplémentaires
    """
    # Créer le dossier logs s'il n'existe pas
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Nom du fichier de log avec la date
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"audit_{today}.log"
    
    # Créer l'entrée de log
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    log_entry = {
        "timestamp": timestamp,
        "user": user,
        "level": level,
        "action": action,
        "details": details or {}
    }
    
    # Format lisible pour l'humain
    human_format = f"{timestamp} | {user:15} | {level:8} | {action}"
    if details:
        human_format += f" | {json.dumps(details)}"
    
    # Écrire dans le fichier
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(human_format + "\n")
        
        # Également écrire dans le fichier audit principal
        with open("audit.log", "a", encoding="utf-8") as f:
            f.write(human_format + "\n")
        
        return True
    except Exception as e:
        # Fallback en cas d'erreur d'écriture
        print(f"ERREUR JOURNALISATION: {e}")
        return False

def get_recent_logs(n=50, level=None):
    """
    Récupère les N derniers logs
    
    Args:
        n (int): Nombre de logs à récupérer
        level (str): Filtrer par niveau
    
    Returns:
        list: Liste des logs
    """
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    log_file = Path("logs") / f"audit_{today}.log"
    
    if not log_file.exists():
        return []
    
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        logs = []
        for line in reversed(lines[-n:]):  # Lire à l'envers pour avoir les plus récents
            line = line.strip()
            if not line:
                continue
            
            if level and f"| {level}" not in line:
                continue
            
            logs.append(line)
        
        return logs
    except Exception as e:
        print(f"ERREUR LECTURE LOGS: {e}")
        return []

def log_login_attempt(username, success, ip_address=None, user_agent=None):
    """
    Journalise une tentative de connexion
    
    Args:
        username (str): Nom d'utilisateur
        success (bool): Succès de la tentative
        ip_address (str): Adresse IP
        user_agent (str): User-Agent du navigateur
    """
    action = "Tentative de connexion réussie" if success else "Tentative de connexion échouée"
    details = {"ip": ip_address, "user_agent": user_agent}
    
    log_event(
        username if success else "unknown",
        action,
        "INFO" if success else "WARNING",
        details
    )

def log_data_access(user, data_source, record_count=None):
    """
    Journalise l'accès aux données
    
    Args:
        user (str): Utilisateur
        data_source (str): Source de données
        record_count (int): Nombre d'enregistrements accédés
    """
    details = {"source": data_source}
    if record_count:
        details["records"] = record_count
    
    log_event(user, "Accès aux données", "INFO", details)

def log_model_action(user, action, model_name, details=None):
    """
    Journalise les actions sur les modèles IA
    
    Args:
        user (str): Utilisateur
        action (str): Action (train, predict, evaluate, etc.)
        model_name (str): Nom du modèle
        details (dict): Détails supplémentaires
    """
    action_desc = {
        "train": "Entraînement modèle",
        "predict": "Prédiction modèle",
        "evaluate": "Évaluation modèle",
        "load": "Chargement modèle",
        "save": "Sauvegarde modèle"
    }
    
    log_details = {
        "model": model_name,
        "action": action,
        **(details or {})
    }
    
    log_event(
        user,
        action_desc.get(action, f"Action modèle: {action}"),
        "INFO",
        log_details
    )