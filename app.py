import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, time, timedelta
import uuid

# --- IMPORTATIONS LOCALES ---
from database import SupplyChainDB
from auth import check_password

# =====================================================================
# 1. CONFIGURATION DE L'APPLICATION
# =====================================================================
st.set_page_config(
    page_title="YMS • Carrefour Supply",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Constantes Globales
LISTE_QUAIS = ["Q4", "Q5", "Q6", "Q7"]
TEMPS_DECHARGEMENT_MIN = 45

# =====================================================================
# 2. CSS "MIDNIGHT OPS V21" (Cache en constante pour la performance)
# =====================================================================
CSS_STYLE = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400&display=swap');

    :root {
        --bg-dark: #0f1116; --card-bg: #151922; --border-color: #262a36; --input-bg: #1a1e29;
        --text-primary: #ffffff; --text-secondary: #cbd5e1;
        --c-green: #10b981; --c-blue: #3b82f6; --c-yellow: #f59e0b; --c-red: #ef4444;         
    }

    /* GLOBAL RESET */
    .stApp { background-color: var(--bg-dark); font-family: 'Inter', sans-serif; color: var(--text-primary) !important; }
    p, span, div { color: var(--text-primary); }
    h1, h2, h3 { color: #ffffff !important; font-weight: 700; letter-spacing: -0.5px; }
    h4 { color: var(--c-blue) !important; font-weight: 600; margin-top: 15px !important; margin-bottom: 10px !important; }
    label { color: #ffffff !important; font-weight: 600 !important; font-size: 14px !important; }
    .st-emotion-cache-1wivap2 { color: var(--text-secondary) !important; }
    [data-testid="InputInstructions"] { display: none !important; } 

    /* SIDEBAR */
    [data-testid="stSidebar"] { background-color: var(--card-bg) !important; border-right: 1px solid var(--border-color) !important; }
    [data-testid="stSidebar"] * { color: #ffffff !important; }

    /* BOUTONS */
    button[kind="primary"] { background-color: var(--c-blue) !important; color: white !important; border: none !important; border-radius: 6px !important; font-weight: 600 !important; }
    button[kind="primary"]:hover { background-color: #2563eb !important; }
    button[kind="secondary"] { background-color: rgba(239, 68, 68, 0.1) !important; color: var(--c-red) !important; border: 1px solid var(--c-red) !important; border-radius: 6px !important; font-weight: 600 !important; }
    button[kind="secondary"]:hover { background-color: rgba(239, 68, 68, 0.2) !important; }

    /* EXPANDER */
    [data-testid="stExpander"] { background-color: var(--card-bg) !important; border-radius: 8px !important; border: 1px solid var(--border-color) !important; overflow: hidden; }
    [data-testid="stExpander"] details, [data-testid="stExpander"] summary, [data-testid="stExpanderDetails"] { background-color: var(--card-bg) !important; }
    [data-testid="stExpander"] summary:hover { background-color: var(--card-bg) !important; color: var(--c-blue) !important; }
    [data-testid="stExpander"] div[data-testid="stText"] { background-color: transparent !important; }

    /* INPUTS & OEIL MOT DE PASSE */
    .stTextInput input, .stNumberInput input, .stDateInput input, textarea, input[type="time"] { 
        background-color: var(--input-bg) !important; border: 1px solid #374151 !important; color: #ffffff !important; border-radius: 6px !important; 
    }
    div[data-baseweb="input"] { background-color: var(--input-bg) !important; border-radius: 6px !important; }
    div[data-baseweb="input"] > div { background-color: transparent !important; }
    div[data-baseweb="input"] button { background-color: transparent !important; }
    div[data-baseweb="input"] button svg { fill: #94a3b8 !important; } 
    div[data-baseweb="input"] button:hover svg { fill: #ffffff !important; } 

    /* CALENDRIER TRANSPARENT */
    div[data-baseweb="calendar"] { background-color: var(--card-bg) !important; border: 1px solid var(--border-color) !important; border-radius: 8px !important; padding: 5px !important; }
    div[data-baseweb="calendar"] [role="gridcell"], div[data-baseweb="calendar"] [role="columnheader"], div[data-baseweb="calendar"] [role="rowheader"] { background-color: transparent !important; color: #ffffff !important; }
    div[data-baseweb="calendar"] [role="gridcell"] *:hover { background-color: transparent !important; color: #ffffff !important; }
    div[data-baseweb="calendar"] [role="gridcell"] > div:hover { background-color: rgba(59, 130, 246, 0.4) !important; border-radius: 50% !important; }
    div[data-baseweb="calendar"] div[aria-selected="true"], div[data-baseweb="calendar"] div[aria-selected="true"] * { background-color: var(--c-blue) !important; color: white !important; font-weight: bold !important; border-radius: 50% !important; }
    div[data-baseweb="calendar"] [role="button"]:hover { background-color: transparent !important; color: var(--c-blue) !important; }

    /* MENUS DÉROULANTS */
    div[data-baseweb="select"] > div { background-color: var(--input-bg) !important; border: 1px solid #374151 !important; color: #ffffff !important; border-radius: 6px !important; }
    div[data-baseweb="select"] div[data-baseweb="base-input"] { color: #ffffff !important; }
    div[data-baseweb="select"] span { color: #ffffff !important; font-weight: 500 !important; }
    div[data-baseweb="select"] svg { fill: #ffffff !important; }
    ul[data-baseweb="menu"], div[role="listbox"] { background-color: #1a1e29 !important; border: 1px solid var(--c-blue) !important; }
    li[data-baseweb="option"], li[role="option"] { color: #ffffff !important; background-color: #1a1e29 !important; }
    li[data-baseweb="option"]:hover, li[role="option"]:hover, li[aria-selected="true"] { background-color: #3b82f6 !important; color: white !important; }
    span[data-baseweb="tag"] { background-color: var(--c-blue) !important; color: white !important; }

    /* ONGLETS (TABS) ADMIN */
    button[data-baseweb="tab"] { background-color: transparent !important; }
    button[data-baseweb="tab"] p { color: #94a3b8 !important; font-weight: 600; font-size: 16px; }
    button[data-baseweb="tab"][aria-selected="true"] p { color: var(--c-blue) !important; }
    button[data-baseweb="tab"][aria-selected="true"] { border-bottom-color: var(--c-blue) !important; }

    /* CARTES STATUT */
    .status-card { background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 10px; padding: 15px; margin-bottom: 12px; position: relative; transition: transform 0.2s; }
    .status-card:hover { transform: translateY(-2px); border-color: #475569; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
    .card-header { display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px; }
    .card-id { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--text-secondary); opacity: 0.8; }
    .card-title { font-weight: 700; color: #ffffff; font-size: 16px; margin-bottom: 4px; }
    .card-meta { font-size: 13px; color: #cbd5e1; display: flex; gap: 15px; align-items: center; font-weight: 500; }

    .border-green { border-left: 4px solid var(--c-green) !important; }
    .border-blue { border-left: 4px solid var(--c-blue) !important; }
    .border-yellow { border-left: 4px solid var(--c-yellow) !important; }
    .border-red { border-left: 4px solid var(--c-red) !important; }
    .text-green { color: var(--c-green) !important; } .text-blue { color: var(--c-blue) !important; } .text-yellow { color: var(--c-yellow) !important; } .text-red { color: var(--c-red) !important; }

    .js-plotly-plot .plotly .modebar { opacity: 0.2 !important; }
    .js-plotly-plot .plotly .modebar:hover { opacity: 1 !important; }
    </style>
"""
st.markdown(CSS_STYLE, unsafe_allow_html=True)


# =====================================================================
# 3. INITIALISATION ET SÉCURITÉ
# =====================================================================
@st.cache_resource
def get_db():
    return SupplyChainDB()


db = get_db()
role = check_password()

if role is None:
    st.markdown("<br><br><br><center style='color:#94a3b8'>🔐 <i>Accès sécurisé. Veuillez vous connecter.</i></center>",
                unsafe_allow_html=True)
    st.stop()


# =====================================================================
# 4. FONCTIONS UTILITAIRES (HELPERS) OPTIMISÉES
# =====================================================================
def get_time_window(heure_str):
    """Calcule proprement le créneau de 45 minutes et renvoie les formats utiles."""
    h_str = str(heure_str)[:5]
    try:
        start_dt = datetime.strptime(h_str, "%H:%M")
        end_dt = start_dt + timedelta(minutes=TEMPS_DECHARGEMENT_MIN)
        return h_str, end_dt.strftime("%H:%M"), start_dt, end_dt
    except:
        # Fallback de sécurité si erreur de parsing
        return h_str, h_str, datetime.now(), datetime.now()


def parse_date(date_val, format_fr=False):
    """Parse la date proprement et évite les plantages."""
    if pd.isna(date_val): return "N/A"
    try:
        dt_obj = pd.to_datetime(date_val)
        return dt_obj.strftime('%d/%m/%Y') if format_fr else dt_obj.strftime('%Y-%m-%d')
    except:
        return str(date_val).split(" ")[0]


def get_next_available_time(df, target_date, quai, proposed_start_time):
    """Vérifie intelligemment les conflits sur un quai (Version vectorisée ultra-rapide)."""
    # Filtrage direct avec Pandas pour gagner du temps
    df_valid = df[(df['statut'] == 'Validé') & (df['quai'] == quai)].copy()
    if df_valid.empty: return None

    # Ajout d'une colonne de date pure pour le filtre
    df_valid['date_only'] = pd.to_datetime(df_valid['date_prevue']).dt.date
    df_day = df_valid[df_valid['date_only'] == target_date]

    if df_day.empty: return None

    intervals = []
    proposed_start_dt = datetime.combine(target_date, proposed_start_time)
    proposed_end_dt = proposed_start_dt + timedelta(minutes=TEMPS_DECHARGEMENT_MIN)

    # Boucle rapide via to_dict('records')
    for r in df_day.to_dict('records'):
        _, _, s_t, e_t = get_time_window(r['heure_prevue'])
        s_dt = datetime.combine(target_date, s_t.time())
        intervals.append((s_dt, s_dt + timedelta(minutes=TEMPS_DECHARGEMENT_MIN)))

    intervals.sort(key=lambda x: x[0])

    conflict = False
    for s, e in intervals:
        if proposed_start_dt < e and proposed_end_dt > s:
            conflict = True
            break

    if not conflict: return None

    candidate_time = proposed_start_dt
    for s, e in intervals:
        candidate_end = candidate_time + timedelta(minutes=TEMPS_DECHARGEMENT_MIN)
        if candidate_time < e and candidate_end > s:
            candidate_time = e

    return candidate_time


def supplier_card_html(row):
    """Génère le HTML de la carte fournisseur avec un rendu haute performance."""
    config = {
        "Validé": {"class": "border-green", "icon": "check_circle", "icon_color": "text-green",
                   "status_text": "Confirmé"},
        "Refusé": {"class": "border-red", "icon": "cancel", "icon_color": "text-red", "status_text": "Refusé"},
        "En attente": {"class": "border-yellow", "icon": "hourglass_top", "icon_color": "text-yellow",
                       "status_text": "En attente"},
        "Contre-Proposition": {"class": "border-blue", "icon": "swap_horiz", "icon_color": "text-blue",
                               "status_text": "Action Requise"}
    }
    s = config.get(row['statut'], config["En attente"])
    date_str = parse_date(row['date_prevue'])
    h_start, h_end, _, _ = get_time_window(row['heure_prevue'])
    time_display = f"{h_start} - {h_end}"
    is_modified = row.get('est_modifie', False) in [1, True, "1", "true", "True"]

    context_html = ""
    if row['statut'] == "Validé":
        quai = row['quai'] if row['quai'] not in ['Non assigné', 'En attente Q.', 'TBD'] else 'TBD'
        context_html = f"<div style='margin-top:8px; font-size:14px; font-weight: 600; color:#10b981; display:flex; align-items:center; gap:5px;'><span class='material-symbols-outlined' style='font-size:18px;'>location_on</span> Quai assigné : <b>{quai}</b></div>"

        if is_modified:
            s['status_text'] = "Confirmé (Ajusté)"
            context_html += f"""
            <div style="margin-top: 12px; padding: 12px; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 6px; display: flex; align-items: start; gap: 8px;">
                <span class="material-symbols-outlined" style="color: #f59e0b; font-size: 20px;">info</span>
                <div>
                    <div style="color: #fcd34d; font-weight: 700; font-size: 14px; margin-bottom: 2px;">Horaire ajusté par le Hub</div>
                    <div style="color: #e2e8f0; font-size: 13px;">Votre créneau a été décalé. Le nouveau créneau est de <b style="color:white; font-size: 14px;">{time_display}</b>.</div>
                </div>
            </div>
            """

    elif row['statut'] == "Refusé":
        msg = row['message_sc'] if row['message_sc'] else "Non spécifié"
        context_html = f"<div style='margin-top:8px; font-size:14px; font-weight: 600; color:#ef4444;'>🛑 Motif : {msg}</div>"

    return f"""
    <div class="status-card {s['class']}">
        <div class="card-header">
            <div><div class="card-id">{row['id']}</div><div class="card-title">{row['categorie']}</div></div>
            <div style="text-align:right;"><span class="material-symbols-outlined {s['icon_color']}">{s['icon']}</span><div style="font-size:12px; font-weight:700;" class="{s['icon_color']}">{s['status_text']}</div></div>
        </div>
        <div class="card-meta"><span>📅 {date_str}</span><span>⏰ {time_display}</span><span>📦 {row['palettes']} Pal.</span></div>
        {context_html}
    </div>
    """


# =====================================================================
# 5. VUE FOURNISSEUR (PORTAIL PARTENAIRE)
# =====================================================================
if role == "FOURNISSEUR":
    st.markdown(
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />',
        unsafe_allow_html=True)

    c_title, c_act = st.columns([6, 1])
    c_title.markdown(
        f"## 👋 Portail Partenaire : <span style='color: #3b82f6;'>{st.session_state.username.capitalize()}</span>",
        unsafe_allow_html=True)
    if c_act.button("🔄 Actualiser", type="primary", use_container_width=True, key="refresh_supplier"):
        st.rerun()

    with st.expander("📦 Enregistrer une expédition", expanded=True):
        with st.form("form_fournisseur"):
            st.markdown("#### Informations Générales")
            c1, c2, c3 = st.columns(3)
            date_f = c1.date_input("Date de livraison")
            heure_f = c2.time_input("Heure souhaitée d'arrivée", datetime.strptime("08:00", "%H:%M").time())
            cat = c3.selectbox("Famille", ["Frais (0-4°C)", "Surgelés", "Epicerie", "Liquides"])

            st.markdown("#### Détails du Transport")
            c4, c5 = st.columns(2)
            transporteur = c4.text_input("Transporteur (ex: STEF, XPO...)")
            email_f = c5.text_input("E-mail de l'utilisateur", "logistics@supplier.com")

            c6, c7, c8 = st.columns(3)
            nom_chauffeur = c6.text_input("Nom du chauffeur")
            tel_f = c7.text_input("N° portable du chauffeur")
            immatriculation = c8.text_input("N° d'immatriculation")

            st.markdown("#### Marchandise & Notes")
            c9, c10 = st.columns(2)
            pal = c9.number_input("Palettes", min_value=1, max_value=33, value=26)
            colis = c10.number_input("Colis", min_value=0, value=0)

            commentaire = st.text_area("Commentaire (optionnel)",
                                       placeholder="Instructions spécifiques, références de commande...")
            st.info(
                "⏱️ Note : Le temps de déchargement au quai est fixé à un forfait de 45 minutes après l'arrivée du camion.")

            if st.form_submit_button("Transmettre la demande", type="primary", use_container_width=True):
                new_id = f"REQ-{str(uuid.uuid4())[:5].upper()}"
                db.create_demande(new_id, st.session_state.username.capitalize(), cat, pal, colis, date_f,
                                  str(heure_f)[:5], email_f, tel_f, transporteur, nom_chauffeur, immatriculation,
                                  commentaire)
                st.success("Demande transmise au hub logistique avec succès !")
                st.rerun()

    st.markdown("### 📋 Mes Livraisons")
    df = db.get_all()
    if not df.empty:
        mon_df = df[df['fournisseur'] == st.session_state.username.capitalize()]
        sort_col = 'created_at' if 'created_at' in mon_df.columns else 'date_prevue'
        # Utilisation de to_dict pour des performances optimales
        for row in mon_df.sort_values(by=sort_col, ascending=False).to_dict('records'):
            st.markdown(supplier_card_html(row), unsafe_allow_html=True)
            if row['statut'] == "Contre-Proposition":
                col_btn1, col_btn2, _ = st.columns([1, 1, 6])
                with col_btn1:
                    if st.button("✅ Accepter", key=f"acc_{row['id']}", type="primary"):
                        db.update_statut(row['id'], "Validé", quai="En attente Q.", msg="Accord Fournisseur",
                                         est_modifie=True)
                        st.rerun()
                with col_btn2:
                    if st.button("❌ Refuser", key=f"dec_{row['id']}", type="secondary"):
                        db.update_statut(row['id'], "Refusé", msg="Refus Fournisseur")
                        st.rerun()

# =====================================================================
# 6. VUE ADMIN (HUB LOGISTIQUE)
# =====================================================================
elif role == "ADMIN":
    st.markdown(
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" />',
        unsafe_allow_html=True)

    c_title, c_act = st.columns([6, 1])
    c_title.markdown("## 🏭 Gestion de cour (YMS)")
    if c_act.button("🔄 Actualiser", type="primary", use_container_width=True, key="refresh_admin"):
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    tabs = st.tabs(["📥 Boîte de réception", "🏢 Gestion des Quais", "📅 Planning Gantt"])
    df = db.get_all()

    # --- TAB 1: INBOX ---
    with tabs[0]:
        st.markdown("#### 📥 Flux Entrant")
        to_do_df = df[df['statut'] == "En attente"] if not df.empty else pd.DataFrame()

        if to_do_df.empty:
            st.info("Aucune demande en attente pour le moment.")
        else:
            # Itération hyper-rapide
            for row in to_do_df.to_dict('records'):
                date_inbox = parse_date(row['date_prevue'], format_fr=True)
                h_start, h_end, start_t_inbox, _ = get_time_window(row['heure_prevue'])
                time_display_inbox = f"{h_start} à {h_end}"
                transp_name = f" • {row['transporteur']}" if pd.notna(row.get('transporteur')) and row[
                    'transporteur'] else ""

                with st.expander(f"📦 {row['fournisseur']} • Prévu le {date_inbox} de {time_display_inbox}{transp_name}",
                                 expanded=True):
                    st.markdown(f"""
                    <div style="font-size: 14px; color: #ffffff; margin-bottom: 12px; line-height: 1.6;">
                        <b>👤 Chauffeur :</b> <span style="color:#cbd5e1;">{row.get('nom_chauffeur', 'N/A')}</span> | <b>📞 Tél :</b> <span style="color:#cbd5e1;">{row.get('telephone', 'N/A')}</span><br>
                        <b>🚛 Immatriculation :</b> <span style="color:#cbd5e1;">{row.get('immatriculation', 'N/A')}</span><br>
                        <b>📦 Marchandise :</b> <span style="color:#cbd5e1;">{row.get('palettes', 0)} Palettes | {row.get('colis', 0)} Colis | Famille : {row.get('categorie', 'N/A')}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    if pd.notna(row.get('commentaire')) and row['commentaire']:
                        st.info(f"📝 Note du fournisseur : {row['commentaire']}")

                    st.markdown("---")
                    msg_placeholder = st.empty()

                    c1, c2 = st.columns(2)
                    quai = c1.selectbox("Assigner un Quai", LISTE_QUAIS, key=f"q_{row['id']}")
                    h_edit = c2.time_input("Heure d'arrivée", value=start_t_inbox.time(), step=timedelta(minutes=15),
                                           key=f"h_{row['id']}")

                    b1, b2, b3 = st.columns([1, 1, 2])

                    if b1.button("✅ Valider l'accès", key=f"v_{row['id']}", type="primary", use_container_width=True):
                        target_date = pd.to_datetime(row['date_prevue']).date() if pd.notna(
                            row['date_prevue']) else None

                        if target_date:
                            next_avail_dt = get_next_available_time(df, target_date, quai, h_edit)

                            if next_avail_dt:
                                msg_placeholder.markdown(f"""
                                <div style="background-color: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.5); border-radius: 6px; padding: 12px; margin-bottom: 15px; display: flex; align-items: start; gap: 10px;">
                                    <span class="material-symbols-outlined" style="color: #ef4444; font-size: 20px;">error</span>
                                    <div>
                                        <div style="color: #fca5a5; font-weight: 700; font-size: 14px; margin-bottom: 2px;">Quai indisponible !</div>
                                        <div style="color: #e2e8f0; font-size: 13px;">Le <b>{quai}</b> est déjà occupé. Il sera libre à partir de <b style="color:white; font-size: 14px;">{next_avail_dt.strftime('%H:%M')}</b>.</div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                is_mod = str(h_edit)[:5] != str(row['heure_prevue'])[:5]
                                db.update_statut(row['id'], "Validé", quai, nouvelle_heure=str(h_edit)[:5],
                                                 est_modifie=is_mod)
                                st.rerun()

                    if b2.button("❌ Refuser", key=f"r_{row['id']}", type="secondary", use_container_width=True):
                        db.update_statut(row['id'], "Refusé")
                        st.rerun()

    # --- TAB 2: GESTION DES QUAIS ---
    with tabs[1]:
        st.markdown("#### 🏢 Opérations Quotidiennes (Vue par Quai)")
        date_gestion = st.date_input("Sélectionner la date d'opération", datetime.now(), key="date_gestion")

        if df.empty:
            st.info("La base de données est vide.")
        else:
            # Filtrage optimisé
            df_date = df[(df['statut'] == 'Validé') & (
                        pd.to_datetime(df['date_prevue']).dt.date == pd.to_datetime(date_gestion).date())]

            cols = st.columns(4)
            for i, quai in enumerate(LISTE_QUAIS):
                with cols[i]:
                    st.markdown(f"""
                    <div style="background-color: #1e293b; padding: 12px; border-radius: 8px; text-align: center; border-bottom: 4px solid var(--c-blue); margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                        <h3 style="margin: 0; color: white; font-size: 20px; font-weight: 800; letter-spacing: 1px;">{quai}</h3>
                    </div>
                    """, unsafe_allow_html=True)

                    df_quai = df_date[df_date['quai'] == quai]

                    if df_quai.empty:
                        st.markdown("""
                        <div style='text-align:center; padding: 20px; background: rgba(255,255,255,0.02); border: 1px dashed #374151; border-radius: 8px;'>
                            <span class='material-symbols-outlined' style='color:#475569; font-size: 30px;'>deck</span><br>
                            <span style='color:#64748b; font-size:14px; font-weight: 500;'>Quai Libre</span>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        for row in df_quai.sort_values(by='heure_prevue').to_dict('records'):
                            h_start, h_end, _, _ = get_time_window(row['heure_prevue'])

                            st.markdown(f"""
                            <div class="status-card" style="padding: 12px; border-left: 4px solid var(--c-blue); margin-bottom: 10px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                    <div style="color:var(--c-blue); font-weight:700; font-size:14px; display:flex; align-items:center; gap:5px; background: rgba(59, 130, 246, 0.1); padding: 3px 8px; border-radius: 4px;">
                                        <span class="material-symbols-outlined" style="font-size:16px;">schedule</span> {h_start} - {h_end}
                                    </div>
                                </div>
                                <div style="color:white; font-weight:800; font-size:15px; margin-bottom: 8px; letter-spacing: 0.5px;">{row['fournisseur']}</div>
                                <div style="color:#cbd5e1; font-size:12px; display:flex; flex-direction:column; gap:4px; font-weight: 500;">
                                    <span style="display:flex; align-items:center; gap:6px;"><span class="material-symbols-outlined" style="font-size:14px; color:#94a3b8;">inventory_2</span> {row['palettes']} Pal. | {row['colis']} Colis</span>
                                    <span style="display:flex; align-items:center; gap:6px;"><span class="material-symbols-outlined" style="font-size:14px; color:#94a3b8;">local_shipping</span> {row['transporteur'] if pd.notna(row['transporteur']) and row['transporteur'] else 'N/A'}</span>
                                    <span style="display:flex; align-items:center; gap:6px;"><span class="material-symbols-outlined" style="font-size:14px; color:#94a3b8;">pin</span> {row['immatriculation'] if pd.notna(row['immatriculation']) and row['immatriculation'] else 'N/A'}</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

    # --- TAB 3: PLANNING GANTT ---
    with tabs[2]:
        st.markdown("#### 📅 Séquencement Temporel (Gantt)")
        c_filt1, c_filt2 = st.columns([1, 3])
        gantt_date = c_filt1.date_input("Sélectionner la date", datetime.now(), key="gantt_date_gantt")

        if df.empty:
            st.info("La base de données est vide.")
        else:
            options_filtre_quai = ["Tout"] + LISTE_QUAIS
            quais_selected = c_filt2.multiselect("Filtrer par Quai", options_filtre_quai, default=["Tout"],
                                                 key="gantt_quai_filter")

            gantt_df = df[(df['statut'] == 'Validé') & (
                        pd.to_datetime(df['date_prevue']).dt.date == pd.to_datetime(gantt_date).date())].copy()

            if not gantt_df.empty:
                if "Tout" not in quais_selected and len(quais_selected) > 0:
                    gantt_df = gantt_df[gantt_df['quai'].isin(quais_selected)]
                    y_axis_order = list(reversed(quais_selected))
                else:
                    y_axis_order = list(reversed(LISTE_QUAIS))

                if not gantt_df.empty:
                    # CALCUL VECTORISÉ TRÈS RAPIDE POUR LE GANTT
                    gantt_df['start'] = pd.to_datetime(
                        gantt_df['date_prevue'].astype(str).str[:10] + ' ' + gantt_df['heure_prevue'].astype(str).str[
                                                                             :5])
                    gantt_df['end'] = gantt_df['start'] + pd.to_timedelta(TEMPS_DECHARGEMENT_MIN, unit='m')

                    fig = px.timeline(
                        gantt_df, x_start="start", x_end="end", y="quai", color="categorie", text="fournisseur",
                        color_discrete_map={"Frais (0-4°C)": "#0ea5e9", "Epicerie": "#f59e0b", "Surgelés": "#1e3a8a",
                                            "Liquides": "#ef4444", "DPH": "#d946ef"},
                        template="plotly_dark", height=450
                    )

                    fig.update_layout(
                        xaxis_title=None, yaxis_title=None, plot_bgcolor='#151922', paper_bgcolor='#151922',
                        font=dict(family="Inter", size=13, color="#e2e8f0"), margin=dict(t=40, b=40, l=10, r=10),
                        bargap=0.3,
                        legend=dict(title=dict(text="Familles", font=dict(size=14, color="white")), orientation="v",
                                    y=0.5, x=1.02, font=dict(color="white", size=12), bgcolor="rgba(0,0,0,0)"),
                        xaxis=dict(tickformat="%H:%M", side="bottom", gridcolor="#262a36", showgrid=True, dtick=3600000,
                                   range=[datetime.combine(gantt_date, time(6, 0)),
                                          datetime.combine(gantt_date, time(22, 0))]),
                        yaxis=dict(categoryarray=y_axis_order, categoryorder="array", showgrid=True,
                                   gridcolor="#262a36", tickfont=dict(color="white", size=13))
                    )
                    fig.update_traces(marker_line_color='#151922', marker_line_width=2, opacity=0.95,
                                      textposition="inside", insidetextanchor="middle",
                                      textfont=dict(color="white", size=12, weight="bold"))

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Aucune livraison pour les quais sélectionnés.")
            else:
                st.info(f"Aucune livraison planifiée le {gantt_date.strftime('%d/%m/%Y')}.")