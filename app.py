import streamlit as st
import os
import base64
import json
from groq import Groq
import google.generativeai as genai

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="AEGIS-CORE // BETA", 
    page_icon="🛡️", 
    layout="wide"
)

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

# Initialisation des états globaux
if "profiles" not in st.session_state:
    st.session_state.profiles = load_profiles()

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "sessions" not in st.session_state:
    st.session_state["sessions"] = {"Discussion 1": []}

if "session_active" not in st.session_state:
    st.session_state["session_active"] = "Discussion 1"

# --- INJECTION CSS & ANIMATION BRUME ---
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

    <div class="intro-overlay">
        AEGIS-CORE
        <div class="intro-sub">// PROTOCOLE BETA INITIALISE //</div>
    </div>
    
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

# --- MATRICE PROMPTS (20 THEMES PROMPT) ---
MATRICE_PROMPTS = {
    "Pedagogie, Quiz & Resumes": [
        "Genere un Quiz interactif de 5 questions a choix multiples base sur notre derniere discussion.",
        "Redige une fiche de synthese pedagogique claire et structuree du projet en cours.",
        "Concois un plan de formation étape par étape pour maîtriser ce sujet de A à Z.",
        "Genere une fiche de revision rapide sous forme de carte mentale textuelle."
    ],
    "Strategie & Geopolitique": [
        "Analyse les equilibres geopolitiques actuels avec une precision tactique.",
        "Evalue les risques strategiques d'un conflit technologique global.",
        "Dresse une cartographie des dependances en matieres premieres critiques."
    ],
    "Developpement & Code": [
        "Donne-moi une structure propre et modulaire pour un projet Python professionnel.",
        "Optimise un algorithme Python pour reduire la complexite temporelle.",
        "Concois une architecture REST API scalable avec FastAPI."
    ],
    "Entrepreneuriat & SaaS": [
        "Propose une idee de micro-SaaS B2B a fort potentiel avec un budget reduit.",
        "Dresse un plan d'acquisition client cible pour un outil SaaS de niche.",
        "Redige le Pitch Deck complet de 10 slides pour presenter un projet IA."
    ],
    "Analyse & Diagnostic Technique": [
        "Identifie la cause racine d'une panne systeme recurrente.",
        "Audite la securite d'une infrastructure Cloud AWS/GCP."
    ],
    "Creation de Contenu & Design": [
        "Redige un script de video court captivant des les 3 premieres secondes.",
        "Concois la charte editoriale complete d'une marque de technologie."
    ],
    "Cybersecurite & Protocoles": [
        "Redige une politique de securite des systemes d'information.",
        "Explique la mise en place d'une architecture Zero Trust."
    ],
    "Data Science & Finance": [
        "Propose un modele de prediction du Churn base sur le Machine Learning.",
        "Concois un pipeline ETL propre en Python avec Pandas et SQLAlchemy."
    ],
    "Ingenierie des IA & Prompts": [
        "Concois un System Prompt robuste pour garantir le respect strict des consignes.",
        "Propose une architecture RAG avec Vector DB."
    ],
    "GameDev & Moteurs 3D": [
        "Redige le cahier des charges de Game Design pour un jeu d'action.",
        "Explique la gestion de la physique et des collisions sous Unreal Engine 5."
    ],
    "Optimisation Systeme": [
        "Propose une methode pour reduire la latence d'une application web.",
        "Audite la consommation memoire d'un serveur Linux."
    ],
    "Cloud & DevOps": [
        "Redige un fichier Kubernetes complet pour un deploiement haute disponibilite.",
        "Concois un plan de migration d'un serveur physique vers le Cloud."
    ],
    "Growth Hacking": [
        "Propose 3 canaux de croissance virale a faible cout pour une nouvelle application.",
        "Redige une sequence d'e-mails de prospection B2B a fort taux de conversion."
    ],
    "Redaction Technique": [
        "Redige un fichier README.md professionnel et percutant pour un depot GitHub.",
        "Cree une documentation technique claire pour une API REST."
    ],
    "Ethique & Souverainete": [
        "Analyse les enjeux de la souverainete des donnees en Europe.",
        "Redige une charte ethique pour l'utilisation d'une IA au sein d'une organisation."
    ],
    "Veille Technologique": [
        "Dresse un panorama des innovations majeures en intelligence artificielle.",
        "Analyse l'impact de l'informatique quantique sur la cryptographie actuelle."
    ],
    "Product Management": [
        "Redige une User Story claire et detaillee avec ses criteres d'acceptation.",
        "Concois une matrice de priorisation des fonctionnalites d'un MVP."
    ],
    "Reseaux & Protocoles": [
        "Explique le fonctionnement du protocole DNS et les risques d'attaque.",
        "Detaille les couches du modele OSI avec un exemple concret."
    ],
    "R&D Scientifique": [
        "Propose une methodologie rigoureuse pour mener une experimentation scientifique.",
        "Redige un resume des avancees recentes dans les batteries a l'etat solide."
    ],
    "Maintenance & Resilience": [
        "Concois un plan de reprise d'activite en cas de panne majeure.",
        "Redige un rapport post-mortem suite a un incident de production."
    ]
}

# --- MATRICE DE PERSONNALISATION (30 THEMES x 30 PROPOSITIONS) ---
noms_themes_perso = [
    "Palette de Couleurs & Ambiance", "Typographie & Polices", "Taille & Echelle des Textes",
    "Avatars & Symboles Tactiques", "Disposition & Mise en Page", "Theme des Blocs de Code",
    "Densite d'Affichage & Spacing", "Mode Focus & Epure", "Horodatage & Metadonnees",
    "Langue & Registre de l'IA", "Tonalite & Style de Reponse", "Longueur Max & Verbosite",
    "Mode Resume & Synthese", "Message de Bienvenue", "Vitesse de Frappe & Streaming",
    "Alertes Sonores & Volume", "Effets Visuels & Brume", "Raccourcis Clavier & Envoi",
    "Historique & Incognito", "Mode Economie de Donnees", "Defilement Automatique",
    "Niveau de Rigueur & RAG", "Format des Explications (Bullet/Markdown)", "Gestion des Emojis",
    "Mise en Evidence des Hypotheses", "Prompt Systeme Personnalise", "Mode Console / Terminal",
    "Exportation des Discussions", "Gestion des Alertes Reseau", "Comportement de Repli (Fallback)"
