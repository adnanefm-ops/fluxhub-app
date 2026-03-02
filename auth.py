import streamlit as st


def check_password():
    USERS = {"admin": "carrefour2026", "danone": "yaourt123"}

    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
        st.session_state.username = None

    with st.sidebar:
        # Ajout du nom avec un style Premium (Dégradé, ombre subtile, police moderne)
        st.markdown("""
            <div style='text-align: center; margin-bottom: 25px; padding-top: 10px;'>
                <div style='color: #94a3b8; font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 4px;'>
                    Développé par
                </div>
                <div style='
                    background: linear-gradient(90deg, #60a5fa, #3b82f6, #93c5fd);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    font-size: 24px; 
                    font-weight: 800; 
                    letter-spacing: 0.5px; 
                    margin-top: 2px;
                    font-family: "Inter", sans-serif;
                    text-shadow: 0px 4px 15px rgba(59, 130, 246, 0.25);
                '>
                    Nouriman ALLAY
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Centrage parfait du logo (Correction du warning avec use_container_width=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("https://upload.wikimedia.org/wikipedia/fr/3/3b/Logo_Carrefour.svg", use_container_width=True)

        st.markdown("<h2 style='text-align: center; color: white; margin-top: 10px; font-size: 24px;'>Connexion</h2>",
                    unsafe_allow_html=True)

        if not st.session_state.user_role:
            u = st.text_input("Identifiant")
            p = st.text_input("Mot de passe", type="password")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Se connecter", type="primary", use_container_width=True):
                if u in USERS and USERS[u] == p:
                    st.session_state.username = u
                    st.session_state.user_role = "ADMIN" if u == "admin" else "FOURNISSEUR"
                    st.rerun()
                else:
                    st.error("Identifiants incorrects")
            return None
        else:
            st.success(f"Connecté: {st.session_state.username.capitalize()}")
            if st.button("Déconnexion", type="secondary", use_container_width=True):
                st.session_state.user_role = None
                st.rerun()
            return st.session_state.user_role