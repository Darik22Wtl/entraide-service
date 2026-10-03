mport sqlite3
import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Entraide & Services Locaux",
    page_icon="🤝",
    layout="wide"
)

# --- STYLE CSS AVANCÉ & MODERNE ---
st.markdown("""
    <style>
    /* Style général de l'en-tête */
    .main-header {
        font-size: 2.8rem;
        color: #FF4B4B;
        text-align: center;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sub-header {
        text-align: center;
        color: #4F8BF9;
        font-size: 1.2rem;
        margin-bottom: 30px;
        font-weight: 500;
    }
    /* Cartes de service élégantes avec effet d'ombre */
    .service-card {
        background-color: #ffffff;
        padding: 22px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease;
    }
    .service-card:hover {
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.08);
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALISATION DE LA BASE DE DONNÉES ---
DB_NAME = "entraide_v2.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
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

# Initialisation immédiate de la base
init_db()

def get_connection():
    return sqlite3.connect(DB_NAME)

# --- GESTION DE L'UTILISATEUR (BARRE LATÉRALE STYLISÉE) ---
st.markdown('<p class="main-header">🤝 Entraide & Services Locaux</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Le réseau de solidarité et d\'échange entre voisins</p>', unsafe_allow_html=True)

st.sidebar.header("👤 Mon Profil Voisin")
username_input = st.sidebar.text_input("Votre pseudo", value="")
city_input = st.sidebar.text_input("Votre ville", value="Brive-la-Gaillarde")

if not username_input:
    st.warning("👋 Bienvenue ! Veuillez entrer votre pseudo et votre ville dans la barre latérale à gauche pour commencer.")
    st.stop()

def get_or_create_user(username, city):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, city, credits FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (username, city, credits) VALUES (?, ?, 10)", (username, city))
        conn.commit()
        cursor.execute("SELECT id, city, credits FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
    else:
        cursor.execute("UPDATE users SET city = ? WHERE username = ?", (city, username))
        conn.commit()
    conn.close()
    return user

user_data = get_or_create_user(username_input, city_input)

st.sidebar.markdown("---")
st.sidebar.success(f"Connecté : *{username_input}*")
st.sidebar.write(f"📍 Ville : *{city_input}*")
# Affichage stylisé des crédits avec une métrique Streamlit
st.sidebar.metric(label="💰 Vos Crédits Solidaires", value=f"{user_data[2]} pts")
st.sidebar.markdown("---")

# --- MENU DE NAVIGATION ---
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
                
                if status == "disponible" and author != username_input:
                    if st.button(f"Prendre ce service ({cost} crédits)", key=f"take_{service_id}"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("SELECT credits FROM users WHERE username = ?", (username_input,))
                        u_cred = cursor.fetchone()[0]
                        
                        if u_cred >= cost:
                            cursor.execute("UPDATE users SET credits = credits - ? WHERE username = ?", (cost, username_input))
                            cursor.execute("UPDATE users SET credits = credits + ? WHERE username = ?", (cost, author))
                            cursor.execute("UPDATE services SET status = 'en cours', completed_by = ? WHERE id = ?", (username_input, service_id))
                            conn.commit()
                            conn.close()
                            st.success("Service pris en charge avec succès ! Les crédits ont été transférés.")
                            st.rerun()
                        else:
                            conn.close()
                            st.error("Vous n'avez pas assez de crédits pour prendre ce service.")
                
                elif status == "en cours":
                    st.info(f"🔄 Ce service est actuellement réalisé par : *{completed_by}*")
                    if (author == username_input or completed_by == username_input) and st.button("Marquer comme terminé", key=f"finish_{service_id}"):
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
                                           (service_id, username_input, new_msg))
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
                """, (username_input, city_input, category, title, description, cost))
                conn.commit()
                conn.close()
                st.success("Votre service a été publié avec succès pour votre ville !")
            else:
                st.error("Veuillez remplir tous les champs du formulaire.")

elif menu == "📋 Mes services partagés":
    st.header(f"📋 Les services proposés par {username_input}")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, city, category, title, description, cost, status, completed_by FROM services WHERE author = ?", (username_input,))
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
