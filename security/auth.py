"""
Module d'authentification sécurisée Sonelgaz
"""
import streamlit as st
import hashlib
from datetime import datetime, timedelta

# ----------------------------------
# Utilisateurs Sonelgaz (POC – à remplacer par LDAP/AD en production)
# ----------------------------------
USERS = {
    "admin": {
        "password": "admin123",
        "role": "admin",
        "full_name": "Administrateur Système",
        "email": "admin@sonelgaz.dz"
    },
    "superviseur": {
        "password": "super123",
        "role": "superviseur",
        "full_name": "Superviseur Réseau",
        "email": "superviseur@sonelgaz.dz"
    },
    "technicien": {
        "password": "tech123",
        "role": "technicien",
        "full_name": "Technicien Maintenance",
        "email": "technicien@sonelgaz.dz"
    },
    "lecture": {
        "password": "lecture123",
        "role": "lecture",
        "full_name": "Consultant Lecture",
        "email": "consultant@sonelgaz.dz"
    }
}

def hash_password(password):
    """Hachage sécurisé du mot de passe"""
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate():
    """
    Authentification utilisateur avec gestion de session
    """
    # Initialisation de la session
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.login_time = None
        st.session_state.session_timeout = 1800  # 30 minutes en secondes
    
    # Vérifier si la session a expiré
    if (st.session_state.authenticated and 
        st.session_state.login_time and
        datetime.now() - st.session_state.login_time > timedelta(seconds=st.session_state.session_timeout)):
        
        st.session_state.authenticated = False
        st.warning("Session expirée. Veuillez vous reconnecter.")
        return False
    
    # Si déjà authentifié
    if st.session_state.authenticated:
        return True
    
    # Interface de connexion
    st.sidebar.subheader("🔐 Connexion Sonelgaz")
    
    with st.sidebar.form("login_form"):
        username = st.text_input("Identifiant", placeholder="Votre identifiant")
        password = st.text_input("Mot de passe", type="password", placeholder="Votre mot de passe")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            remember = st.checkbox("Se souvenir", value=True)
        with col2:
            submitted = st.form_submit_button("Se connecter", use_container_width=True)
    
    if submitted:
        if not username or not password:
            st.sidebar.error("Identifiant et mot de passe requis")
            return False
        
        if username in USERS and USERS[username]["password"] == password:
            # Authentification réussie
            st.session_state.authenticated = True
            st.session_state.user = username
            st.session_state.role = USERS[username]["role"]
            st.session_state.full_name = USERS[username]["full_name"]
            st.session_state.email = USERS[username]["email"]
            st.session_state.login_time = datetime.now()
            st.session_state.session_timeout = 3600 if remember else 1800
            
            # Journalisation
            from security.audit_log import log_event
            log_event(username, f"Connexion réussie (rôle: {USERS[username]['role']})")
            
            st.sidebar.success(f"Bienvenue {USERS[username]['full_name']}!")
            st.rerun()
            return True
        else:
            st.sidebar.error("❌ Identifiant ou mot de passe incorrect")
            # Journalisation tentative échouée
            try:
                from security.audit_log import log_event
                log_event("unknown", f"Tentative de connexion échouée: {username}")
            except:
                pass
            return False
    
    return False

def logout():
    """Déconnexion sécurisée"""
    if st.session_state.get("authenticated", False):
        user = st.session_state.user
        st.session_state.clear()
        st.success(f"Au revoir {user}!")
        st.rerun()

def require_role(required_role):
    """
    Vérifie si l'utilisateur a le rôle requis
    Usage: if require_role("admin"): ...
    """
    if not st.session_state.get("authenticated", False):
        return False
    
    user_role = st.session_state.get("role", "")
    
    # Hiérarchie des rôles
    role_hierarchy = {
        "lecture": 1,
        "technicien": 2,
        "superviseur": 3,
        "admin": 4
    }
    
    current_level = role_hierarchy.get(user_role, 0)
    required_level = role_hierarchy.get(required_role, 0)
    
    return current_level >= required_level

def get_current_user():
    """Récupère les informations de l'utilisateur connecté"""
    if st.session_state.get("authenticated", False):
        return {
            "username": st.session_state.user,
            "role": st.session_state.role,
            "full_name": st.session_state.full_name,
            "email": st.session_state.email,
            "login_time": st.session_state.login_time
        }
    return None

def check_session_timeout():
    """Vérifie et gère le timeout de session"""
    if not st.session_state.get("authenticated", False):
        return True
    
    login_time = st.session_state.get("login_time")
    timeout = st.session_state.get("session_timeout", 1800)
    
    if login_time and (datetime.now() - login_time).seconds > timeout:
        logout()
        return True
    
    # Avertissement 5 minutes avant expiration
    if login_time and (datetime.now() - login_time).seconds > (timeout - 300):
        remaining = timeout - (datetime.now() - login_time).seconds
        if remaining > 0:
            minutes = remaining // 60
            seconds = remaining % 60
            st.warning(f"⚠️ Votre session expire dans {minutes}min {seconds}sec")
    
    return False