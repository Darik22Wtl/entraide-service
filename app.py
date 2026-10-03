import sqlite3
import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Entraide & Services Locaux",
    page_icon="🤝",
    layout="wide"
)

# --- STYLE CSS COLORÉ ET MODERNE ---
st.markdown("""
    <style>
    /* Fond général de l'application avec un joli dégradé doux */
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* En-tête principal coloré avec dégradé vif */
    .main-header {
        font-size: 2.8rem;
        color: #ffffff;
        text-align: center;
        font-weight: 800;
        padding: 30px;
        background: linear-gradient(135deg, #FF4B4B, #FF8F00);
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(255, 75, 75, 0.3);
        margin-bottom: 10px;
    }
    
    .sub-header {
        text-align: center;
        color: #495057;
        font-size: 1.2rem;
        margin-bottom: 35px;
        font-weight: 600;
    }

    /* Boîte de connexion centrale stylisée */
    .login-container {
        background-color: #ffffff;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
        max-width: 500px;
        margin: 50px auto;
        border-top: 6px solid #FF4B4B;
    }

    /* Cartes de service modernes */
    .service-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 14px;
        margin-bottom: 20px;
        border: 1px solid #dee2e6;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease;
    }
    .service-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALISATION DE LA BASE DE DONNÉES ---
DB_NAME = "entraide_final.db"

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
if "step" not in st.session_state:
    st.session_state.step = "ask_email"
if "temp_email" not in st.session_state:
    st.session_state.temp_email = ""

# --- ÉCRAN DE CONNEXION (SI NON CONNECTÉ) ---
if not st.session_state.logged_in:
    st.markdown('<p class="main-header">🤝 Entraide & Services Locaux</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Connectez-vous pour rejoindre votre communauté</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Étape 1 : Demande de l'e-mail
    if st.session_state.step == "ask_email":
        st.subheader("🔐 Étape 1 : Votre E-mail")
        email_input = st.text_input("Entrez votre adresse e-mail")
        
        if st.button("Recevoir mon code de validation", type="primary"):
            if email_input and "@" in email_input:
                st.session_state.temp_email = email_input
                st.session_state.step = "ask_code"
                st.rerun()
            else:
                st.error("Veuillez entrer une adresse e-mail valide.")
                
    # Étape 2 : Demande du code de validation
    elif st.session_state.step == "ask_code":
        st.subheader("📬 Étape 2 : Code de vérification")
        st.info(f"Un code a été simulé pour : *{st.session_state.temp_email}\n\n🔑 **Votre code de test est : 1234*")
        
        code_input = st.text_input("Entrez le code à 4 chiffres", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Valider le code", type="primary"):
                if code_input == "1234":
                    st.session_state.step = "ask_profile"
                    st.rerun()
                else:
                    st.error("Code incorrect. Essayez 1234.")
        with col2:
            if st.button("Retour"):
                st.session_state.step = "ask_email"
                st.rerun()

    # Étape 3 : Demande du pseudo et de la ville
    elif st.session_state.step == "ask_profile":
        st.subheader("👤 Étape 3 : Votre Profil Voisin")
        username_input = st.text_input("Votre pseudo")
        city_input = st.text_input("Votre ville", value="Brive-la-Gaillarde")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Entrer dans l'application", type="primary"):
                if username_input.strip() and city_input.strip():
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, username, city, credits FROM users WHERE email = ?", (st.session_state.temp_email,))
                    user = cursor.fetchone()
                    if not user:
                        cursor.execute("INSERT INTO users (email, username, city, credits) VALUES (?, ?, ?, 10)", 
                                       (st.session_state.temp_email, username_input, city_input))
                        conn.commit()
                    else:
                        cursor.execute("UPDATE users SET username = ?, city = ? WHERE email = ?", 
                                       (username_input, city_input, st.session_state.temp_email))
                        conn.commit()
                    conn.close()
                    
                    st.session_state.logged_in = True
                    st.session_state.email = st.session_state.temp_email
                    st.session_state.username = username_input
                    st.session_state.city = city_input
                    st.rerun()
                else:
                    st.error("Veuillez remplir tous les champs.")
        with col2:
            if st.button("Retour"):
                st.session_state.step = "ask_code"
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- APPLICATION PRINCIPALE (APRÈS CONNEXION RÉUSSIE) ---
email_input = st.session_state.email
current_username = st.session_state.username
city_input = st.session_state.city

# Récupérer les crédits actualisés
conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT credits FROM users WHERE email = ?", (email_input,))
user_credits = cursor.fetchone()[0]
conn.close()

# En-tête application
st.markdown('<p class="main-header">🤝 Entraide & Services Locaux</p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-header">Bienvenue sur votre réseau solidaire à {city_input} !</p>', unsafe_allow_html=True)

# Barre latérale
st.sidebar.header("👤 Mon Profil Voisin")
st.sidebar.success(f"Connecté : *{current_username}*")
st.sidebar.write(f"📧 E-mail : {email_input}")
st.sidebar.write(f"📍 Ville : *{city_input}*")
st.sidebar.metric(label="💰 Vos Crédits Solidaires", value=f"{user_credits} pts")

if st.sidebar.button("Se déconnecter"):
    st.session_state.logged_in = False
    st.session_state.step = "ask_email"
    st.rerun()

st.sidebar.markdown("---")
menu = st.sidebar.selectbox("Navigation", ["🔍 Services dans ma ville", "➕ Proposer un service", "📋 Mes services partagés"])

# Dictionnaire des émojis par catégorie
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
                            st.success("Service pris en charge avec succès ! Les crédits ont été transférés.")
                            st.rerun()
                        else:
                            conn.close()
                            st.error("Vous n'avez pas assez de crédits pour prendre ce service.")
                
                elif status == "en cours":
                    st.info(f"🔄 Ce service est actuellement réalisé par : *{completed_by}*")
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
                        st.write("Aucun message pour l'instant. Discutez pour vous organiser !")
                        
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
                            st.success("Message envoyé !")
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
                st.success("Votre service a été publié avec succès pour votre ville !")
            else:
                st.error("Veuillez remplir tous les champs du formulaire.")

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
                    st.info(f"Pris en charge par votre voisin : *{completed_by}*")
                elif status == "terminé":
                    st.success("Ce service a été réalisé avec succès !")
                st.divider()
