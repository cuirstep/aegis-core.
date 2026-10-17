import streamlit as st
import os
import base64
import json
import time
from llm_router import route_and_generate

# Importation des fonctions SQLite depuis database.py
from database import init_db, register_user, verify_user, init_chat_db, save_user_session, load_user_sessions

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="AEGIS-CORE // BETA", 
    page_icon="🛡️", 
    layout="wide"
)

# Initialisation des bases de données SQLite au démarrage
init_db()
init_chat_db()

# --- INITIALISATION DES ÉTATS GLOBAUX ---
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# Synchronisation des sessions avec SQLite
if "sessions" not in st.session_state:
    if st.session_state.current_user:
        st.session_state["sessions"] = load_user_sessions(st.session_state.current_user)
    else:
        st.session_state["sessions"] = {"Discussion 1": []}

if "session_active" not in st.session_state or st.session_state["session_active"] not in st.session_state["sessions"]:
    st.session_state["session_active"] = list(st.session_state["sessions"].keys())[0]

# --- INJECTION CSS & ANIMATION BRUME (Jouée une seule fois) ---
if "intro_played" not in st.session_state:
    st.session_state["intro_played"] = True
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
            70% { opacity: 1; filter: blur(3px); visibility: visible; }
            100% { opacity: 0; filter: blur(15px); visibility: hidden; pointer-events: none; }
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
            animation: brumeFadeOut 2.0s cubic-bezier(0.4, 0, 0.2, 1) forwards;
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
    """, unsafe_allow_html=True)

# --- MATRICE PROMPTS (20 DOMAINES) ---
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
        "Explique la physique et les collisions sous Unreal Engine 5."
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

# --- BARRE LATERALE ---
quick_action = None

with st.sidebar:
    st.subheader("Espace Membre")
    if not st.session_state.current_user:
        auth_mode = st.radio("Mode", ["Connexion", "Créer un compte"], key="auth_radio")

        if auth_mode == "Créer un compte":
            new_user = st.text_input("Pseudo", key="reg_user")
            p1 = st.text_input("Mot de passe", type="password", key="reg_p1")
            p2 = st.text_input("Confirmez le mot de passe", type="password", key="reg_p2")
            if st.button("Valider la création"):
                if not new_user or not p1:
                    st.error("Champs incomplets.")
                elif p1 != p2:
                    st.error("Les mots de passe ne correspondent pas.")
                else:
                    success, msg = register_user(new_user, p1)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
        else:
            log_user = st.text_input("Pseudo", key="log_user")
            log_pass = st.text_input("Mot de passe", type="password", key="log_pass")
            if st.button("Se connecter"):
                if verify_user(log_user, log_pass):
                    st.session_state.current_user = log_user
                    st.session_state["sessions"] = load_user_sessions(log_user)
                    st.session_state["session_active"] = list(st.session_state["sessions"].keys())[0]
                    st.success(f"Bienvenue {log_user} !")
                    st.rerun()
                else:
                    st.error("Identifiants incorrects.")
    else:
        st.success(f"Connecté : **{st.session_state.current_user}**")
        if st.button("Déconnexion"):
            st.session_state.current_user = None
            st.session_state["sessions"] = {"Discussion 1": []}
            st.session_state["session_active"] = "Discussion 1"
            st.rerun()

    st.markdown("---")

    # ESPACE COMMANDANT (ADMIN)
    if not st.session_state.is_admin:
        with st.expander("Espace Commandant"):
            admin_code = st.text_input("Code Secret", type="password", key="admin_key")
            if st.button("Authentification Admin"):
                correct_admin_code = st.secrets.get("ADMIN_CODE", "AEGIS2026")
                if admin_code == correct_admin_code:
                    st.session_state.is_admin = True
                    st.success("Accès Commandant activé.")
                    st.rerun()
                else:
                    st.error("Code refusé.")
    else:
        st.info("Mode Commandant Total")
        if st.button("Verrouiller Admin"):
            st.session_state.is_admin = False
            st.rerun()

    st.markdown("---")

    # MULTI-SESSIONS (Persistées en SQLite)
    st.markdown("### MULTI-SESSIONS")
    if st.button("Nouvelle discussion"):
        new_name = f"Discussion {len(st.session_state['sessions']) + 1}"
        st.session_state["sessions"][new_name] = []
        st.session_state["session_active"] = new_name
        if st.session_state.current_user:
            save_user_session(st.session_state.current_user, new_name, [])
        st.rerun()

    session_keys = list(st.session_state["sessions"].keys())
    session_index = session_keys.index(st.session_state["session_active"]) if st.session_state["session_active"] in session_keys else 0
    session_choisie = st.selectbox("Sessions enregistrées :", session_keys, index=session_index)
    
    if session_choisie != st.session_state["session_active"]:
        st.session_state["session_active"] = session_choisie
        st.rerun()

    st.markdown("---")

    # MATRICE DE COMMANDES
    st.markdown("### MATRICE DE COMMANDES")
    theme_choisi = st.selectbox("Domaine Prompt :", list(MATRICE_PROMPTS.keys()))
    prompt_selectionne = st.selectbox("Commande :", MATRICE_PROMPTS[theme_choisi])
    
    if st.button("Injecter le prompt"):
        quick_action = prompt_selectionne

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = (
    "Tu es AEGIS-CORE (Version Beta), un systeme d'IA souverain developpe par le Commandant. "
    "Tu es ultra-performant, direct et rigoureux. "
    "Si tu emets une hypothese ou une deduction, étiquette-la OBLIGATOIREMENT par '[HYPOTHESE / DEDUCTION]'."
)

# --- INTERFACE PRINCIPALE ---
st.markdown(f"### AEGIS-CORE // {st.session_state['session_active'].upper()} (BETA)")
st.caption(f"Domaine actif : **{theme_choisi}**")

st.markdown("---")

# PANNEAU ADMIN COMMANDANT
if st.session_state.is_admin:
    st.header("Panneau de Controle Global (Commandant)")
    st.warning("Acces complet aux donnees, profils et diagnostics du serveur.")
    if st.button("Reinitialiser toutes les sessions (Danger)"):
        st.success("Opération simulée.")
    st.markdown("---")

# --- GESTION DU CHAT & PERSISTANCE ---
messages_actuels = st.session_state["sessions"][st.session_state["session_active"]]

for message in messages_actuels:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
     
