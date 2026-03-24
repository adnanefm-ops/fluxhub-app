import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
import os

# --- CONFIGURATION E-MAIL SÉCURISÉE (STREAMLIT SECRETS) ---
# Le bloc try/except évite que l'application plante complètement si tu oublies de configurer un secret
try:
    ADMIN_EMAIL = st.secrets["ADMIN_EMAIL"]
    SENDER_EMAIL = st.secrets["SENDER_EMAIL"]
    SENDER_PASSWORD = st.secrets["SENDER_PASSWORD"]
except KeyError as e:
    st.error(f"⚠️ Erreur de configuration : Le secret {e} est manquant.")
    ADMIN_EMAIL = ""
    SENDER_EMAIL = ""
    SENDER_PASSWORD = ""

def send_email(to_email, subject, html_content):
    """Moteur d'envoi d'e-mail via SMTP."""
    # Sécurité : vérifier que le mot de passe est bien chargé avant d'essayer d'envoyer
    if not SENDER_PASSWORD:
        st.error("Impossible d'envoyer l'e-mail : Mot de passe non configuré dans les secrets.")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg['Subject'] = subject
        msg['From'] = f"Logiwave YMS <{SENDER_EMAIL}>"
        msg['To'] = to_email
        msg.attach(MIMEText(html_content, 'html'))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Erreur d'envoi e-mail : {e}")
        return False
