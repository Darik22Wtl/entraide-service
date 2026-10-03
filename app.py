import sqlite3
import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Entraide & Services Locaux",
    page_icon="🤝",
    layout="wide"
)

# --- INITIALISATION DE LA BASE DE DONNÉES ---
DB_NAME = "entraide.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Table des utilisateurs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            credits INTEGER DEFAULT 10
        )
    """)
    
    # Table des services
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            cost INTEGER NOT NULL,
            status TEXT DEFAULT 'disponible',
            completed_by TEXT
        )
    """)
    
    conn.commit()
    conn.close()

# Lancer l'initialisation de la base au démarrage
init_db()

# --- INTERFACE UTILISATEUR ---
st.title("🤝 Entraide & Services Locaux")
st.write("Bienvenue sur la plateforme d'échange et de services entre voisins !")

# Menu de navigation latéral
menu = st.sidebar.selectbox("Navigation", ["Voir les services", "Proposer un service"])

# Connexion à la base pour les requêtes
def get_connection():
    return sqlite3.connect(DB_NAME)

if menu == "Voir les services":
    st.header("📋 Liste des services disponibles")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, author, title, description, cost, status FROM services")
    services = cursor.fetchall()
    conn.close()
    
    if not services:
        st.info("Aucun service n'a encore été partagé. Soyez le premier à en proposer un !")
    else:
        for s in services:
            service_id, author, title, description, cost, status = s
            with st.container():
                st.subheader(f"📌 {title}")
                st.write(f"**Proposé par :** {author} | **Coût :** {cost} crédits | **Statut :** {status}")
                st.write(f"*Description :* {description}")
                st.divider()

elif menu == "Proposer un service":
    st.header("➕ Proposer un nouveau service")
    
    with st.form("service_form"):
        author = st.text_input("Votre nom / pseudo")
        title = st.text_input("Titre du service (ex: Jardinage, Cours de maths...)")
        description = st.text_area("Description détaillée de ce que vous proposez")
        cost = st.number_input("Coût en crédits", min_value=1, value=5, step=1)
        
        submitted = st.form_submit_button("Publier le service")
        
        if submitted:
            if author.strip() and title.strip() and description.strip():
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO services (author, title, description, cost, status)
                    VALUES (?, ?, ?, ?, 'disponible')
                """, (author, title, description, cost))
                conn.commit()
                conn.close()
                st.success("Votre service a été publié avec succès !")
            else:
                st.error("Veuillez remplir tous les champs du formulaire.")
