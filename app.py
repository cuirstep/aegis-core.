import os
import json
import base64
import time
import requests
import io
import streamlit as st
from llm_router import route_and_generate

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="AEGIS-CORE // BETA", 
    page_icon="🛡️", 
    layout="wide"
)

# --- IMPORT BASE DE DONNÉES ---
from database import init_db, register_user, verify_user, init_chat_db, save_user_session, load_user_sessions

init_db()
init_chat_db()

# --- FONCTION SYNTHÈSE VOCALE SÉCURISÉE ---
def text_to_speech_elevenlabs(text, langue="fr"):
    # Récupération sécurisée depuis st.secrets ou os.environ
    api_key = st.secrets.get("ELEVENLABS_API_KEY", os.getenv("ELEVENLABS_API_KEY", ""))
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

# --- INITIALISATION DE L'ÉTAT DE SESSION ---
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "sessions" not in st.session_state:
    if st.session_state.current_user:
        loaded = load_user_sessions(st.session_state.current_user)
        st.session_state["sessions"] = loaded if loaded else {"Discussion 1": []}
    else:
        st.session_state["sessions"] = {"Discussion 1": []}

if "session_active" not in st.session_state or st.session_state["session_active"] not in st.session_state["sessions"]:
    st.session_state["session_active"] = list(st.session_state["sessions"].keys())[0]

# --- INJECTION CSS & ANIMATION DE DÉMARRAGE ---
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

# --- INTERFACE PRINCIPALE DE DISCUSSION ---
st.title("🛡️ AEGIS-CORE // Interface Opérationnelle")

# Barre latérale pour la gestion des sessions
st.sidebar.title("Paramètres & Sessions")
active_session = st.session_state["session_active"]
session_names = list(st.session_state["sessions"].keys())

selected_session = st.sidebar.selectbox("Discussion active", session_names, index=session_names.index(active_session))
if selected_session != st.session_state["session_active"]:
    st.session_state["session_active"] = selected_session
    st.rerun()

# Affichage de l'historique de la discussion active
current_messages = st.session_state["sessions"][st.session_state["session_active"]]

for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Lecture audio si stockée et disponible
        if message["role"] == "assistant" and "audio" in message and message["audio"]:
            st.audio(message["audio"], format="audio/mp3")

# Zone de saisie utilisateur sécurisée avec gestion de prompt
if prompt := st.chat_input("Entrez votre directive pour AEGIS..."):
    # Ajout du message utilisateur
    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Génération de la réponse via le routeur LLM
    with st.chat_message("assistant"):
        with st.spinner("AEGIS analyse et traite la requête..."):
            try:
                reponse_ia = route_and_generate(prompt)
            except Exception as e:
                reponse_ia = f"Erreur lors du traitement par le routeur LLM : {e}"
            
            st.markdown(reponse_ia)
            
            # Génération optionnelle de la voix ElevenLabs
            audio_bytes = text_to_speech_elevenlabs(reponse_ia)
            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3")

    # Enregistrement dans l'historique de session
    current_messages.append({
        "role": "assistant", 
        "content": reponse_ia, 
        "audio": audio_bytes if audio_bytes else None
    })
    
    # Persistance SQLite si utilisateur connecté
    if st.session_state.current_user:
        save_user_session(st.session_state.current_user, st.session_state["sessions"])
