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
    
    # Table des utilisateurs (avec gestion des crédits)
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
    
    # Table pour les messages/discussion autour des services
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id INTEGER NOT NULL,
            sender TEXT NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY(service_id) REFERENCES services(id)
        )
    """)
    
    conn.commit()
    conn.close()

init_db()

def get_connection():
    return sqlite3.connect(DB_NAME)

# Fonction pour récupérer ou créer un utilisateur automatiquement
def get_or_create_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, credits FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (username, credits) VALUES (?, 10)", (username,))
        conn.commit()
        cursor.execute("SELECT id, credits FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
    conn.close()
    return user

# --- INTERFACE UTILISATEUR ---
st.title("🤝 Entraide & Services Locaux")
st.write("Échangez des services, discutez entre voisins et gagnez des crédits !")

# Barre latérale pour l'utilisateur actuel
st.sidebar.header("Mon Profil")
current_user = st.sidebar.text_input("Votre pseudo", value="MonPseudo")

if current_user:
    user_data = get_or_create_user(current_user)
    st.sidebar.write(text=f"💰 Vos crédits : **{user_data[1]}**")

# Menu de navigation
menu = st.sidebar.selectbox("Navigation", ["Voir les services", "Proposer un service"])

if menu == "Voir les services":
    st.header("📋 Liste des services disponibles")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, author, title, description, cost, status, completed_by FROM services")
    services = cursor.fetchall()
    conn.close()
    
    if not services:
        st.info("Aucun service n'a encore été partagé.")
    else:
        for s in services:
            service_id, author, title, description, cost, status, completed_by = s
            with st.container():
                st.subheader(f"📌 {title}")
                st.write(f"**Proposé par :** {author} | **Coût :** {cost} crédits | **Statut :** `{status}`")
                st.write(f"*Description :* {description}")
                
                if status == "disponible" and author != current_user:
                    if st.button(f"Prendre ce service ({cost} crédits)", key=f"take_{service_id}"):
                        # Vérifier si l'utilisateur a assez de crédits
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT credits FROM users WHERE username = ?", (current_user,))
                        u_cred = cursor.fetchone()[0]
                        
                        if u_cred >= cost:
                            # Déduire les crédits de l'acheteur
                            cursor.execute("UPDATE users SET credits = credits - ? WHERE username = ?", (cost, current_user))
                            # Ajouter les crédits à l'auteur
                            cursor.execute("UPDATE users SET credits = credits + ? WHERE username = ?", (cost, author))
                            # Mettre à jour le service
                            cursor.execute("UPDATE services SET status = 'en cours', completed_by = ? WHERE id = ?", (current_user, service_id))
                            conn.commit()
                            conn.close()
                            st.success("Vous avez pris en charge ce service ! Les crédits ont été transférés.")
                            st.rerun()
                        else:
                            conn.close()
                            st.error("Vous n'avez pas assez de crédits pour prendre ce service.")
                
                elif status == "en cours":
                    st.info(f"Ce service est réalisé par : {completed_by}")
                    if (author == current_user or completed_by == current_user) and st.button("Marquer comme terminé", key=f"finish_{service_id}"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE services SET status = 'terminé' WHERE id = ?", (service_id,))
                        conn.commit()
                        conn.close()
                        st.success("Service terminé avec succès !")
                        st.rerun()

                # --- SECTION DISCUSSION / MESSAGERIE ---
                with st.expander(f"💬 Espace discussion pour '{title}'"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT sender, content FROM messages WHERE service_id = ?", (service_id,))
                    messages = cursor.fetchall()
                    conn.close()
                    
                    if messages:
                        for m in messages:
                            st.text(f"{m[0]} : {m[1]}")
                    else:
                        st.write("Aucun message pour l'instant. Discutez avec le voisin pour vous organiser !")
                        
                    with st.form(f"msg_form_{service_id}"):
                        new_msg = st.text_input("Votre message", key=f"input_msg_{service_id}")
                        send_btn = st.form_submit_button("Envoyer")
                        if send_btn and new_msg.strip():
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO messages (service_id, sender, content) VALUES (?, ?, ?)", 
                                           (service_id, current_user, new_msg))
                            conn.commit()
                            conn.close()
                            st.success("Message envoyé !")
                            st.rerun()
                
                st.divider()

elif menu == "Proposer un service":
    st.header("➕ Proposer un nouveau service")
    
    with st.form("service_form"):
        title = st.text_input("Titre du service (ex: Jardinage, Cours de guitare...)")
        description = st.text_area("Description détaillée")
        cost = st.number_input("Coût en crédits demandé", min_value=1, value=5, step=1)
        
        submitted = st.form_submit_button("Publier le service")
        
        if submitted:
            if current_user.strip() and title.strip() and description.strip():
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO services (author, title, description, cost, status)
                    VALUES (?, ?, ?, ?, 'disponible')
                """, (current_user, title, description, cost))
                conn.commit()
                conn.close()
                st.success("Votre service a été publié avec succès !")
            else:
                st.error("Veuillez remplir tous les champs et indiquer votre pseudo dans la barre latérale.")
