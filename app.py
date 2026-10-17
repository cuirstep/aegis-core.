streamlit as st
import os
import base64
from groq import Groq
import google.generativeai as genai

st.set_page_config(
    page_title="AEGIS-CORE // BETA", 
    page_icon="assets/aegis_logo.png" if os.path.exists("assets/aegis_logo.png") else "🛡️", 
    layout="wide"
)

# --- INJECTION CSS & ANIMATION BRUME (GÉRÉE EN PUR CSS/JS SANS BLOQUER) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {
        display: none !important;
    }
    
    /* --- ANIMATION BRUME DISPARITION AUTOMATIQUE --- */
    @keyframes brumeFadeOut {
        0% { opacity: 1; filter: blur(0px); visibility: visible; }
        75% { opacity: 1; filter: blur(3px); visibility: visible; }
        100% { opacity: 0; filter: blur(15px); visibility: hidden; display: none; }
    }

    .intro-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background-color: #000000;
        color: #ffffff;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 999999;
        pointer-events: none;
        animation: brumeFadeOut 2.8s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        font-family: monospace;
        letter-spacing: 8px;
        font-size: 3em;
        font-weight: bold;
    }
    
    .intro-sub {
        font-size: 0.35em;
        letter-spacing: 4px;
        color: #888888;
        margin-top: 10px;
    }
    </style>

    <!-- ÉCRAN D'INTRODUCTION CINÉMATIQUE -->
    <div class="intro-overlay">
        AEGIS-CORE
        <div class="intro-sub">// PROTOCOLE BÊTA INITIALISÉ //</div>
    </div>
    
    <!-- AUDIO MILITAIRE COURT (3 SECONDES) -->
    <audio autoplay style="display:none;">
        <source src="https://www.myinstants.com/media/sounds/metal-gear-solid-alert-sound.mp3" type="audio/mpeg">
    </audio>
""", unsafe_allow_html=True)

# --- FONCTIONS UTILITAIRES ---
def get_base64_img(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def custom_icon(path, size=24):
    b64 = get_base64_img(path)
    if b64:
        return f'<img src="data:image/png;base64,{b64}" width="{size}" style="vertical-align: middle; margin-right: 8px;">'
    return ""

# --- API KEYS & CONFIG ---
gemini_key = st.secrets.get("GEMINI_API_KEY", "")
github_token = st.secrets.get("GITHUB_TOKEN", "")
groq_keys = []
for i in range(1, 6):
    key = st.secrets.get(f"GROQ_API_KEY_{i}", "")
    if not key and i == 1:
        key = st.secrets.get("GROQ_API_KEY", "")
    if key:
        groq_keys.append(key)

if gemini_key:
    try:
        genai.configure(api_key=gemini_key)
    except Exception:
        pass

# --- MATRICE INTÉGRALE : 20 THÈMES ---
MATRICE_PROMPTS = {
    "🎓 Pédagogie, Quiz & Résumés": [
        "Genere un Quiz interactif de 5 questions a choix multiples base sur notre derniere discussion.",
        "Redige une fiche de synthese pedagogique claire et structuree du projet en cours.",
        "Concois un plan de formation étape par étape pour maîtriser ce sujet de A à Z.",
        "Genere une fiche de revision rapide sous forme de carte mentale textuelle."
    ],
    "🛡️ Stratégie & Géopolitique": [
        "Analyse les equilibres geopolitiques actuels avec une precision tactique.",
        "Evalue les risques strategiques d'un conflit technologique global.",
        "Dresse une cartographie des dependances en matieres premieres critiques."
    ],
    "💻 Développement & Code": [
        "Donne-moi une structure propre et modulaire pour un projet Python professionnel.",
        "Optimise un algorithme Python pour reduire la complexite temporelle.",
        "Concois une architecture REST API scalable avec FastAPI."
    ],
    "🚀 Entrepreneuriat & SaaS": [
        "Propose une idee de micro-SaaS B2B a fort potentiel avec un budget reduit.",
        "Dresse un plan d'acquisition client cible pour un outil SaaS de niche.",
        "Redige le Pitch Deck complet de 10 slides pour presenter un projet IA."
    ],
    "🧠 Analyse & Diagnostic Technique": [
        "Identifie la cause racine d'une panne systeme recurrente.",
        "Audite la securite d'une infrastructure Cloud AWS/GCP."
    ],
    "🎨 Création de Contenu & Design": [
        "Redige un script de video court captivant des les 3 premieres secondes.",
        "Concois la charte editoriale complete d'une marque de technologie."
    ],
    "🔒 Cybersécurité & Protocoles": [
        "Redige une politique de securite des systemes d'information.",
        "Explique la mise en place d'une architecture Zero Trust."
    ],
    "📊 Data Science & Finance": [
        "Propose un modele de prediction du Churn base sur le Machine Learning.",
        "Concois un pipeline ETL propre en Python avec Pandas et SQLAlchemy."
    ],
    "🤖 Ingénierie des IA & Prompts": [
        "Concois un System Prompt robuste pour garantir le respect strict des consignes.",
        "Propose une architecture RAG avec Vector DB."
    ],
    "🕹️ GameDev & Moteurs 3D": [
        "Redige le cahier des charges de Game Design pour un jeu d'action.",
        "Explique la gestion de la physique et des collisions sous Unreal Engine 5."
    ],
    "⚡ Optimisation Système": [
        "Propose une methode pour reduire la latence d'une application web.",
        "Audite la consommation memoire d'un serveur Linux."
    ],
    "☁️ Cloud & DevOps": [
        "Redige un fichier Kubernetes complet pour un deploiement haute disponibilite.",
        "Concois un plan de migration d'un serveur physique vers le Cloud."
    ],
    "📈 Growth Hacking": [
        "Propose 3 canaux de croissance virale a faible cout pour une nouvelle application.",
        "Redige une sequence d'e-mails de prospection B2B a fort taux de conversion."
    ],
    "📝 Rédaction Technique": [
        "Redige un fichier README.md professionnel et percutant pour un depot GitHub.",
        "Cree une documentation technique claire pour une API REST."
    ],
    "⚖️ Éthique & Souveraineté": [
        "Analyse les enjeux de la souverainete des donnees en Europe.",
        "Redige une charte ethique pour l'utilisation d'une IA au sein d'une organisation."
    ],
    "🔮 Veille Technologique": [
        "Dresse un panorama des innovations majeures en intelligence artificielle.",
        "Analyse l'impact de l'informatique quantique sur la cryptographie actuelle."
    ],
    "🎯 Product Management": [
        "Redige une User Story claire et detaillee avec ses criteres d'acceptation.",
        "Concois une matrice de priorisation des fonctionnalites d'un MVP."
    ],
    "🌐 Réseaux & Protocoles": [
        "Explique le fonctionnement du protocole DNS et les risques d'attaque.",
        "Detaille les couches du modele OSI avec un exemple concret."
    ],
    "🧪 R&D Scientifique": [
        "Propose une methodologie rigoureuse pour mener une experimentation scientifique.",
        "Redige un resume des avancees recentes dans les batteries a l'etat solide."
    ],
    "🛠️ Maintenance & Résilience": [
        "Concois un plan de reprise d'activite en cas de panne majeure.",
        "Redige un rapport post-mortem suite a un incident de production."
    ]
}

# --- MULTI-SESSIONS ---
if "sessions" not in st.session_state:
    st.session_state["sessions"] = {"Discussion 1": []}
if "session_active" not in st.session_state:
    st.session_state["session_active"] = "Discussion 1"

# --- SIDEBAR ---
quick_action = None

with st.sidebar:
    if os.path.exists("assets/aegis_logo.png"):
        st.image("assets/aegis_logo.png", width=120)
    
    icon_sessions = custom_icon("assets/aegis_sessions.png")
    st.markdown(f"### {icon_sessions} MULTI-SESSIONS", unsafe_allow_html=True)
    
    if st.button("➕ Nouvelle discussion"):
        new_name = f"Discussion {len(st.session_state['sessions']) + 1}"
        st.session_state["sessions"][new_name] = []
        st.session_state["session_active"] = new_name
        st.rerun()

    session_choisie = st.selectbox("Sessions enregistrées :", list(st.session_state["sessions"].keys()), index=list(st.session_state["sessions"].keys()).index(st.session_state["session_active"]))
    if session_choisie != st.session_state["session_active"]:
        st.session_state["session_active"] = session_choisie
        st.rerun()

    st.markdown("---")
    icon_code = custom_icon("assets/aegis_code.png")
    st.markdown(f"### {icon_code} MATRICE DE COMMANDES", unsafe_allow_html=True)
    theme_choisi = st.selectbox("Domaine :", list(MATRICE_PROMPTS.keys()))
    prompt_selectionne = st.selectbox("Commande :", MATRICE_PROMPTS[theme_choisi])
    
    if st.button("🚀 Injecter le prompt"):
        quick_action = prompt_selectionne

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = (
    "Tu es AEGIS-CORE (Version Bêta), un systeme d'IA souverain developpe par le Commandant. "
    "Tu es ultra-performant, direct et rigoureux. "
    "Si tu emets une hypothese ou une deduction, étiquette-la OBLIGATOIREMENT par '[HYPOTHESE / DEDUCTION]'."
)

# --- INTERFACE PRINCIPALE ---
col_logo, col_title = st.columns([0.12, 0.88])
with col_logo:
    if os.path.exists("assets/aegis_logo.png"):
        st.image("assets/aegis_logo.png", width=80)
    else:
        st.markdown("🛡️")
with col_title:
    st.markdown(f"### AEGIS-CORE // {st.session_state['session_active'].upper()} (BÊTA)")
    st.caption(f"Domaine actif : **{theme_choisi}**")

st.markdown("---")

messages_actuels = st.session_state["sessions"][st.session_state["session_active"]]

for message in messages_actuels:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- GESTION DE LA SAISIE & ÉDITION ---
prompt_a_traiter = None

if messages_actuels:
    dernier_index_user = -1
    for idx, m in enumerate(reversed(messages_actuels)):
        if m["role"] == "user":
            dernier_index_user = len(messages_actuels) - 1 - idx
            break
            
    if dernier_index_user != -1:
        with st.expander("✏️ Modifier votre dernière directive"):
            nouveau_texte = st.text_input("Ajustez votre consigne :", value=messages_actuels[dernier_index_user]["content"], key=f"edit_txt_{st.session_state['session_active']}")
            if st.button("Mettre à jour et relancer", key=f"btn_edit_run_{st.session_state['session_active']}"):
                st.session_state["sessions"][st.session_state["session_active"]] = messages_actuels[:dernier_index_user]
                prompt_a_traiter = nouveau_texte
                st.rerun()

# Récupération de la saisie (Chat input, Quick Action ou Édition)
prompt_input = st.chat_input("Entrez votre directive, Commandant...")
if quick_action:
    prompt_input = quick_action
if prompt_a_traiter:
    prompt_input = prompt_a_traiter

# --- TRAITEMENT DU PROMPT ET APPEL AUX LLM ---
if prompt_input:
    messages_actuels.append({"role": "user", "content": prompt_input})
    with st.chat_message("user"):
        st.markdown(prompt_input)

    with st.chat_message("assistant"):
        reponse_finale = ""
        succes = False

        if gemini_key and not succes:
            for model_name in ["gemini-2.5-flash", "gemini-1.5-flash"]:
                try:
                    model = genai.GenerativeModel(model_name=model_name, system_instruction=SYSTEM_PROMPT)
                    chat_history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in messages_actuels[:-1]]
                    chat = model.start_chat(history=chat_history)
                    response = chat.send_message(prompt_input, stream=True)

                    def generate_fast_stream():
                        for chunk in response:
                            if chunk.text:
                                for char in chunk.text:
                                    yield char
                                    import time
                                    time.sleep(0.0001)

                    reponse_finale = st.write_stream(generate_fast_stream())
                    succes = True
                    break
                except Exception:
                    pass

        if groq_keys and not succes:
            messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}] + [{"role": m["role"], "content": m["content"]} for m in messages_actuels]
            for g_key in groq_keys:
                try:
                    client = Groq(api_key=g_key)
                    stream = client.chat.completions.create(
                        model="openai/gpt-oss-20b", 
                        messages=messages_payload, 
                        stream=True
                    )
                    
                    def generate_groq_fast():
                        for chunk in stream:
                            content = chunk.choices[0].delta.content
                            if content:
                                for char in content:
                                    yield char
                                    import time
                                    time.sleep(0.0001)

                    reponse_finale = st.write_stream(generate_groq_fast())
                    succes = True
                    break
                except Exception:
                    pass

        if not succes:
            reponse_finale = "❌ Erreur de réseau : Les canaux distants ne répondent pas."
            st.markdown(reponse_finale)

        messages_actuels.append({"role": "assistant", "content": reponse_finale})
import streamlit as st

# --- CONFIGURATION INITIALE DES ÉTATS ---
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "user_logged" not in st.session_state:
    st.session_state.user_logged = False

if "user_profiles" not in st.session_state:
    # Stockage temporaire des profils utilisateurs créés (pseudo -> mot de passe)
    st.session_state.user_profiles = {}

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# --- BARRE LATÉRALE : GESTION DES ESPACES ---
with st.sidebar:
    st.title("🛡️ AEGIS-CORE")
    st.markdown("---")
    
    # --- SECTION 1 : ESPACE UTILISATEUR (Personnalisation & Sécurité) ---
    st.subheader("👤 Espace Utilisateur")
    
    if not st.session_state.user_logged:
        user_choice = st.radio("Action", ["Se connecter", "Créer un profil"], key="user_mode_radio")
        
        if user_choice == "Créer un profil":
            new_pseudo = st.text_input("Choisissez votre pseudo", key="new_user_pseudo")
            pass1 = st.text_input("Mot de passe", type="password", key="new_pass1")
            pass2 = st.text_input("Confirmez le mot de passe", type="password", key="new_pass2")
            
            if st.button("Enregistrer mon profil"):
                if not new_pseudo or not pass1:
                    st.error("Veuillez remplir tous les champs.")
                elif pass1 != pass2:
                    st.error("Les deux mots de passe ne correspondent pas.")
                elif new_pseudo in st.session_state.user_profiles:
                    st.error("Ce pseudo existe déjà.")
                else:
                    st.session_state.user_profiles[new_pseudo] = pass1
                    st.success("Profil créé avec succès ! Connectez-vous.")
        
        else: # Se connecter
            login_pseudo = st.text_input("Votre pseudo", key="login_pseudo")
            login_pass = st.text_input("Mot de passe", type="password", key="login_pass")
            
            if st.button("Connexion Utilisateur"):
                if login_pseudo in st.session_state.user_profiles and st.session_state.user_profiles[login_pseudo] == login_pass:
                    st.session_state.user_logged = True
                    st.session_state.current_user = login_pseudo
                    st.success(f"Bienvenue, {login_pseudo} !")
                    st.rerun()
                else:
                    st.error("Pseudo ou mot de passe incorrect.")
    else:
        st.success(connect_msg := f"Connecté en tant que : **{st.session_state.current_user}**")
        if st.button("Déconnexion Utilisateur"):
            st.session_state.user_logged = False
            st.session_state.current_user = None
            st.rerun()

    st.markdown("---")

    # --- SECTION 2 : ESPACE COMMANDANT (Admin Total) ---
    st.subheader("🔐 Espace Commandant")
    
    if not st.session_state.is_admin:
        admin_input = st.text_input("Code Commandant", type="password", key="admin_code_input")
        if st.button("Déverrouiller Admin"):
            # Récupère le code admin depuis les secrets Streamlit (ou "AEGIS2026" par défaut)
            correct_admin_code = st.secrets.get("ADMIN_CODE", "AEGIS2026")
            if admin_input == correct_admin_code:
                st.session_state.is_admin = True
                st.success("Accès Commandant accordé !")
                st.rerun()
            else:
                st.error("Code Commandant incorrect.")
    else:
        st.success("🟢 Mode Commandant Actif (100% Droits)")
        if st.button("Verrouiller l'Admin"):
            st.session_state.is_admin = False
            st.rerun()

# --- CORPS PRINCIPAL DE L'APPLICATION ---
st.title("AEGIS-CORE — Interface Souveraine")

# 1. Si le Commandant est connecté : Accès total aux réglages avancés et au noyau
if st.session_state.is_admin:
    st.markdown("### 🛠️ Panneau de Contrôle Avancé (Réservé au Commandant)")
    st.info("Vous avez le contrôle total sur le système, les clés API, les logs et la configuration globale.")
    
    # Exemple de commande admin sécurisée
    with st.expander("⚙️ Paramètres système et maintenance"):
        st.write(f"Profils utilisateurs enregistrés : {len(st.session_state.user_profiles)}")
        if st.button("Purger les profils utilisateurs"):
            st.session_state.user_profiles = {}
            st.success("Base des profils vidée.")

# 2. Si un utilisateur classique est connecté : Personnalisation sécurisée sans risque de tout casser
elif st.session_state.user_logged:
    st.markdown(f"### 🎛️ Espace de Personnalisation de {st.session_state.current_user}")
    st.write("Ici, vous pouvez personnaliser votre expérience AEGIS (choix des thèmes, préférences d'affichage) en toute sécurité.")
    
    # Paramètres utilisateur inoffensifs pour l'app
    user_theme = st.selectbox("Choisir l'ambiance visuelle de votre interface :", ["Défaut (Brume cinématique)", "Mode Clair", "Mode Nuit Profond"])
    user_notifications = st.checkbox("Activer les alertes sonores personnalisées", value=True)
    
    if st.button("Sauvegarder mes préférences"):
        st.success("Préférences enregistrées avec succès !")

# 3. Si personne n'est connecté : Accueil général et Chat public
else:
    st.warning("⚠️ Veuillez vous connecter via la barre latérale pour accéder à votre espace personnalisé ou lancer le chat.")
    st.markdown("Bienvenue sur la version Bêta d'AEGIS-CORE. L'intelligence souveraine du peuple.")
import streamlit as st
import json
import os

# --- PERSISTANCE DES PROFILS UTILISATEURS ---
USER_DB_FILE = "user_profiles.json"

def load_profiles():
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_profiles(profiles):
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=2)

# Initialize Session State
if "profiles" not in st.session_state:
    st.session_state.profiles = load_profiles()

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# --- BARRE LATÉRALE : CONNEXION & SÉCURITÉ ---
with st.sidebar:
    st.title("🛡️ AEGIS-CORE")
    st.markdown("---")

    # SECTION UTILISATEUR
    if not st.session_state.current_user:
        st.subheader("👤 Espace Membre")
        tab_login, tab_register = st.tabs(["Connexion", "Créer un compte"])

        with tab_register:
            new_user = st.text_input("Pseudo", key="reg_user")
            p1 = st.text_input("Mot de passe", type="password", key="reg_p1")
            p2 = st.text_input("Confirmez le mot de passe", type="password", key="reg_p2")
            if st.button("Valider la création"):
                if not new_user or not p1:
                    st.error("Champs incomplets.")
                elif p1 != p2:
                    st.error("Les mots de passe ne correspondent pas.")
                elif new_user in st.session_state.profiles:
                    st.error("Ce pseudo existe déjà.")
                else:
                    # Création du profil avec options par défaut
                    st.session_state.profiles[new_user] = {
                        "password": p1,
                        "config": {
                            "theme": "Sombre Cinématique",
                            "font_size": "Moyenne",
                            "sound": True,
                            "speed": "Normale",
                            "avatar": "🛡️",
                            "density": "Équilibré",
                            "summary_mode": False,
                            "auto_scroll": True,
                            "lang": "Français",
                            "tone": "Factuel & Précis",
                            "code_theme": "Dark Plus",
                            "display_timestamp": True,
                            "max_tokens": 1000,
                            "welcome_msg": True,
                            "shortcut_keys": True,
                            "privacy_mode": False,
                            "data_saver": False,
                            "layout": "Plein écran",
                            "focus_mode": False,
                            "alert_level": "Moyenne"
                        }
                    }
                    save_profiles(st.session_state.profiles)
                    st.success("Compte créé avec succès ! Connectez-vous.")

        with tab_login:
            log_user = st.text_input("Pseudo", key="log_user")
            log_pass = st.text_input("Mot de passe", type="password", key="log_pass")
            if st.button("Se connecter"):
                profiles = st.session_state.profiles
                if log_user in profiles and profiles[log_user]["password"] == log_pass:
                    st.session_state.current_user = log_user
                    st.success(f"Bienvenue {log_user} !")
                    st.rerun()
                else:
                    st.error("Identifiants incorrects.")
    else:
        st.success(f"Connecté : **{st.session_state.current_user}**")
        if st.button("Déconnexion"):
            st.session_state.current_user = None
            st.rerun()

    st.markdown("---")

    # SECTION COMMANDANT (ADMIN)
    if not st.session_state.is_admin:
        with st.expander("🔐 Espace Commandant"):
            admin_code = st.text_input("Code Secret", type="password", key="admin_key")
            if st.button("Authentification Admin"):
                if admin_code == st.secrets.get("ADMIN_CODE", "AEGIS2026"):
                    st.session_state.is_admin = True
                    st.success("Accès Commandant activé.")
                    st.rerun()
                else:
                    st.error("Code refusé.")
    else:
        st.info("🟢 Mode Commandant Total")
        if st.button("Verrouiller Admin"):
            st.session_state.is_admin = False
            st.rerun()

# --- INTERFACE PRINCIPALE ---
st.title("AEGIS-CORE — Plateforme Souveraine")

# 1. MODE COMMANDANT (Contrôle total du système)
if st.session_state.is_admin:
    st.header("🛠️ Panneau de Contrôle Global (Commandant)")
    st.warning("Accès complet aux données, profils et diagnostics du serveur.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Nombre de comptes enregistrés", len(st.session_state.profiles))
    with col2:
        if st.button("Réinitialiser tous les profils utilisateurs"):
            st.session_state.profiles = {}
            save_profiles({})
            st.success("Base de données purgée.")

    with st.expander("📋 Liste des utilisateurs inscrits"):
        st.write(list(st.session_state.profiles.keys()))

# 2. MODE UTILISATEUR (20+ Options de Personnalisation)
elif st.session_state.current_user:
    user = st.session_state.current_user
    config = st.session_state.profiles[user]["config"]

    st.header(f"⚙️ Personnalisation de l'interface — {user}")
    st.caption("Ajustez vos préférences sans affecter les autres membres ni le code source.")

    tab1, tab2, tab3, tab4 = st.tabs(["🎨 Visuel & Theme", "🤖 Comportement de l'IA", "🔊 Audio & Notifications", "🔒 Confidentialité & Performance"])

    with tab1:
        st.subheader("Apparence & Affichage (8 Options)")
        config["theme"] = st.selectbox("1. Ambiance visuelle", ["Sombre Cinématique", "Cyberpunk Gold", "Mode Épuré", "Nuit Profonde"], index=0)
        config["font_size"] = st.select_slider("2. Taille de police", options=["Petite", "Moyenne", "Grande", "Très Grande"], value=config.get("font_size", "Moyenne"))
        config["avatar"] = st.selectbox("3. Avatar utilisateur", ["🛡️", "⚔️", "🦅", "⚡", "👤"], index=0)
        config["layout"] = st.radio("4. Disposition de la page", ["Centré", "Plein écran"], index=1)
        config["code_theme"] = st.selectbox("5. Thème des blocs de code", ["Dark Plus", "Monokai", "GitHub Dark", "Solarized Light"])
        config["density"] = st.select_slider("6. Densité d'affichage", options=["Compact", "Équilibré", "Aéré"])
        config["focus_mode"] = st.checkbox("7. Activer le Mode Focus (masque les détails superflus)", value=config.get("focus_mode", False))
        config["display_timestamp"] = st.checkbox("8. Afficher l'horodatage des messages", value=config.get("display_timestamp", True))

    with tab2:
        st.subheader("Réponses de l'IA (6 Options)")
        config["lang"] = st.selectbox("9. Langue principale de réponse", ["Français", "Anglais", "Espagnol", "Allemand"])
        config["tone"] = st.selectbox("10. Style de réponse", ["Factuel & Précis", "Analytique & Détaillé", "Pédagogique", "Direct & Concis"])
        config["max_tokens"] = st.slider("11. Longueur maximale des réponses", 200, 2000, config.get("max_tokens", 1000), step=100)
        config["summary_mode"] = st.checkbox("12. Générer automatiquement un résumé en fin de réponse", value=config.get("summary_mode", False))
        config["welcome_msg"] = st.checkbox("13. Afficher le message d'accueil personnalisé à l'ouverture", value=config.get("welcome_msg", True))
        config["speed"] = st.select_slider("14. Vitesse de frappe de l'IA", options=["Instantanée", "Normale", "Lente (Effet Machine à écrire)"])

    with tab3:
        st.subheader("Sons & Alertes (3 Options)")
        config["sound"] = st.checkbox("15. Activer le signal sonore d'alerte militaire (3 sec)", value=config.get("sound", True))
        config["alert_level"] = st.select_slider("16. Volume / Intensité sonore", options=["Discret", "Moyenne", "Maximum"])
        config["shortcut_keys"] = st.checkbox("17. Raccourcis clavier d'envoi rapide (Ctrl+Entrée)", value=config.get("shortcut_keys", True))

    with tab4:
        st.subheader("Sécurité & Réseau (3 Options)")
        config["privacy_mode"] = st.checkbox("18. Mode Incognito (ne garde pas l'historique de session local)", value=config.get("privacy_mode", False))
        config["data_saver"] = st.checkbox("19. Économie de données (Désactive les animations lourdes/brume)", value=config.get("data_saver", False))
        config["auto_scroll"] = st.checkbox("20. Défilement automatique vers le bas à chaque nouveau message", value=config.get("auto_scroll", True))

    st.markdown("---")
    if st.button("💾 Enregistrer mes réglages"):
        st.session_state.profiles[user]["config"] = config
        save_profiles(st.session_state.profiles)
        st.success("Toutes vos préférences ont été sauvegardées de manière permanente !")

# 3. PAGE D'ACCUEIL POUR VISITATIONS
else:
    st.info("👋 Veuillez vous connecter ou créer un compte dans le menu de gauche pour personnaliser votre espace.")
    st.markdown("### Interface Souveraine AEGIS-CORE")
