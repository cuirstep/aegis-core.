import os
import json
import base64
import time
import requests
import io
import streamlit as st

# --- ROUTEUR LLM & SYNTHÈSE VOCALE ---
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

# --- INJECTION CSS (SUPPRESSION TOTALE DES ICÔNES & DESIGN ÉPURÉ) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* SUPPRESSION RADICALE DE TOUTES LES ICÔNES DE CHAT */
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

# --- MATRICE PROMPTS ---
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

# --- GESTION DU CHAT & PERSISTANCE ---
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
                st.session_state["sessions"][st.session_state["session_active"]] = messages_actuels[:dernier_index_user]
                prompt_a_traiter = nouveau_texte
                if st.session_state.current_user:
                    save_user_session(st.session_state.current_user, st.session_state["session_active"], st.session_state["sessions"][st.session_state["session_active"]])
                st.rerun()

prompt_input = st.chat_input("Entrez votre directive, Commandant...")
if quick_action:
    prompt_input = quick_action
if prompt_a_traiter:
    prompt_input = prompt_a_traiter

if prompt_input:
    messages_actuels.append({"role": "user", "content": prompt_input})
    with st.chat_message("user"):
        st.markdown(prompt_input)

    with st.chat_message("assistant"):
        contexte_limite = messages_actuels[-10:]
        
        def generate_stream():
            for chunk_text in route_and_generate(
                prompt=prompt_input,
                system_prompt=SYSTEM_PROMPT,
                provider="auto",
                history=contexte_limite
            ):
                yield chunk_text

        reponse_finale = st.write_stream(generate_stream())

        messages_actuels.append({"role": "assistant", "content": reponse_finale})
with st.chat_message("assistant"):
        contexte_limite = messages_actuels[-10:]
        
        def generate_stream():
            for chunk_text in route_and_generate(
                prompt=prompt_input,
                system_prompt=SYSTEM_PROMPT,
                provider="auto",
                history=contexte_limite
            ):
                yield chunk_text

        # --- EFFET VISUEL : CERCLE ANIMÉ STYLE DISCORD (Vert et Bleu) ---
        st.markdown("""
            <style>
            .discord-speaking-ring {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                border: 3px solid #00ff66;
                box-shadow: 0 0 10px #00bfff, inset 0 0 6px #00ff66;
                animation: discordPulse 1.2s infinite ease-in-out;
                display: inline-block;
                margin-bottom: 8px;
            }
            @keyframes discordPulse {
                0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(0, 255, 102, 0.7), 0 0 0 0 rgba(0, 191, 255, 0.7); }
                70% { transform: scale(1.15); box-shadow: 0 0 0 8px rgba(0, 255, 102, 0), 0 0 0 16px rgba(0, 191, 255, 0); }
                100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(0, 255, 102, 0), 0 0 0 0 rgba(0, 191, 255, 0); }
            }
            </style>
            <div style="display: flex; align-items: center; gap: 8px;">
                <div class="discord-speaking-ring"></div>
                <span style="font-size: 0.8em; color: #00ff66; font-family: monospace;">CANAL AUDIO ACTIF...</span>
            </div>
        """, unsafe_allow_html=True)

        reponse_finale = st.write_stream(generate_stream())
        messages_actuels.append({"role": "assistant", "content": reponse_finale})

        # --- SYNTHÈSE VOCALE ELEVENLABS MULTILINGUE ---
        langue_courante = "fr"
        if any(m in reponse_finale.lower() for m in ["the", "is", "and", "you"]):
            langue_courante = "en"
        elif any(m in reponse_finale.lower() for m in ["el", "la", "que", "por"]):
            langue_courante = "es"
        elif any(m in reponse_finale.lower() for m in ["fi", "min", "ala"]):
            langue_courante = "ar"
        elif any(m in reponse_finale.lower() for m in ["não", "como", "para"]):
            langue_courante = "pt"

        audio_content = text_to_speech_elevenlabs(reponse_finale, langue=langue_courante)
        if audio_content:
            st.audio(io.BytesIO(audio_content), format='audio/mpeg', autoplay=True)

        if st.session_state.current_user:
            save_user_session(st.session_state.current_user, st.session_state["session_active"], messages_actuels)
