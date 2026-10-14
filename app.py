import streamlit as st
import os
import time
import base64
from datetime import datetime
from groq import Groq
import google.generativeai as genai

st.set_page_config(
    page_title="AEGIS-CORE // BETA", 
    page_icon="assets/aegis_logo.png" if os.path.exists("assets/aegis_logo.png") else "🛡️", 
    layout="wide"
)

# --- INJECTION CSS (DESIGN ÉPURÉ NOIR & BLANC, ANIMATION BRUME & AUDIO) ---
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
    
    /* --- ANIMATION BRUME & INTRO AEGIS (3 SECONDES) --- */
    @keyframes brumeIntro {
        0% { opacity: 0; filter: blur(20px); transform: scale(1.1); }
        50% { opacity: 1; filter: blur(5px); transform: scale(1.02); }
        100% { opacity: 0; filter: blur(0px); transform: scale(1); display: none; }
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
        z-index: 99999;
        animation: brumeIntro 3.2s ease-out forwards;
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

    <!-- ÉCRAN D'INTRODUCTION CINÉMATIQUE (BÊTA) -->
    <div class="intro-overlay">
        AEGIS-CORE
        <div class="intro-sub">// PROTOCOLE BÊTA INITIALISÉ //</div>
    </div>
    
    <!-- SYNTHÈSE VOCALE / AUDIO MILITAIRE COURT (3 SECONDES) -->
    <audio autoplay style="display:none;">
        <source src="https://www.myinstants.com/media/sounds/metal-gear-solid-alert-sound.mp3" type="audio/mpeg">
    </audio>
""", unsafe_allow_html=True)

# --- FONCTION POUR CHARGER LES ÉMOJIS D'ÉLITE ---
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

# --- MATRICE PROMPTS ---
MATRICE_PROMPTS = {
    "Pédagogie, Quiz & Résumés": [
        "Genere un Quiz interactif de 5 questions a choix multiples base sur notre derniere discussion.",
        "Redige une fiche de synthese pedagogique claire et structuree du projet en cours.",
        "Concois un plan de formation étape par étape pour maîtriser ce sujet de A à Z.",
        "Genere une fiche de revision rapide sous forme de carte mentale textuelle."
    ],
    "Stratégie & Géopolitique": [
        "Analyse les equilibres geopolitiques actuels avec une precision tactique.",
        "Evalue les risques strategiques d'un conflit technologique global.",
        "Dresse une cartographie des dependances en matieres premieres critiques."
    ],
    "Développement & Code": [
        "Donne-moi une structure propre et modulaire pour un projet Python professionnel.",
        "Optimise un algorithme Python pour reduire la complexite temporelle.",
        "Conçois une architecture REST API scalable avec FastAPI."
    ],
    "Entrepreneuriat & SaaS": [
        "Propose une idee de micro-SaaS B2B a fort potentiel avec un budget reduit.",
        "Dresse un plan d'acquisition client cible pour un outil SaaS de niche.",
        "Redige le Pitch Deck complet de 10 slides pour presenter un projet IA."
    ]
}

# --- MULTI-SESSIONS ---
if "sessions" not in st.session_state:
    st.session_state["sessions"] = {"Discussion 1": []}
if "session_active" not in st.session_state:
    st.session_state["session_active"] = "Discussion 1"

# --- SIDEBAR (ÉPURÉE SANS HORLOGE NI GUIDE) ---
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

# --- SYSTEM
