import sqlite3
import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Entraide & Services Locaux",
    page_icon="🤝",
    layout="wide"
)

# --- STYLE CSS ULTRA-COLORÉ ET DÉCORÉ ---
st.markdown("""
    <style>
    /* Fond global de l'application avec un dégradé coloré */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Bannière principale très colorée */
    .custom-banner {
        background: linear-gradient(135deg, #ff4b4b 0%, #ff9000 50%, #ffb300 100%);
        padding: 40px 20px;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 10px 25px rgba(255, 75, 75, 0.3);
        margin-bottom: 30px;
        border: 2px solid rgba(255, 255, 255, 0.4);
    }
    .custom-banner h1 {
        color: white !important;
        font-size: 2.8rem;
        font-weight: 900;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .custom-banner p {
        color: #fffaf0;
        font-size: 1.3rem;
        font-weight: 600;
    }

    /* Boîte de connexion stylisée */
    .login-box {
        background: white;
        padding: 35px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        border-top: 8px solid #ff4b4b;
    }

    /* Cartes de service avec bordure colorée */
    .service-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 20px;
        border: 1px solid #e2e8f0;
        border-left: 6px solid #4f8bf9;
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease;
    }
    .service-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALISATION DE LA BASE DE DONNÉES ---
DB_NAME = "entraide_direct.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            city TEXT DEFAULT 'Brive-la-Gaillarde',
            credits INTEGER DEFAULT 10
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            city TEXT NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            cost INTEGER NOT NULL,
            status TEXT DEFAULT 'disponible',
            completed_by TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id INTEGER NOT NULL,
            sender TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

def get_connection():
    return sqlite3.connect(DB_NAME)

# --- GESTION DE LA SESSION DE CONNEXION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- ÉCRAN DE CONNEXION DIRECTE PAR E-MAIL ---
if not st.session_state.logged_in:
    st.markdown("""
        <div class="custom-banner">
            <h1>🤝 Entraide & Services Locaux</h1>
            <p>🌟 Le réseau de solidarité coloré entre voisins à Brive ! 🌟</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.subheader("🔐 Connexion Voisin")
        st.write("Entrez vos informations pour accéder directement à l'application et enregistrer votre e-mail.")
        
        with st.form("login_form"):
            email_input = st.text_input("Votre adresse e-mail")
            username_input = st.text_input("Votre pseudo")
            city_input = st.text_input("Votre ville", value="Brive-la-Gaillarde")
            
            submit_btn = st.form_submit_button("Entrer dans l'application", type="primary", use_container_width=True)
            
            if submit_btn:
                if email_input and "@" in email_input and username_input.strip() and city_input.strip():
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, username, city, credits FROM users WHERE email = ?", (email_input,))
                    user = cursor.fetchone()
                    if not user:
                        cursor.execute("INSERT INTO users (email, username, city, credits) VALUES (?, ?, ?, 10)", 
                                       (email_input, username_input, city_input))
                        conn.commit()
                    else:
                        cursor.execute("UPDATE users SET username = ?, city = ? WHERE email = ?", 
                                       (username_input, city_input, email_input))
                        conn.commit()
                    conn.close()
                    
                    st.session_state.logged_in = True
                    st.session_state.email = email_input
                    st.session_state.username = username_input
                    st.session_state.city = city_input
                    st.rerun()
                else:
                    st.error("Veuillez remplir tous les champs avec un e-mail valide.")
                    
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- APPLICATION PRINCIPALE (APRÈS CONNEXION) ---
email_input = st.session_state.email
current_username = st.session_state.username
city_input = st.session_state.city

conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT credits FROM users WHERE email = ?", (email_input,))
user_credits = cursor.fetchone()[0]
conn.close()

# Bannière colorée dans l'application
st.markdown(f"""
    <div class="custom-banner">
        <h1>🤝 Entraide & Services Locaux</h1>
        <p>✨ Bienvenue sur votre réseau solidaire à {city_input} ! ✨</p>
    </div>
""", unsafe_allow_html=True)

# Barre latérale
st.sidebar.header("👤 Mon Profil Voisin")
st.sidebar.success(f"Connecté : *{current_username}*")
st.sidebar.write(f"📧 E-mail : {email_input}")
st.sidebar.write(f"📍 Ville : *{city_input}*")
st.sidebar.metric(label="💰 Vos Crédits Solidaires", value=f"{user_credits} pts")

if st.sidebar.button("Se déconnecter"):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")
menu = st.sidebar.selectbox("Navigation", ["🔍 Services dans ma ville", "➕ Proposer un service", "📋 Mes services partagés"])

category_icons = {
    "🛠️ Bricolage & Réparation": "🛠️",
    "🌱 Jardinage & Extérieur": "🌱",
    "📚 Cours & Soutien scolaire": "📚",
    "🍳 Cuisine & Repas": "🍳",
    "🐾 Garde d'animaux": "🐾",
    "🚗 Transport & Covoiturage": "🚗",
    "💻 Informatique & Numérique": "💻",
    "✨ Autre service": "✨"
}

if menu == "🔍 Services dans ma ville":
    st.header(f"📍 Services disponibles à {city_input}")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, author, city, category, title, description, cost, status, completed_by FROM services WHERE city = ?", (city_input,))
    services = cursor.fetchall()
    conn.close()
    
    if not services:
        st.info(f"Aucun service n'est proposé pour le moment à {city_input}. Soyez le premier à en lancer un !")
    else:
        for s in services:
            service_id, author, city, category, title, description, cost, status, completed_by = s
            icon = category_icons.get(category, "✨")
            
            with st.container():
                st.markdown(f"""
                    <div class="service-card">
                        <h3>{icon} {title}</h3>
                        <p><b>Catégorie :</b> {category} | <b>Proposé par :</b> {author} ({city})</p>
                        <p><b>Coût :</b> {cost} crédits | <b>Statut :</b> <code>{status}</code></p>
                        <p><i>{description}</i></p>
                    </div>
                """, unsafe_allow_html=True)
                
                if status == "disponible" and author != current_username:
                    if st.button(f"Prendre ce service ({cost} crédits)", key=f"take_{service_id}"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT credits FROM users WHERE email = ?", (email_input,))
                        u_cred = cursor.fetchone()[0]
                        
                        if u_cred >= cost:
                            cursor.execute("UPDATE users SET credits = credits - ? WHERE email = ?", (cost, email_input))
                            cursor.execute("UPDATE users SET credits = credits + ? WHERE username = ?", (cost, author))
                            cursor.execute("UPDATE services SET status = 'en cours', completed_by = ? WHERE id = ?", (current_username, service_id))
                            conn.commit()
                            conn.close()
                            st.success("Service pris en charge avec succès !")
                            st.rerun()
                        else:
                            conn.close()
                            st.error("Vous n'avez pas assez de crédits.")
                
                elif status == "en cours":
                    st.info(f"🔄 Réalisé par : *{completed_by}*")
                    if (author == current_username or completed_by == current_username) and st.button("Marquer comme terminé", key=f"finish_{service_id}"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("UPDATE services SET status = 'terminé' WHERE id = ?", (service_id,))
                        conn.commit()
                        conn.close()
                        st.success("Service marqué comme terminé !")
                        st.rerun()

                with st.expander(f"💬 Discuter pour '{title}'"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT sender, content FROM messages WHERE service_id = ?", (service_id,))
                    messages = cursor.fetchall()
                    conn.close()
                    
                    if messages:
                        for m in messages:
                            st.text(f"{m[0]} : {m[1]}")
                    else:
                        st.write("Aucun message pour l'instant.")
                        
                    with st.form(key=f"msg_form_{service_id}"):
                        new_msg = st.text_input("Votre message", key=f"input_msg_{service_id}")
                        send_btn = st.form_submit_button("Envoyer")
                        if send_btn and new_msg.strip():
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO messages (service_id, sender, content) VALUES (?, ?, ?)", 
                                           (service_id, current_username, new_msg))
                            conn.commit()
                            conn.close()
                            st.rerun()
                st.divider()

elif menu == "➕ Proposer un service":
    st.header("➕ Proposer un nouveau service")
    
    with st.form("service_form"):
        category = st.selectbox("Choisissez une catégorie", list(category_icons.keys()))
        title = st.text_input("Titre du service (ex: Tonte de pelouse, Cours de maths...)")
        description = st.text_area("Description détaillée de ce que vous proposez")
        cost = st.number_input("Coût en crédits demandé", min_value=1, value=5, step=1)
        
        submitted = st.form_submit_button("Publier le service")
        
        if submitted:
            if title.strip() and description.strip():
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO services (author, city, category, title, description, cost, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'disponible')
                """, (current_username, city_input, category, title, description, cost))
                conn.commit()
                conn.close()
                st.success("Votre service a été publié avec succès !")
            else:
                st.error("Veuillez remplir tous les champs.")

elif menu == "📋 Mes services partagés":
    st.header(f"📋 Les services proposés par {current_username}")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, city, category, title, description, cost, status, completed_by FROM services WHERE author = ?", (current_username,))
    my_services = cursor.fetchall()
    conn.close()
    
    if not my_services:
        st.info("Vous n'avez publié aucun service pour l'instant.")
    else:
        for s in my_services:
            service_id, city, category, title, description, cost, status, completed_by = s
            icon = category_icons.get(category, "✨")
            
            with st.container():
                st.markdown(f"""
                    <div class="service-card">
                        <h3>{icon} {title}</h3>
                        <p><b>Catégorie :</b> {category} | <b>Ville :</b> {city}</p>
                        <p><b>Coût :</b> {cost} crédits | <b>Statut :</b> <code>{status}</code></p>
                        <p><i>{description}</i></p>
                    </div>
                """, unsafe_allow_html=True)
                
                if status == "en cours":
                    st.info(f"Pris en charge par : *{completed_by}*")
                elif status == "terminé":
                    st.success("Réalisé avec succès !")
                st.divider()
