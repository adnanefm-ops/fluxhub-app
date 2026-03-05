import sqlite3
import pandas as pd
from datetime import datetime, timedelta

DB_NAME = "supply_chain_v3.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    """Initialise la BDD et effectue les migrations automatiques."""
    conn = get_connection()
    c = conn.cursor()

    # 1. Création de la table de base (avec les nouveaux champs)
    c.execute('''
        CREATE TABLE IF NOT EXISTS livraisons (
            id TEXT PRIMARY KEY,
            fournisseur TEXT,
            categorie TEXT,
            palettes INTEGER,
            colis INTEGER,
            date_prevue DATE,
            heure_prevue TEXT,
            email TEXT,
            telephone TEXT,
            transporteur TEXT,
            nom_chauffeur TEXT,
            immatriculation TEXT,
            commentaire TEXT,
            statut TEXT,
            quai TEXT,
            message_sc TEXT,
            est_modifie BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Migration automatique : on ajoute les nouveaux champs
    columns_to_check = {
        "est_modifie": "BOOLEAN DEFAULT 0",
        "message_sc": "TEXT",
        "email": "TEXT",
        "telephone": "TEXT",
        "colis": "INTEGER DEFAULT 0",
        "transporteur": "TEXT",
        "nom_chauffeur": "TEXT",
        "immatriculation": "TEXT",
        "commentaire": "TEXT"
    }

    c.execute("PRAGMA table_info(livraisons)")
    existing_cols = [row[1] for row in c.fetchall()]

    for col_name, col_type in columns_to_check.items():
        if col_name not in existing_cols:
            print(f"🔧 Migration : Ajout de la colonne '{col_name}'...")
            try:
                c.execute(f"ALTER TABLE livraisons ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                print(f"Erreur migration {col_name}: {e}")

    conn.commit()
    conn.close()

class SupplyChainDB:
    def __init__(self):
        init_db()

    def create_demande(self, id_req, fourn, cat, pal, colis, date, heure, email, tel, transporteur, chauffeur, immat, comm):
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO livraisons (
                id, fournisseur, categorie, palettes, colis, date_prevue, heure_prevue, 
                email, telephone, transporteur, nom_chauffeur, immatriculation, commentaire, 
                statut, quai, message_sc, est_modifie
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (id_req, fourn, cat, pal, colis, date, heure, email, tel, transporteur, chauffeur, immat, comm, "En attente", "Non assigné", "", 0))
        conn.commit()
        conn.close()

    def update_statut(self, id_req, statut, quai=None, msg="", nouvelle_heure=None, est_modifie=False):
        conn = get_connection()
        c = conn.cursor()

        query = "UPDATE livraisons SET statut = ?, message_sc = ?, est_modifie = ?"
        params = [statut, msg, est_modifie]

        if quai:
            query += ", quai = ?"
            params.append(quai)

        if nouvelle_heure:
            query += ", heure_prevue = ?"
            params.append(nouvelle_heure)

        query += " WHERE id = ?"
        params.append(id_req)

        c.execute(query, tuple(params))
        conn.commit()
        conn.close()

    def check_conflit(self, date_str, heure_str, quai):
        """Vérifie si le quai est libre (Tolérance +/- 30 min)"""
        df = self.get_all()
        if df.empty: return False

        # On ne garde que les validés sur ce quai ce jour-là
        target_date = pd.to_datetime(date_str).date()
        conflits = df[
            (df['statut'] == 'Validé') &
            (df['quai'] == quai) &
            (df['date_prevue'].dt.date == target_date)
            ]

        if conflits.empty: return False

        # Vérification fine de l'heure
        heure_exacte = conflits[conflits['heure_prevue'] == str(heure_str)[:5]]

        return not heure_exacte.empty

    def get_all(self):
        conn = get_connection()
        try:
            df = pd.read_sql("SELECT * FROM livraisons", conn)
            # Conversion forcée des types pour éviter les bugs Streamlit
            if not df.empty:
                df['date_prevue'] = pd.to_datetime(df['date_prevue'])
                df['est_modifie'] = df['est_modifie'].astype(bool)
        except Exception as e:
            print(f"Erreur lecture BDD: {e}")
            df = pd.DataFrame()
        finally:
            conn.close()
        return df

    def get_kpis(self):
        df = self.get_all()
        if df.empty: return 0, 0, 0, 0
        total = len(df)
        attente = len(df[df['statut'] == "En attente"])
        valide = len(df[df['statut'] == "Validé"])
        palettes = df['palettes'].sum()
        return total, attente, valide, palettes
