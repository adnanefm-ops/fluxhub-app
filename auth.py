import streamlit as st
import base64
import os


def get_image_base64(image_path):
    """Lit une image locale et la convertit en Base64 pour l'intégrer au HTML."""
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""


def check_password():
    """Vérifie le mot de passe et retourne le rôle de l'utilisateur."""

    # --- BASE DE DONNÉES DES COMPTES ---
    USERS = {
        "admin": {"pwd": "admin", "role": "ADMIN", "name": "Hub Logistique"},
        "stefrennes": {"pwd": "carrefour123", "role": "FOURNISSEUR", "name": "STEF Rennes"},
        "florette": {"pwd": "carrefour345", "role": "FOURNISSEUR", "name": "Florette"},
        "fournisseur": {"pwd": "test", "role": "FOURNISSEUR", "name": "Fournisseur Test"}
    }

    # Lecture du logo local
    logo_b64 = get_image_base64("logo.png")

    # --- GESTION DES TAILLES DU LOGO ---
    if logo_b64:
        # Logo de la page d'accueil (Agrandi à 140px)
        img_html = f'<img src="data:image/png;base64,{logo_b64}" width="200" style="margin-bottom: 15px; border-radius: 8px;">'

        # Logo de la barre latérale (Agrandi à 90px)
        img_html_sidebar = f'<img src="data:image/png;base64,{logo_b64}" width="90" style="margin-bottom: 12px; border-radius: 8px;">'
    else:
        img_html = '<div style="color: #ef4444; font-size: 10px; margin-bottom:10px;">[Image logo.png introuvable]</div>'
        img_html_sidebar = img_html

    def login_form():
        with st.form("Credentials"):

            # --- LOGO ET NOM SUR LA PAGE DE CONNEXION ---
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 10px;">
                {img_html}
                <div style="color: #94a3b8; font-size: 11px; text-transform: uppercase; letter-spacing: 1px;">Powered by Nouriman ALLAY</div>
                <div style="color: #ffffff; font-weight: 700; font-size: 18px; margin-top: 2px;">Nouriman ALLAY</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<hr style='border-color: #262a36; margin: 15px 0 25px 0;'>", unsafe_allow_html=True)

            # --- CHAMPS DE CONNEXION ---
            username = st.text_input("Identifiant (ex: stef rennes)").strip().lower()
            password = st.text_input("Mot de passe", type="password")

            submit = st.form_submit_button("Se connecter", type="primary", use_container_width=True)

            if submit:
                if username in USERS and USERS[username]["pwd"] == password:
                    st.session_state["password_correct"] = True
                    st.session_state["username"] = USERS[username]["name"]
                    st.session_state["role"] = USERS[username]["role"]
                    st.rerun()
                else:
                    st.error("😕 Identifiant ou mot de passe incorrect")

    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            login_form()
        return None

    else:
        with st.sidebar:

            # --- LOGO ET NOM DANS LA BARRE LATÉRALE ---
            st.markdown(f"""
            <div style="text-align: center; padding: 15px 10px; margin-bottom: 25px; background-color: rgba(255,255,255,0.02); border-radius: 8px; border: 1px solid #262a36;">
                {img_html_sidebar}
                <div style="color: #94a3b8; font-size: 10px; text-transform: uppercase; letter-spacing: 1px;">Gestion de Cour par</div>
                <div style="color: #3b82f6; font-weight: 700; font-size: 14px; margin-top: 3px;">Nouriman ALLAY</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background-color: rgba(59, 130, 246, 0.1); padding: 15px; border-radius: 8px; border: 1px solid rgba(59, 130, 246, 0.3); text-align: center; margin-bottom: 20px;">
                <span class="material-symbols-outlined" style="font-size: 30px; color: #3b82f6;">account_circle</span><br>
                <span style="color: white; font-weight: 600; font-size: 16px;">{st.session_state['username']}</span><br>
                <span style="color: #94a3b8; font-size: 12px;">{st.session_state['role']}</span>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🚪 Se déconnecter", type="secondary", use_container_width=True):
                st.session_state.clear()
                st.rerun()

        return st.session_state["role"]
