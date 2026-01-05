import streamlit as st
import hashlib

# ----------------------------------
# Utilisateurs (POC – remplaçable LDAP/AD)
# ----------------------------------
USERS = {
    "admin": {
        "password": "admin123",
        "role": "admin"
    },
    "superviseur": {
        "password": "super123",
        "role": "superviseur"
    },
    "lecture": {
        "password": "lecture123",
        "role": "lecture"
    }
}

def authenticate():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.sidebar.subheader("🔐 Connexion sécurisée")

    username = st.sidebar.text_input("Utilisateur")
    password = st.sidebar.text_input("Mot de passe", type="password")

    if st.sidebar.button("Connexion"):
        if username in USERS and USERS[username]["password"] == password:
            st.session_state.authenticated = True
            st.session_state.user = username
            st.session_state.role = USERS[username]["role"]
            st.sidebar.success("Connexion réussie")
            return True
        else:
            st.sidebar.error("Accès refusé")

    return False