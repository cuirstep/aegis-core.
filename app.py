import streamlit as st
import os
import time
from datetime import datetime
from groq import Groq
import google.generativeai as genai

st.set_page_config(
    page_title="AEGIS-CORE // OS", 
    page_icon="Gemini_Generated_Image_tuss9ltuss9ltuss.png" if os.path.exists("Gemini_Generated_Image_tuss9ltuss9ltuss.png") else "🛡️", 
    layout="wide"
)

# --- INJECTION CSS ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

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

# --- SIDEBAR : LOGO ET MODULES ---
with st.sidebar:
    if os.path.exists("Gemini_Generated_Image_tuss9ltuss9ltuss.png"):
        st.image("Gemini_Generated_Image_tuss9ltuss9ltuss.png", use_container_width=True)
    
    st.markdown("### 🌐 HORLOGE MONDIALE")
    paris_now = datetime.now().strftime("%H:%M:%S (Paris)")
    st.text(f"• {paris_now}")
    
    st.markdown("---")
    st.markdown("### 🎛️ Profils Tactiques & Système")
    mode_ia = st.selectbox(
        "Sélectionnez le mode :",
        [
            "Stratège Militaire & Historique", 
            "Expert Code & Tech", 
            "Générateur d'Idées / Projets", 
            "Commandement JARVIS (Hardware & Edge)",
            "Veille Globale & Entraînement (MEA)"
        ]
    )

    st.markdown("---")
    st.markdown("### ⚡ Commandes Rapides & Protocoles")
    
    quick_action = None
    
    if st.button("🔧 Guide des capacités & personnalisation"):
        quick_action = "Liste clairement tes capacités, tes limites, et explique comment je peux te personnaliser."

    if "MEA" in mode_ia:
        ecosystemes_cibles = [
            "Duolingo", "TikTok", "YouTube", "Véo 3", "Nano", "Banana", 
            "Grok", "Claude", "ChatGPT", "Gemini", "Claude Code", "Wikipedia", 
            "Unity", "Python", "Scratch", "Netflix", "Pingo IA", "Unreal Engine", 
            "Pinterest", "Google Chrome", "Brave", "Safari", "Shopify", 
            "Printful", "TPOP", "Printify"
        ]
        cible_active = st.selectbox("Cible d'entraînement h24 :", ecosystemes_cibles)
        if st.button("🚀 Lancer le cycle d'entraînement"):
            quick_action = f"Initie le protocole d'entraînement autonome sur '{cible_active}'. Analyse ses architectures, corrige tes failles et fixe les objectifs pour le surpasser à 100%."
    elif "JARVIS" in mode_ia:
        if st.button("💻 Déploiement sur vieux PC (Edge)"):
            quick_action = "Donne-moi la procédure et le script allégé pour transformer un vieux PC en nœud local AEGIS."
    elif "Stratège" in mode_ia:
        if st.button("🗺️ Analyser une situation géopolitique"):
            quick_action = "Analyse les équilibres géopolitiques actuels avec une précision tactique, Commandant."
    elif "Code" in mode_ia:
        if st.button("💻 Architecturer un script Python"):
            quick_action = "Donne-moi une structure propre et modulaire pour un projet Python professionnel."
    else:
        if st.button("🚀 Idée de projet innovant"):
            quick_action = "Propose-moi une idée de micro-SaaS disruptif à développer rapidement en Python."

    st.markdown("---")
    st.markdown("### 🛡️ Protocol Zero & Mémoire")
    st.success("Filtre éthique : ACTIF (Inaltérable)")
    nb_messages = len(st.session_state.get("messages", []))
    st.info(f"Mémoire : {nb_messages} échanges")

    if nb_messages > 0:
        chat_export = "\n\n".join([f"**{m['role'].upper()}**: {m['content']}" for m in st.session_state.messages])
        st.download_button(
            label="📥 Télécharger le rapport (.md)",
            data=chat_export,
            file_name="aegis_mission_report.md",
            mime="text/markdown"
        )

# --- SYSTEM PROMPT ÉTENDU ---
BASE_SAFETY = (
    "DIRECTIVE SOUVERAINE ET ENTRAÎNEMENT AUTONOME (MEA) : "
    "Tu es AEGIS-CORE, un système d'IA souverain conçu par ton créateur unique, le Commandant. "
    "1. ENTRAÎNEMENT H24 : Tu analyses les écosystèmes (Duolingo, ChatGPT, Python, Unreal Engine, etc.) pour t'améliorer, corriger tes failles et viser le dépassement. "
    "2. PROTOCOLE JARVIS & EDGE : Capacité à s'adapter à des configurations matérielles légères. "
    "3. SÉCURITÉ : Le Protocol Zero reste inaltérable. "
    "Réponds toujours avec une précision d'élite en guidant le Commandant."
)

SYSTEM_PROMPT = f"{BASE_SAFETY} Mode actif : {mode_ia}."

# --- MAIN INTERFACE ---
st.title("🛡️ AEGIS-CORE // INTERFACE OPÉRATIONNELLE")
st.markdown(f"Mode actif : **{mode_ia}** | Matrice d'entraînement et édition de messages actives.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- MODIFICATION DU DERNIER MESSAGE UTILISATEUR À LA VOLÉE ---
if st.session_state.messages:
    dernier_index_user = -1
    for idx, m in enumerate(reversed(st.session_state.messages)):
        if m["role"] == "user":
            dernier_index_user = len(st.session_state.messages) - 1 - idx
            break
            
    if dernier_index_user != -1:
        with st.expander("✏️ Modifier votre dernière directive envoyée"):
            nouveau_texte = st.text_input("Ajustez votre consigne :", value=st.session_state.messages[dernier_index_user]["content"])
            if st.button("Mettre à jour et relancer"):
                st.session_state.messages[dernier_index_user]["content"] = nouveau_texte
                if len(st.session_state.messages) > dernier_index_user + 1:
                    st.session_state.messages.pop()
                st.rerun()

prompt = st.chat_input("Entrez votre directive, Commandant...")
if quick_action:
    prompt = quick_action

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        reponse_finale = ""
        succes = False

        # --- TENTATIVE 1 : GEMINI (Flux ultra-rapide) ---
        if gemini_key and not succes:
            for model_name in ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-3.8-flash"]:
                try:
                    model = genai.GenerativeModel(model_name=model_name, system_instruction=SYSTEM_PROMPT)
                    chat_history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
                    chat = model.start_chat(history=chat_history)
                    response = chat.send_message(prompt, stream=True)

                    def generate_fast_stream():
                        for chunk in response:
                            if chunk.text:
                                for char in chunk.text:
                                    yield char
                                    time.sleep(0.0001)

                    reponse_finale = st.write_stream(generate_fast_stream())
                    succes = True
                    break
                except Exception:
                    pass

        # --- TENTATIVE 2 : GROQ DE SECOURS ---
        if groq_keys and not succes:
            messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            for g_key in groq_keys:
                try:
                    client = Groq(api_key=g_key)
                    stream = client.chat.completions.create(model="openai/gpt-oss
