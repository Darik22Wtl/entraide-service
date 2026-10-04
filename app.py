import hashlib
import html
import hmac
import os
import secrets
import smtplib
import sqlite3
import time
from contextlib import contextmanager
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import streamlit as st
try:
    import streamlit.components.v1 as components
except Exception:
    components = None

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Entraide & Services Locaux", page_icon="🤝", layout="wide"
)

CODE_VALIDITY_SECONDS = 600  # 10 minutes
MAX_CODE_ATTEMPTS = 5
DB_NAME = "entraide_v14.db"
SESSION_DAYS = 30
COOKIE_NAME = "entraide_token"

# --- STYLE CSS ---
st.markdown(
    """
    <style>
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
    .custom-banner {
        background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);
        padding: 45px 25px;
        border-radius: 25px;
        color: white;
        text-align: center;
        box-shadow: 0 15px 35px rgba(255, 65, 108, 0.4);
        margin-bottom: 30px;
        border: 3px solid rgba(255, 255, 255, 0.6);
    }
    .custom-banner h1 { color: white !important; font-size: 3rem; font-weight: 900; }
    .login-box {
        background: rgba(255, 255, 255, 0.95);
        padding: 40px;
        border-radius: 24px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
        border-top: 10px solid #ff416c;
    }
    .service-card {
        background-color: #ffffff;
        padding: 26px;
        border-radius: 18px;
        margin-bottom: 22px;
        border: 1px solid #ffdde1;
        border-left: 8px solid #ff416c;
        box-shadow: 0 8px 20px rgba(255, 65, 108, 0.1);
    }
    .dashboard-section {
        background: rgba(255, 255, 255, 0.9);
        padding: 25px;
        border-radius: 20px;
        border: 2px solid #ff416c;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        margin-top: 30px;
        margin-bottom: 30px;
    }

    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
    html, body, .stApp, .stMarkdown, button, input, textarea { font-family: 'Poppins', sans-serif; }
    .stApp::before {
        content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0; opacity: 0.22;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='220' height='220'%3E%3Ctext x='15' y='45' font-size='30'%3E🤝%3C/text%3E%3Ctext x='130' y='95' font-size='26'%3E🌻%3C/text%3E%3Ctext x='40' y='140' font-size='26'%3E🏡%3C/text%3E%3Ctext x='150' y='200' font-size='28'%3E💛%3C/text%3E%3Ctext x='85' y='205' font-size='22'%3E🌳%3C/text%3E%3C/svg%3E");
    }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #fff5f7 0%, #ffd9e0 100%); border-right: 3px solid #ff416c; }
    .stButton > button, .stFormSubmitButton > button { border-radius: 999px; border: 2px solid #ff416c; font-weight: 600; transition: all .2s; }
    .stButton > button:hover, .stFormSubmitButton > button:hover { background: #ff416c; color: white; transform: translateY(-2px); box-shadow: 0 6px 14px rgba(255,65,108,.35); }
    .service-card { transition: transform .2s, box-shadow .2s; }
    .service-card:hover { transform: translateY(-4px); box-shadow: 0 14px 28px rgba(255,65,108,.22); }
    .custom-banner p { font-size: 1.15rem; opacity: .95; }
    .stats-row, .tiles { display: flex; gap: 16px; flex-wrap: wrap; justify-content: center; margin-bottom: 22px; }
    .stat-pill { background: rgba(255,255,255,.9); border: 2px solid #ff416c; border-radius: 999px; padding: 8px 22px; font-weight: 600; color: #c2185b; }
    .tile { flex: 1; min-width: 200px; max-width: 300px; background: #fff; border-radius: 20px; padding: 22px; text-align: center; border-bottom: 6px solid #ff416c; box-shadow: 0 8px 20px rgba(255,65,108,.15); }
    .tile .big { font-size: 2.4rem; }
    .tile h4 { margin: 6px 0; color: #d6244f; }
    .tile p { margin: 0; font-size: .9rem; color: #555; }
    .space-title { text-align: center; color: #d6244f; font-weight: 800; }
    .profile-card { display: flex; align-items: center; gap: 22px; background: linear-gradient(135deg, #ff416c, #ff4b2b); color: white; border-radius: 24px; padding: 24px 30px; box-shadow: 0 12px 28px rgba(255,65,108,.35); margin-bottom: 22px; }
    .profile-card h2 { color: white; margin: 0; }
    .profile-card p { margin: 4px 0 0; opacity: .95; }
    .avatar { width: 72px; height: 72px; border-radius: 50%; background: white; color: #ff416c; font-size: 2.2rem; font-weight: 800; display: flex; align-items: center; justify-content: center; border: 4px solid rgba(255,255,255,.6); flex-shrink: 0; }
    .stat-card { background: rgba(255,255,255,.95); border-radius: 18px; padding: 16px 8px; text-align: center; border-top: 5px solid #ff416c; box-shadow: 0 6px 16px rgba(0,0,0,.08); }
    .stat-icon { font-size: 1.6rem; }
    .stat-value { font-size: 1.9rem; font-weight: 800; color: #d6244f; line-height: 1.1; }
    .stat-label { font-size: .8rem; color: #666; }
    .mini-card { background: #fff; border-radius: 14px; padding: 14px 18px; margin-bottom: 12px; border-left: 6px solid #ff416c; box-shadow: 0 4px 12px rgba(0,0,0,.07); }
    .mini-card small { color: #666; }
    .badge { padding: 2px 12px; border-radius: 999px; font-size: .78rem; font-weight: 600; color: white; }
    .badge.ok { background: #2e9e5b; } .badge.wip { background: #f39c12; } .badge.done { background: #7f8c8d; }
    .stTabs [data-baseweb="tab"] { font-weight: 600; }

    /* ===== THÈME NOIR ===== */
    .stApp { background: #000000 !important; }
    .stApp::before { display: none !important; }
    .stApp, .stApp p, .stApp li, .stApp label,
    .stApp [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stCaptionContainer"],
    .stApp [data-testid="stMetricLabel"],
    .stApp [data-testid="stMetricValue"],
    .stApp .stTabs [data-baseweb="tab"] { color: #f5f5f5; }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4 { color: #ffffff; }
    section[data-testid="stSidebar"] { background: #0b0b0b; }
    .login-box, .service-card, .tile, .mini-card, .stat-card, .dashboard-section, .stat-pill {
        background: #141414; color: #f2f2f2; border-color: #3a1f27;
    }
    .stat-pill { color: #ff8fa8; }
    .tile h4, .stat-value { color: #ff6b8a; }
    .tile p, .stat-label, .mini-card small { color: #bdbdbd; }
    .stApp .space-title { color: #ff6b8a; }

    /* ===== CONTRASTES (lisibilité sur fond noir) ===== */
    section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div { background: #101010 !important; }
    .login-box, .service-card, .tile, .mini-card, .stat-card, .stat-pill {
        background: #1f1f1f !important; border: 1px solid rgba(255,65,108,.45); border-left: 6px solid #ff416c;
    }
    .stat-card, .tile { border-left: 1px solid rgba(255,65,108,.45); }
    .stApp hr { border-color: #3a3a3a !important; }
    .stApp a { color: #7db7ff; }
    /* boutons : fond sombre, texte blanc, contour rose */
    .stApp .stButton > button, .stApp .stFormSubmitButton > button, .stApp .stDownloadButton > button {
        background: #262626 !important; color: #ffffff !important; border: 2px solid #ff416c !important;
    }
    .stApp .stButton > button *, .stApp .stFormSubmitButton > button * { color: #ffffff !important; }
    .stApp .stButton > button:hover, .stApp .stFormSubmitButton > button:hover { background: #ff416c !important; }
    .stApp button[kind="primary"], .stApp button[kind="primaryFormSubmit"],
    .stApp [data-testid="stBaseButton-primary"], .stApp [data-testid="stBaseButton-primaryFormSubmit"] {
        background: #ff416c !important; color: #ffffff !important; border: 2px solid #ffffff !important;
    }
    /* champs de saisie et listes : fond gris foncé, texte blanc */
    .stApp input, .stApp textarea, .stApp [data-baseweb="select"] > div,
    .stApp [data-baseweb="input"], .stApp [data-baseweb="base-input"], .stApp [data-baseweb="textarea"] {
        background: #262626 !important; color: #ffffff !important; border-color: #ff416c !important;
    }
    .stApp [data-baseweb="select"] * { color: #ffffff !important; }
    .stApp [data-baseweb="select"] svg { fill: #ffffff !important; }
    .stApp input::placeholder, .stApp textarea::placeholder { color: #a0a0a0 !important; }
    .stApp [data-testid="stNumberInput"] button { background: #262626 !important; color: #ffffff !important; }
    /* messages (info, succès, erreur) : fond opaque + texte blanc */
    .stApp [data-testid="stAlertContainer"] {
        background: #16263d !important; border: 1px solid #3b82f6; border-radius: 12px;
    }
    .stApp [data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]) { background: #12301d !important; border-color: #22c55e; }
    .stApp [data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]) { background: #3a2d10 !important; border-color: #f59e0b; }
    .stApp [data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]) { background: #3b1519 !important; border-color: #ef4444; }
    .stApp [data-testid="stAlertContainer"], .stApp [data-testid="stAlertContainer"] * { color: #ffffff !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

esc = html.escape  # échappement systématique du contenu utilisateur


# --- SECRETS (jamais de mot de passe dans le code) ---
def get_secret(name):
    value = os.environ.get(name)
    if value:
        return value
    try:
        return st.secrets[name]
    except Exception:
        return None


def send_verification_email(receiver_email, code):
    sender_email = get_secret("SMTP_EMAIL") or "entraideservicelocaux@gmail.com"
    sender_password = get_secret("SMTP_PASSWORD")
    if not sender_email or not sender_password:
        print("Erreur : SMTP_EMAIL / SMTP_PASSWORD non configurés.")
        return False

    body = f"""
    Bonjour,

    Voici votre code de vérification pour vous connecter à l'application d'entraide :

    🔑 {code}

    Ce code est strictement personnel et valable {CODE_VALIDITY_SECONDS // 60} minutes.

    À très vite sur l'application !
    """
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Votre code de vérification - Entraide & Services"
    message.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        return True
    except Exception as e:
        print(f"Erreur d'envoi : {e}")
        return False


# --- BASE DE DONNÉES ---
@contextmanager
def db():
    """Connexion avec commit automatique et rollback en cas d'erreur."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL COLLATE NOCASE,
                city TEXT NOT NULL DEFAULT 'Brive-la-Gaillarde',
                credits INTEGER NOT NULL DEFAULT 10 CHECK (credits >= 0)
            );
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author_email TEXT NOT NULL REFERENCES users(email),
                city TEXT NOT NULL,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                cost INTEGER NOT NULL CHECK (cost >= 1),
                status TEXT NOT NULL DEFAULT 'disponible',
                completed_by_email TEXT REFERENCES users(email)
            );
            CREATE TABLE IF NOT EXISTS likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL REFERENCES users(email),
                service_id INTEGER NOT NULL REFERENCES services(id),
                UNIQUE(user_email, service_id)
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id INTEGER NOT NULL REFERENCES services(id),
                sender_email TEXT NOT NULL REFERENCES users(email),
                content TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY,
                email TEXT NOT NULL REFERENCES users(email),
                expires REAL NOT NULL
            );
            """
        )


init_db()


def take_service(service_id, buyer_email):
    """Paiement atomique. Retourne un message d'erreur ou None si succès."""
    with db() as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            "SELECT author_email, cost, status FROM services WHERE id = ?",
            (service_id,),
        ).fetchone()
        if not row or row[2] != "disponible":
            return "Ce service n'est plus disponible."
        author_email, cost, _ = row
        if author_email == buyer_email:
            return "Vous ne pouvez pas prendre votre propre service."
        debit = conn.execute(
            "UPDATE users SET credits = credits - ? WHERE email = ? AND credits >= ?",
            (cost, buyer_email, cost),
        )
        if debit.rowcount == 0:
            return "Vous n'avez pas assez de crédits."
        conn.execute(
            "UPDATE users SET credits = credits + ? WHERE email = ?",
            (cost, author_email),
        )
        conn.execute(
            "UPDATE services SET status = 'en cours', completed_by_email = ? WHERE id = ?",
            (buyer_email, service_id),
        )
    return None


# --- GESTION DE LA SESSION ---
defaults = {
    "logged_in": False,
    "verification_code": None,
    "code_expires": 0.0,
    "code_attempts": 0,
    "temp_email": "",
    "temp_username": "",
    "temp_city": "",
}
for key, value in defaults.items():
    st.session_state.setdefault(key, value)


def reset_verification():
    st.session_state.verification_code = None
    st.session_state.code_attempts = 0



# --- CONNEXION MÉMORISÉE (cookie + session en base, 30 jours) ---
def run_js(js):
    """Exécute du JavaScript dans la page (st.html, sinon ancienne méthode)."""
    try:
        st.html(
            f"<script>(function(){{const W = window; {js}}})();</script>",
            unsafe_allow_javascript=True,
        )
    except TypeError:
        if components is not None:
            components.html(
                f"<script>(function(){{const W = window.parent; {js}}})();</script>",
                height=0,
            )


def _hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


def create_session(email):
    token = secrets.token_urlsafe(32)
    with db() as conn:
        conn.execute("DELETE FROM sessions WHERE expires < ?", (time.time(),))
        conn.execute(
            "INSERT INTO sessions (token_hash, email, expires) VALUES (?, ?, ?)",
            (_hash(token), email, time.time() + SESSION_DAYS * 86400),
        )
    return token


def get_cookie_token():
    try:
        return st.context.cookies.get(COOKIE_NAME)
    except Exception:
        return None


def user_from_token(token):
    if not token:
        return None
    with db() as conn:
        return conn.execute(
            """SELECT u.email, u.username, u.city FROM sessions s
               JOIN users u ON u.email = s.email
               WHERE s.token_hash = ? AND s.expires > ?""",
            (_hash(token), time.time()),
        ).fetchone()


def delete_session(token):
    if token:
        with db() as conn:
            conn.execute("DELETE FROM sessions WHERE token_hash = ?", (_hash(token),))


if not st.session_state.logged_in and not st.session_state.get("just_logged_out"):
    found = user_from_token(get_cookie_token())
    if found:
        st.session_state.logged_in = True
        st.session_state.email, st.session_state.username, st.session_state.city = found

# --- ÉCRAN DE CONNEXION AVEC VÉRIFICATION PAR E-MAIL ---
if not st.session_state.logged_in:
    st.markdown(
        """
        <div class="custom-banner">
            <h1>🤝 Entraide & Services Locaux</h1>
            <p>🌟 Le réseau solidaire de vos voisins : échangez, aidez, partagez ! 🌟</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with db() as conn:
        n_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        n_serv = conn.execute("SELECT COUNT(*) FROM services").fetchone()[0]
        n_done = conn.execute(
            "SELECT COUNT(*) FROM services WHERE status = 'terminé'"
        ).fetchone()[0]
    st.markdown(
        f"""<div class="stats-row">
<span class="stat-pill">👥 {n_users} voisins</span>
<span class="stat-pill">📋 {n_serv} services</span>
<span class="stat-pill">✅ {n_done} échanges réalisés</span>
</div>
<div class="tiles">
<div class="tile"><div class="big">📝</div><h4>1. Proposez</h4><p>Publiez un service : bricolage, cours, jardinage...</p></div>
<div class="tile"><div class="big">🤝</div><h4>2. Échangez</h4><p>Discutez avec vos voisins et prenez un service.</p></div>
<div class="tile"><div class="big">💰</div><h4>3. Gagnez</h4><p>10 crédits offerts à l'inscription, à dépenser ou à gagner !</p></div>
</div>""",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.subheader("🔐 Connexion Voisin")

        if st.session_state.verification_code is None:
            with st.form("login_form"):
                email_input = st.text_input("Votre adresse e-mail")
                username_input = st.text_input("Votre pseudo")
                city_input = st.text_input("Votre ville", value="Brive-la-Gaillarde")
                submit_btn = st.form_submit_button(
                    "Envoyer le code de vérification", type="primary"
                )

            if submit_btn:
                email = email_input.strip().lower()
                username = username_input.strip()
                city = city_input.strip()

                if not (email and "@" in email and username and city):
                    st.error("Veuillez remplir tous les champs correctement.")
                else:
                    with db() as conn:
                        existing = conn.execute(
                            "SELECT username, city FROM users WHERE email = ?",
                            (email,),
                        ).fetchone()
                        taken = conn.execute(
                            "SELECT 1 FROM users WHERE username = ? AND email != ?",
                            (username, email),
                        ).fetchone()

                    if existing:
                        # Compte existant : on garde pseudo et ville enregistrés
                        username, city = existing

                    if taken and not existing:
                        st.error("Ce pseudo est déjà utilisé, choisissez-en un autre.")
                    else:
                        code = str(secrets.randbelow(900000) + 100000)
                        with st.spinner("Envoi de l'e-mail en cours..."):
                            success = send_verification_email(email, code)
                        if success:
                            st.session_state.verification_code = code
                            st.session_state.code_expires = (
                                time.time() + CODE_VALIDITY_SECONDS
                            )
                            st.session_state.code_attempts = 0
                            st.session_state.temp_email = email
                            st.session_state.temp_username = username
                            st.session_state.temp_city = city
                            st.rerun()
                        else:
                            st.error("Erreur lors de l'envoi de l'e-mail.")
        else:
            st.info(
                "Un code a été envoyé à l'adresse : **"
                f"{esc(st.session_state.temp_email)}**"
            )
            with st.form("verify_form"):
                entered_code = st.text_input("Entrez le code à 6 chiffres reçu par mail")
                verify_btn = st.form_submit_button("Valider le code", type="primary")

            if verify_btn:
                if time.time() > st.session_state.code_expires:
                    reset_verification()
                    st.error("Le code a expiré. Veuillez en demander un nouveau.")
                    st.rerun()
                elif st.session_state.code_attempts >= MAX_CODE_ATTEMPTS:
                    reset_verification()
                    st.error("Trop de tentatives. Veuillez recommencer.")
                    st.rerun()
                elif hmac.compare_digest(
                    entered_code.strip(), st.session_state.verification_code
                ):
                    with db() as conn:
                        conn.execute(
                            "INSERT OR IGNORE INTO users (email, username, city, credits)"
                            " VALUES (?, ?, ?, 10)",
                            (
                                st.session_state.temp_email,
                                st.session_state.temp_username,
                                st.session_state.temp_city,
                            ),
                        )
                    st.session_state.new_token = create_session(
                        st.session_state.temp_email
                    )
                    st.session_state.just_logged_out = False
                    st.session_state.logged_in = True
                    st.session_state.email = st.session_state.temp_email
                    st.session_state.username = st.session_state.temp_username
                    st.session_state.city = st.session_state.temp_city
                    reset_verification()
                    st.rerun()
                else:
                    st.session_state.code_attempts += 1
                    left = MAX_CODE_ATTEMPTS - st.session_state.code_attempts
                    st.error(f"Code incorrect. Il vous reste {left} tentative(s).")

            if st.button("🔄 Recommencer (changer d'e-mail)"):
                reset_verification()
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- APPLICATION PRINCIPALE ---
current_email = st.session_state.email

with db() as conn:
    row = conn.execute(
        "SELECT username, city, credits FROM users WHERE email = ?", (current_email,)
    ).fetchone()

if not row:  # compte introuvable : on déconnecte proprement
    st.session_state.logged_in = False
    st.rerun()

current_username, city_input, user_credits = row

if st.session_state.get("new_token"):
    _token = st.session_state.pop("new_token")
    run_js(
        f"W.document.cookie = '{COOKIE_NAME}={_token};"
        f" max-age={SESSION_DAYS * 86400}; path=/; SameSite=Lax; Secure';"
    )

st.markdown(
    f"""
    <div class="custom-banner">
        <h1>🤝 Entraide & Services Locaux</h1>
        <p>✨ Bienvenue sur votre réseau solidaire à {esc(city_input)} ! ✨</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("### 🌳 🌻 Mon Profil Voisin")
st.sidebar.success(f"Connecté : **{current_username}**")
st.sidebar.write(f"📧 E-mail : *{current_email}*")
st.sidebar.write(f"📍 Ville : **{city_input}**")
st.sidebar.metric(label="💰 Vos Crédits Solidaires", value=f"{user_credits} pts")
st.sidebar.caption("Version 5 · couleurs contrastées")

if st.sidebar.button("🚪 Se déconnecter"):
    delete_session(get_cookie_token())
    st.session_state.clear()
    st.session_state.just_logged_out = True
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🛠️ 🌲 Services & Actions")
menu = st.sidebar.selectbox(
    "Navigation",
    [
        "🔍 Services dans ma ville",
        "➕ Proposer un service",
        "📋 Mes services partagés",
    ],
)

category_icons = {
    "🛠 Bricolage & Réparation": "🛠️",
    "🌱 Jardinage & Extérieur": "🌱",
    "📚 Cours & Soutien scolaire": "📚",
    "🍳 Cuisine & Repas": "🍳",
    "🐾 Garde d'animaux": "🐾",
    "🚗 Transport & Covoiturage": "🚗",
    "💻 Informatique & Numérique": "💻",
    "✨ Autre service": "✨",
}

SERVICE_QUERY = """
    SELECT s.id, s.author_email, a.username, s.city, s.category, s.title,
           s.description, s.cost, s.status, s.completed_by_email, c.username
    FROM services s
    JOIN users a ON a.email = s.author_email
    LEFT JOIN users c ON c.email = s.completed_by_email
"""

if menu == "🔍 Services dans ma ville":
    st.header(f"📍 Services disponibles à {city_input}")

    with db() as conn:
        services = conn.execute(
            SERVICE_QUERY + " WHERE s.city = ? ORDER BY s.id DESC", (city_input,)
        ).fetchall()
        liked_ids = {
            r[0]
            for r in conn.execute(
                "SELECT service_id FROM likes WHERE user_email = ?", (current_email,)
            )
        }
        messages_by_service = {}
        for sid, sender, content in conn.execute(
            """SELECT m.service_id, u.username, m.content
               FROM messages m JOIN users u ON u.email = m.sender_email
               ORDER BY m.id"""
        ):
            messages_by_service.setdefault(sid, []).append((sender, content))

    if not services:
        st.info(
            f"Aucun service n'est proposé pour le moment à {city_input}. Soyez le"
            " premier à en lancer un !"
        )
    else:
        for (
            service_id, author_email, author, city, category, title,
            description, cost, status, completed_by_email, completed_by,
        ) in services:
            icon = category_icons.get(category, "✨")
            is_liked = service_id in liked_ids

            with st.container():
                st.markdown(
                    f"""
                    <div class="service-card">
                        <h3>{icon} {esc(title)}</h3>
                        <p><b>Catégorie :</b> {esc(category)} | <b>Proposé par :</b> @{esc(author)} ({esc(city)})</p>
                        <p><b>Coût :</b> {cost} crédits | <b>Statut :</b> <code>{esc(status)}</code></p>
                        <p><i>{esc(description)}</i></p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                like_label = "❤️ Liké" if is_liked else "🤍 Liker ce service"
                if st.button(like_label, key=f"like_{service_id}"):
                    with db() as conn:
                        if is_liked:
                            conn.execute(
                                "DELETE FROM likes WHERE user_email = ? AND service_id = ?",
                                (current_email, service_id),
                            )
                        else:
                            conn.execute(
                                "INSERT OR IGNORE INTO likes (user_email, service_id)"
                                " VALUES (?, ?)",
                                (current_email, service_id),
                            )
                    st.rerun()

                if status == "disponible" and author_email != current_email:
                    if st.button(
                        f"Prendre ce service ({cost} crédits)", key=f"take_{service_id}"
                    ):
                        error = take_service(service_id, current_email)
                        if error:
                            st.error(error)
                        else:
                            st.rerun()

                elif status == "en cours":
                    st.info(f"🔄 Réalisé par : **{completed_by}**")
                    if current_email in (author_email, completed_by_email) and st.button(
                        "Marquer comme terminé", key=f"finish_{service_id}"
                    ):
                        with db() as conn:
                            conn.execute(
                                "UPDATE services SET status = 'terminé' WHERE id = ?",
                                (service_id,),
                            )
                        st.rerun()

                with st.expander(f"💬 Discuter pour '{title}'"):
                    msgs = messages_by_service.get(service_id, [])
                    if msgs:
                        for sender, content in msgs:
                            st.text(f"@{sender} : {content}")
                    else:
                        st.write("Aucun message pour l'instant.")

                    with st.form(key=f"msg_form_{service_id}", clear_on_submit=True):
                        new_msg = st.text_input(
                            "Votre message", key=f"input_msg_{service_id}"
                        )
                        send_btn = st.form_submit_button("Envoyer")
                    if send_btn and new_msg.strip():
                        with db() as conn:
                            conn.execute(
                                "INSERT INTO messages (service_id, sender_email, content)"
                                " VALUES (?, ?, ?)",
                                (service_id, current_email, new_msg.strip()),
                            )
                        st.rerun()
                st.divider()

elif menu == "➕ Proposer un service":
    st.header("➕ Proposer un nouveau service")

    with st.form("service_form"):
        category = st.selectbox("Choisissez une catégorie", list(category_icons.keys()))
        title = st.text_input(
            "Titre du service (ex: Tonte de pelouse, Cours de maths...)"
        )
        description = st.text_area("Description détaillée de ce que vous proposez")
        cost = st.number_input("Coût en crédits demandé", min_value=1, value=5, step=1)
        submitted = st.form_submit_button("Publier le service")

    if submitted:
        if title.strip() and description.strip():
            with db() as conn:
                conn.execute(
                    """INSERT INTO services
                       (author_email, city, category, title, description, cost, status)
                       VALUES (?, ?, ?, ?, ?, ?, 'disponible')""",
                    (
                        current_email, city_input, category,
                        title.strip(), description.strip(), int(cost),
                    ),
                )
            st.success("Votre service a été publié avec succès !")
        else:
            st.error("Veuillez remplir tous les champs.")

elif menu == "📋 Mes services partagés":
    st.header(f"📋 Les services proposés par {current_username}")

    with db() as conn:
        my_services = conn.execute(
            SERVICE_QUERY + " WHERE s.author_email = ? ORDER BY s.id DESC",
            (current_email,),
        ).fetchall()

    if not my_services:
        st.info("Vous n'avez publié aucun service pour l'instant.")
    else:
        for (
            service_id, _ae, _au, city, category, title,
            description, cost, status, _ce, completed_by,
        ) in my_services:
            icon = category_icons.get(category, "✨")
            with st.container():
                st.markdown(
                    f"""
                    <div class="service-card">
                        <h3>{icon} {esc(title)}</h3>
                        <p><b>Catégorie :</b> {esc(category)} | <b>Ville :</b> {esc(city)}</p>
                        <p><b>Coût :</b> {cost} crédits | <b>Statut :</b> <code>{esc(status)}</code></p>
                        <p><i>{esc(description)}</i></p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if status == "en cours":
                    st.info(f"Pris en charge par : **{completed_by}**")
                elif status == "terminé":
                    st.success("Réalisé avec succès !")
                st.divider()

# ==========================================
# MON ESPACE PERSONNEL
# ==========================================
def badge(status):
    cls = {"disponible": "ok", "en cours": "wip", "terminé": "done"}.get(status, "ok")
    return f'<span class="badge {cls}">{esc(status)}</span>'


st.markdown("---")
st.markdown("<h2 class='space-title'>🏡 Mon espace personnel</h2>", unsafe_allow_html=True)

me = current_email
with db() as conn:
    published, taken, received_likes, done = conn.execute(
        """SELECT
             (SELECT COUNT(*) FROM services WHERE author_email = ?),
             (SELECT COUNT(*) FROM services WHERE completed_by_email = ?),
             (SELECT COUNT(*) FROM likes l JOIN services s ON s.id = l.service_id
                WHERE s.author_email = ?),
             (SELECT COUNT(*) FROM services WHERE status = 'terminé'
                AND (author_email = ? OR completed_by_email = ?))""",
        (me, me, me, me, me),
    ).fetchone()
    discussions = conn.execute(
        """SELECT u.username, s.title, m.content
           FROM messages m
           JOIN services s ON m.service_id = s.id
           JOIN users u ON u.email = m.sender_email
           WHERE m.sender_email != ?
             AND (s.author_email = ? OR s.completed_by_email = ?
                  OR m.service_id IN (
                      SELECT service_id FROM messages WHERE sender_email = ?))
           ORDER BY m.id DESC LIMIT 10""",
        (me, me, me, me),
    ).fetchall()
    city_likes = conn.execute(
        """SELECT s.title, a.username, lu.username
           FROM likes l
           JOIN services s ON l.service_id = s.id
           JOIN users a ON a.email = s.author_email
           JOIN users lu ON lu.email = l.user_email
           WHERE s.city = ? ORDER BY l.id DESC LIMIT 10""",
        (city_input,),
    ).fetchall()
    my_pubs = conn.execute(
        "SELECT title, category, status, cost FROM services"
        " WHERE author_email = ? ORDER BY id DESC",
        (me,),
    ).fetchall()
    my_taken = conn.execute(
        """SELECT s.title, a.username, s.status, s.cost
           FROM services s JOIN users a ON a.email = s.author_email
           WHERE s.completed_by_email = ? ORDER BY s.id DESC""",
        (me,),
    ).fetchall()

st.markdown(
    f"""<div class="profile-card">
<div class="avatar">{esc(current_username[:1].upper())}</div>
<div><h2>{esc(current_username)}</h2>
<p>📍 {esc(city_input)} &nbsp;·&nbsp; 📧 {esc(current_email)}</p></div>
</div>""",
    unsafe_allow_html=True,
)

stats = [
    ("💰", user_credits, "Crédits"),
    ("📋", published, "Publiés"),
    ("🤝", taken, "Services pris"),
    ("✅", done, "Terminés"),
    ("❤️", received_likes, "Likes reçus"),
]
for col, (icon, value, label) in zip(st.columns(len(stats)), stats):
    col.markdown(
        f'<div class="stat-card"><div class="stat-icon">{icon}</div>'
        f'<div class="stat-value">{value}</div>'
        f'<div class="stat-label">{label}</div></div>',
        unsafe_allow_html=True,
    )

st.write("")
tab_d, tab_l, tab_p, tab_t = st.tabs(
    ["💬 Discussions", "❤️ Likes", "📋 Mes publications", "🤝 Services pris"]
)

with tab_d:
    if not discussions:
        st.info("Aucune discussion active pour le moment.")
    for sender, title, content in discussions:
        st.markdown(
            f'<div class="mini-card">💬 <b>@{esc(sender)}</b> sur <i>{esc(title)}</i>'
            f'<br><small>"{esc(content)}"</small></div>',
            unsafe_allow_html=True,
        )

with tab_l:
    st.caption(f"Derniers likes à {city_input}")
    if not city_likes:
        st.info("Aucun like enregistré pour l'instant dans votre ville.")
    for title, author, liker in city_likes:
        st.markdown(
            f'<div class="mini-card">❤️ <b>@{esc(liker)}</b> a aimé <i>{esc(title)}</i>'
            f'<br><small>de @{esc(author)}</small></div>',
            unsafe_allow_html=True,
        )

with tab_p:
    if not my_pubs:
        st.info("Vous n'avez encore publié aucun service.")
    for title, cat, status, cost in my_pubs:
        st.markdown(
            f'<div class="mini-card">🔹 <b>{esc(title)}</b> {badge(status)}'
            f'<br><small>{esc(cat)} · 💰 {cost} pts</small></div>',
            unsafe_allow_html=True,
        )

with tab_t:
    if not my_taken:
        st.info("Vous n'avez pas encore pris de service.")
    for title, author, status, cost in my_taken:
        st.markdown(
            f'<div class="mini-card">🤝 <b>{esc(title)}</b> {badge(status)}'
            f'<br><small>proposé par @{esc(author)} · 💰 {cost} pts</small></div>',
            unsafe_allow_html=True,
        )
