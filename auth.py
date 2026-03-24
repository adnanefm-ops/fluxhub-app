import streamlit as st
import base64
import os
from database import SupplyChainDB
from utils import send_email, ADMIN_EMAIL


def get_image_base64(image_path):
    """Lit une image locale et la convertit en Base64 pour l'intégrer au HTML."""
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""


def check_password():
    """Vérifie le mot de passe et retourne le rôle de l'utilisateur."""
    db = SupplyChainDB()
    logo_b64 = get_image_base64("logo.png")

    if logo_b64:
        img_html = f'<img src="data:image/png;base64,{logo_b64}" width="200" style="margin-bottom: 15px; border-radius: 8px;">'
        img_html_sidebar = f'<img src="data:image/png;base64,{logo_b64}" width="90" style="margin-bottom: 12px; border-radius: 8px;">'
    else:
        img_html = '<div style="color: #ef4444; font-size: 10px; margin-bottom:10px;">[Image logo.png introuvable]</div>'
        img_html_sidebar = img_html

    def login_form():
        with st.form("Credentials"):
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 10px;">
                {img_html}
                <div style="color: #94a3b8; font-size: 11px; text-transform: uppercase; letter-spacing: 1px;">Powered by Nouriman ALLAY</div>
                <div style="color: #ffffff; font-weight: 700; font-size: 18px; margin-top: 2px;">Nouriman ALLAY</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<hr style='border-color: #262a36; margin: 15px 0 25px 0;'>", unsafe_allow_html=True)

            username_input = st.text_input("Identifiant").strip().lower()
            password_input = st.text_input("Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter", type="primary", use_container_width=True)

            if submit:
                user_data = db.verify_user(username_input, password_input)

                if user_data:
                    nom, role, statut = user_data
                    if statut == "Actif":
                        st.session_state["password_correct"] = True
                        st.session_state["username"] = nom
                        st.session_state["role"] = role
                        st.rerun()
                    else:
                        st.warning("⏳ Votre compte est toujours en attente de validation par l'administrateur.")
                else:
                    st.error("😕 Identifiant ou mot de passe incorrect")

        # --- NOUVEAU : MOT DE PASSE OUBLIÉ ---
        with st.expander("🔑 Mot de passe oublié ?"):
            with st.form("forgot_password"):
                st.markdown("<p style='font-size: 14px;'>Saisissez l'adresse e-mail associée à votre compte.</p>",
                            unsafe_allow_html=True)
                reset_email = st.text_input("Adresse E-mail")

                btn_reset = st.form_submit_button("Réinitialiser le mot de passe", type="primary",
                                                  use_container_width=True)

                if btn_reset:
                    if not reset_email:
                        st.error("⚠️ Veuillez saisir votre adresse e-mail.")
                    else:
                        success, r_username, r_nom, new_pwd = db.reset_user_password(reset_email)
                        if success:
                            html_reset = f"""
                            <div style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: auto; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px;">
                                <h2 style="color: #f59e0b;">Réinitialisation de mot de passe</h2>
                                <p>Bonjour <strong>{r_nom}</strong>,</p>
                                <p>Suite à votre demande, voici vos nouveaux identifiants temporaires pour vous connecter sur Logiwave :</p>
                                <ul style="background-color: #f8fafc; padding: 15px 30px; border-radius: 6px; list-style-type: square;">
                                    <li><b>Identifiant :</b> {r_username}</li>
                                    <li><b>Nouveau mot de passe :</b> <span style="font-family: monospace; font-weight: bold; font-size: 16px; color:#c026d3;">{new_pwd}</span></li>
                                </ul>
                                <p>Nous vous conseillons de le conserver précieusement.</p>
                            </div>
                            """
                            send_email(reset_email, "[Logiwave] Réinitialisation de votre mot de passe", html_reset)
                            st.success("✅ Un nouveau mot de passe temporaire vous a été envoyé par e-mail.")
                        else:
                            st.error("❌ Aucune adresse e-mail correspondante n'a été trouvée dans notre base.")

        # --- FORMULAIRE DE DEMANDE DE COMPTE ---
        with st.expander("🤝 Devenir partenaire (Demander un compte)"):
            with st.form("request_account"):
                st.markdown("<p style='font-size: 14px;'>Remplissez ce formulaire pour obtenir vos accès.</p>",
                            unsafe_allow_html=True)
                new_nom = st.text_input("Nom de l'entreprise (ex: STEF Rennes)")
                new_email = st.text_input("Adresse E-mail de contact")
                new_password = st.text_input("Choisissez un mot de passe", type="password")
                confirm_password = st.text_input("Confirmez le mot de passe", type="password")  # <-- NOUVEAU CHAMP

                req_submit = st.form_submit_button("Envoyer la demande", type="primary", use_container_width=True)

                if req_submit:
                    if not new_nom or not new_email or not new_password or not confirm_password:
                        st.error("⚠️ Veuillez remplir tous les champs.")
                    elif new_password != confirm_password:  # <-- VÉRIFICATION
                        st.error("❌ Les mots de passe ne correspondent pas.")
                    else:
                        success, req_username = db.create_user_request(new_nom, new_email, new_password)
                        if success:
                            html_admin = f"""
                            <h2 style="color: #3b82f6;">Nouvelle demande d'accès</h2>
                            <p>Le partenaire <b>{new_nom}</b> ({new_email}) souhaite créer un compte sur Logiwave.</p>
                            <p>Veuillez vous connecter à l'interface Administrateur pour approuver ou refuser cette demande.</p>
                            """
                            send_email(ADMIN_EMAIL, f"[Logiwave] Demande de compte : {new_nom}", html_admin)

                            st.success(f"✅ Demande envoyée ! Votre identifiant de connexion sera : **{req_username}**")
                            st.info("Vous recevrez un e-mail dès que l'administrateur aura activé votre compte.")
                        else:
                            st.error("❌ Ce nom d'entreprise est déjà utilisé.")

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
