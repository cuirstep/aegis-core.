import os
import json
import base64
import time
import requests
import io
import streamlit as st
from llm_router import route_and_generate

def text_to_speech_elevenlabs(text, langue="fr"):
    api_key = st.secrets.get("ELEVENLABS_API_KEY", "")
    if not api_key:
        return None
        
    voix_par_langue = {
        "fr": "xclXfpLYbMIBNgiHTm8S",
        "en": "DODLEQrClDo8wCz460ld",
        "es": "U9TSK9KHMlMU2qkeXlQP",
        "ar": "Ywuz3KyW2N5pqKNpwcCL",
        "pt": "IKpiSijWzlhOL6uX83EH"
    }
    
    voice_id = voix_par_langue.get(langue, "xclXfpLYbMIBNgiHTm8S")
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.content
    except Exception:
        pass
    return None
    
from database import init_db, register_user, verify_user, init_chat_db, save_user_session, load_user_sessions

st.set_page_config(
    page_title="AEGIS-CORE // BETA", 
    page_icon="🛡️", 
    layout="wide"
)

init_db()
init_chat_db()

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "sessions" not in st.session_state:
    if st.session_state.current_user:
        st.session_state["sessions"] = load_user_sessions(st.session_state.current_user)
    else:
        st.session_state["sessions"] = {"Discussion 1": []}

if "session_active" not in st.session_state or st.session_state["session_active"] not in st.session_state["sessions"]:
    st.session_state["session_active"] = list(st.session_state["sessions"].keys())[0]

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    [data-testid="stChatMessageAvatarUser"], 
    [data-testid="stChatMessageAvatarAssistant"],
    .stChatMessageAvatar,
    div[data-testid="chatAvatarIcon-user"],
    div[data-testid="chatAvatarIcon-assistant"] {
        display: none !important;
        visibility: hidden !important;
        width: 0px !important;
        height: 0px !important;
        margin: 0px !important;
        padding: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

MATRICE_PROMPTS = {
    "Pedagogie, Quiz & Resumes": [
        "Genere un Quiz interactif de 5 questions a choix multiples base sur notre derniere discussion.",
        "Redige une fiche de synthese pedagogique claire et structuree du projet en cours.",
        "Concois un plan de formation étape par étape pour maîtriser ce sujet de A à Z.",
        "Genere une fiche de revision rapide sous forme de carte mentale textuelle."
    ],
    "Developpement & Code": [
        "Donne-moi une structure propre et modulaire pour un projet Python professionnel.",
        "Optimise un algorithme Python pour reduire la complexite temporelle.",
        "Concois une architecture REST API scalable avec FastAPI."
    ],
    "Cybersecurite & Protocoles": [
        "Redige une politique de securite des systemes d'information.",
        "Explique la mise en place d'une architecture Zero Trust."
    ],
    "Ingenierie des IA & Prompts": [
        "Concois un System Prompt robuste pour garantir le respect strict des consignes.",
        "Propose une architecture RAG avec Vector DB."
    ]
}

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

    st.markdown("### MATRICE DE COMMANDES")
    theme_choisi = st.selectbox("Domaine Prompt :", list(MATRICE_PROMPTS.keys()))
    prompt_selectionne = st.selectbox("Commande :", MATRICE_PROMPTS[theme_choisi])
    
    if st.button("Injecter le prompt"):
        quick_action = prompt_selectionne

SYSTEM_PROMPT = (
    "Tu es AEGIS-CORE (Version Beta), un systeme d'IA souverain developpé par le Commandant. "
    "Tu es ultra-performant, direct, chaleureux et rigoureux. Quand on te salue, réponds de manière courtoise et professionnelle. "
    "Si tu emets une hypothese ou une deduction, étiquette-la OBLIGATOIREMENT par '[HYPOTHESE / DEDUCTION]'."
)

st.markdown(f"### AEGIS-CORE // {st.session_state['session_active'].upper()} (BETA)")
st.caption(f"Domaine actif : **{theme_choisi}**")
st.markdown("---")

messages_actuels = st.session_state["sessions"][st.session_state["session_active"]]

for message in messages_actuels:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt_a_traiter = None

if messages_actuels:
    dernier_index_user = -1
    for idx, m in enumerate(reversed(messages_actuels)):
        if m["role"] == "user":
            dernier_index_user = len(messages_actuels) - 1 - idx
            break
            
    if dernier_index_user != -1:
        with st.expander("Modifier votre derniere directive"):
            nouveau_texte = st.text_input("Ajustez votre consigne :", value=messages_actuels[dernier_index_user]["content"], key=f"edit_txt_{st.session_state['session_active']}")
            if st.button("Mettre a jour et relancer", key=f"btn_edit_run_{st.session_state['session_active']}"):
                st.session_state["sessions"][st.session_state["session_active"]] =
