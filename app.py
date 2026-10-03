import sqlite3
import streamlit as st

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Entraide & Services - Style Vinted",
    page_icon="🤝",
    layout="wide"
)

# --- STYLE CSS STYLE VINTED + MOTIFS PARTOUT ---
st.markdown("""
    <style>
    /* Fond global avec quadrillage ET grille dense d'émojis de services */
    .stApp {
        background-color: #ffecd2;
        background-image: 
            radial-gradient(rgba(255, 65, 108, 0.12) 2px, transparent 2px),
            linear-gradient(45deg, rgba(255, 65, 108, 0.08) 25%, transparent 25%), 
            linear-gradient(-45deg, rgba(255, 65, 108, 0.08) 25%, transparent 25%), 
            linear-gradient(45deg, transparent 75%, rgba(255, 65, 108, 0.08) 75%), 
            linear-gradient(-45deg, transparent 75%, rgba(255, 65, 108, 0.08) 75%);
        background-size: 60px 60px, 40px 40px, 40px 40px, 40px 40px, 40px 40px;
        background-position: 0 0, 0 0, 0 20px, 20px -20px, -20px 0px;
    }
    
    /* Filigrane d'émojis en arrière-plan */
    .stApp::before {
        content: "🚗 🌳 🛠️ 🍳 📚 🌱 💻 🐾 🔧 🏡 🚗 🌳 🛠️ 🍳 📚 🌱 💻 🐾 🔧 🏡 🚗 🌳 🛠️ 🍳 📚 🌱 💻 🐾 🔧 🏡 🚗 🌳 🛠️ 🍳 📚 🌱 💻 🐾 🔧 🏡";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        font-size: 1.8rem;
        line-height: 80px;
        letter-spacing: 50px;
        word-spacing: 50px;
        opacity: 0.08;
        z-index: 0;
        pointer-events: none;
        overflow: hidden;
    }
    
    /* Barre latérale (sidebar) */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%) !important;
        background-image: 
            radial-gradient(rgba(255, 255, 255, 0.25) 2px, transparent 2px),
            radial-gradient(rgba(255, 255, 255, 0.15) 30%, transparent 31%);
        background-size: 30px 30px, 50px 50px;
    }
    
    [data-testid="stSidebar"]::before {
        content: "🚗🌳🛠️🍳📚🌱💻🐾🔧🏡🚗🌳🛠️🍳📚🌱💻🐾🔧🏡🚗🌳🛠️🍳📚🌱💻🐾🔧🏡🚗🌳🛠️🍳📚🌱💻🐾🔧🏡";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        font-size: 1.4rem;
        line-height: 60px;
        letter-spacing: 20px;
        opacity: 0.07;
        z-index: 0;
        pointer-events: none;
        overflow: hidden;
    }

    [data-testid="stSidebar"] > div:first-child {
        position: relative;
        z-index: 1;
    }
    
    [data-testid="stSidebar"] *:not(.stMetric *):not(.stButton button):not(input):not(select) {
        color: #ffffff !important;
    }

    /* Bloc métrique lisible */
    [data-testid="stSidebar"] [data-testid="stMetric"] {
        background-color: #ffffff !important;
        padding: 12px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        border-left: 6px solid #ff416c;
    }
    [data-testid="stSidebar"] [data-testid="stMetric"] label, 
    [data-testid="stSidebar"] [data-testid="stMetric"] div, 
    [data-testid="stSidebar"] [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #1e3c72 !important;
        font-weight: 800 !important;
    }

    /* Boutons sidebar */
    [data-testid="stSidebar"] .stButton button {
        background-color: #ff416c !important;
        color: #ffffff !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: 2px solid #ffffff !important;
        width: 100%;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background-color: #ff4b2b !important;
    }

    /* Selectbox sidebar */
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 8px;
    }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] * {
        color: #1e3c72 !important;
        font-weight: 600;
    }

    /* Bannière principale */
    .custom-banner {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        padding: 40px 20px;
        border-radius: 22px;
        color: white;
        text-align: center;
        box-shadow: 0 15px 35px rgba(255, 65, 108, 0.4);
        margin-bottom: 25px;
        border: 3px solid rgba(255, 255, 255, 0.6);
        position: relative;
        overflow: hidden;
        z-index: 1;
    }
    .custom-banner h1 {
        color: white !important;
        font-size: 2.8rem;
        font-weight: 900;
        text-shadow: 2px 3px 6px rgba(0,0,0,0.3);
        margin-bottom: 5px;
    }
    .custom-banner p {
        color: #fffaf0;
        font-size: 1.3rem;
        font-weight: 600;
    }

    /* Boîte de connexion */
    .login-box {
        background: rgba(255, 255, 255, 0.95);
        padding: 40px;
        border-radius: 24px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
        border-top: 10px solid #ff416c;
        position: relative;
        z-index: 1;
    }
    .login-box * {
        color: #333333 !important;
    }

    /* Style des cartes de service "Façon Vinted" */
    .vinted-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 20px;
        border: 1px solid #ffd1d8;
        box-shadow: 0 6px 18px rgba(0,0,0,0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        z-index: 1;
    }
    .vinted-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(255, 65, 108, 0.15);
    }
    .vinted-price {
        font-size: 1.3rem;
        font-weight: 900;
        color: #ff416c;
    }
    .vinted-tag {
        background-color: #ffe6eb;
        color: #ff416c;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALISATION DE LA BASE DE DONNÉES ---
DB_NAME = "entraide_vinted_v1.db"

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
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            service_id INTEGER NOT NULL,
            UNIQUE(username, service_id)
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

# --- ÉCRAN DE CONNEXION ---
if not st.session_state.logged_in:
    st.markdown("""
        <div class="custom-banner">
            <h1>🛍️ Vinted Services - Brive</h1>
            <p>🌟 Le vide-dressing des services entre voisins ! Achète, vends et troque tes compétences. 🌟</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.subheader("🔐 Connexion Voisin")
        st.write("Entre tes infos pour accéder à ton dressing de services.")
        
        with st.form("login_form"):
            email_input = st.text_input("Ton adresse e-mail")
            username_input = st.text_input("Ton pseudo")
            city_input = st.text_input("Ta ville", value="Brive-la-Gaillarde")
            
            submit_btn = st.form_submit_button("Entrer sur l'application", type="primary", use_container_width=True)
            
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
                    st.error("Remplis tous les champs correctement.")
                    
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- APPLICATION PRINCIPALE ---
email_input = st.session_state.email
current_username = st.session_state.username
city_input = st.session_state.city

# Récupération des crédits
conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT credits FROM users WHERE email = ?", (email_input,))
row = cursor.fetchone()
if row:
    user_credits = row[0]
else:
    cursor.execute("INSERT INTO users (email, username, city, credits) VALUES (?, ?, ?, 10)", (email_input, current_username, city_input))
    conn.commit()
    user_credits = 10
conn.close()

# Bannière appli
st.markdown(f"""
    <div class="custom-banner">
        <h1>🛍️ Vinted Services - Brive</h1>
        <p>✨ Bienvenue sur ton feed solidaire, {current_username} ! ✨</p>
    </div>
""", unsafe_allow_html=True)

# Barre latérale
st.sidebar.markdown(f"### 👤 @{current_username}")
st.sidebar.success(f"Ville : *{city_input}*")
st.sidebar.metric(label="💰 Portefeuille (Crédits)", value=f"{user_credits} pts")

if st.sidebar.button("🚪 Se déconnecter"):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏷️ Menu Dressing")
menu = st.sidebar.selectbox("Navigation", [
    "🔍 Feed du catalogue", 
    "❤️ Mes favoris (Likes)", 
    "➕ Publier un service", 
    "📋 Mes services en vente"
])

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

# --- 1. CATALOGUE / FEED TYPE VINTED ---
if menu == "🔍 Feed du catalogue":
    st.header(f"📍 Catalogue des services à {city_input}")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, author, city, category, title, description, cost, status, completed_by FROM services WHERE city = ?", (city_input,))
    services = cursor.fetchall()
    conn.close()
    
    if not services:
        st.info("Aucun service en ligne pour le moment. Sois le premier à poster ton annonce !")
    else:
        # Affichage en grille de colonnes façon Vinted (2 colonnes)
        cols = st.columns(2)
        for index, s in enumerate(services):
            service_id, author, city, category, title, description, cost, status, completed_by = s
            icon = category_icons.get(category, "✨")
            
            # Vérifier si l'utilisateur a liké ce service
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM likes WHERE username = ? AND service_id = ?", (current_username, service_id))
            is_liked = cursor.fetchone() is not None
            conn.close()
            
            with cols[index % 2]:
                st.markdown(f"""
                    <div class="vinted-card">
                        <span class="vinted-tag">{icon} {category}</span>
                        <h3>{title}</h3>
                        <p style="color: #666; font-size: 0.9rem;">Par <b>@{author}</b> ({city})</p>
                        <p class="vinted-price">🏷️ {cost} crédits</p>
                        <p style="font-style: italic; color: #444;">{description}</p>
                        <p>Statut : <code>{status}</code></p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Bouton Like / Favori
                like_label = "❤️ Retirer des favoris" if is_liked else "🤍 Ajouter aux favoris"
                if st.button(like_label, key=f"like_{service_id}_{index}"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    if is_liked:
                        cursor.execute("DELETE FROM likes WHERE username = ? AND service_id = ?", (current_username, service_id))
                    else:
                        cursor.execute("INSERT INTO likes (username, service_id) VALUES (?, ?)", (current_username, service_id))
                    conn.commit()
                    conn.close()
                    st.rerun()

                # Action d'achat / prise de service
                if status == "disponible" and author != current_username:
                    if st.button(f"Acheter ce service ({cost} pts)", key=f"buy_{service_id}_{index}", type="primary"):
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
                            st.success("Service acquis avec succès !")
                            st.rerun()
                        else:
                            conn.close()
                            st.error("Tu n'as pas assez de crédits dans ton portefeuille.")

                # Espace messages
                with st.expander(f"💬 Messages ({title})"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT sender, content FROM messages WHERE service_id = ?", (service_id,))
                    messages = cursor.fetchall()
                    conn.close()
                    
                    if messages:
                        for m in messages:
                            st.text(f"@{m[0]} : {m[1]}")
                    else:
                        st.write("Aucun message pour l'instant.")
                        
                    with st.form(key=f"msg_form_{service_id}_{index}"):
                        new_msg = st.text_input("Écris ton message", key=f"input_msg_{service_id}_{index}")
                        send_btn = st.form_submit_button("Envoyer")
                        if send_btn and new_msg.strip():
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO messages (service_id, sender, content) VALUES (?, ?, ?)", 
                                           (service_id, current_username, new_msg))
                            conn.commit()
                            conn.close()
                            st.rerun()
                st.write("")

# --- 2. MES FAVORIS (LIKES) ---
elif menu == "❤️ Mes favoris (Likes)":
    st.header("❤️ Mes services favoris")
    st.write("Retrouve ici tous les coups de cœur que tu as likés !")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, s.author, s.city, s.category, s.title, s.description, s.cost, s.status 
        FROM services s 
        JOIN likes l ON s.id = l.service_id 
        WHERE l.username = ?
    """, (current_username,))
    liked_services = cursor.fetchall()
    conn.close()
    
    if not liked_services:
        st.info("Tu n'as encore liké aucun service. Va parcourir le catalogue !")
    else:
        for s in liked_services:
            service_id, author, city, category, title, description, cost, status = s
            icon = category_icons.get(category, "✨")
            
            st.markdown(f"""
                <div class="vinted-card">
                    <span class="vinted-tag">{icon} {category}</span>
                    <h3>{title}</h3>
                    <p style="color: #666; font-size: 0.9rem;">Proposé par <b>@{author}</b> à {city}</p>
                    <p class="vinted-price">🏷️ {cost} crédits</p>
                    <p><i>{description}</i></p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("💔 Retirer des favoris", key=f"rm_like_{service_id}"):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM likes WHERE username = ? AND service_id = ?", (current_username, service_id))
                conn.commit()
                conn.close()
                st.success("Retiré de tes favoris.")
                st.rerun()
            st.divider()

# --- 3. PUBLIER UN SERVICE ---
elif menu == "➕ Publier un service":
    st.header("➕ Mettre en ligne un service")
    
    with st.form("service_form"):
        category = st.selectbox("Choisis une catégorie", list(category_icons.keys()))
        title = st.text_input("Titre de ton service (ex: Tonte de pelouse, Cours d'anglais...)")
        description = st.text_area("Description détaillée (disponibilités, matériel inclus...)")
        cost = st.number_input("Prix demandé en crédits", min_value=1, value=5, step=1)
        
        submitted = st.form_submit_button("Publier l'annonce", type="primary")
        
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
                st.success("Ton annonce de service a été publiée avec succès !")
            else:
                st.error("Remplis tous les champs pour publier.")

# --- 4. MES SERVICES EN VENTE ---
elif menu == "📋 Mes services en vente":
    st.header(f"📋 Ton dressing de services (@{current_username})")
    
    conn = get_
