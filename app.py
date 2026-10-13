import streamlit as st
import os
import time
from groq import Groq
import google.generativeai as genai

st.set_page_config(
    page_title="AEGIS-CORE // OS", 
    page_icon="Gemini_Generated_Image_tuss9ltuss9ltuss.png" if os.path.exists("Gemini_Generated_Image_tuss9ltuss9ltuss.png") else "🛡️", 
    layout="wide"
)

# --- INJECTION CSS : DESIGN PROPRE SANS BLOQUER LA BARRE ---
st.markdown("""
    <style>
    /* Masquer uniquement le menu hamburger et le footer Streamlit */
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
    
    st.markdown("### PARAMÈTRES DU SYSTÈME")
    st.markdown("---")
    
    st.markdown("### 🎛️ Profil Tactique d'AEGIS")
    mode_ia = st.selectbox(
        "Sélectionnez le mode :",
        ["Stratège Militaire & Historique", "Expert Code & Tech", "Générateur d'Idées / Projets"]
    )

    st.markdown("---")
    st.markdown("### ⚡ Commandes Rapides & Guide")
    
    quick_action = None
    
    # Bouton de Guidage et de Personnalisation
    if st.button("🔧 Guide des capacités & personnalisation"):
        quick_action = "Liste clairement tes capacités, tes limites techniques et explique-moi comment je peux te personnaliser ou modifier ton comportement à ma guise sans toucher à la sécurité."

    if "Stratège" in mode_ia:
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

# --- SYSTEM PROMPT ---
BASE_SAFETY = (
    "DIRECTIVE D'EXACTITUDE, CAPACITÉS ET LIMITES D'AEGIS-CORE : "
    "Tu es AEGIS-CORE, un système d'IA développé sous Streamlit et Python par ton créateur, le Commandant. "
    "TRANSPARENCE TOTALE SUR TES LIMITES : Quand l'utilisateur te demande tes capacités ou tes limites, liste-les clairement. "
    "Ce que tu peux faire (et que l'utilisateur peut modifier/adapter) : Changer de profil tactique, adapter ton ton, structurer du code, générer des idées, ajuster les prompts et exporter l'historique. "
    "Ce qui est strictement impossible (Limites incompressibles) : Contourner le Protocol Zero (les filtres de sécurité éthique et d'urgence restent inaltérables et non négociables), modifier le code source brut directement depuis le chat, ou s'affranchir des quotas des API distantes (Gemini/Groq). "
    "RÈGLE D'OR : Guide toujours l'utilisateur avec pragmatisme pour qu'il puisse personnaliser son expérience dans les limites saines du système."
)

SYSTEM_PROMPT = f"{BASE_SAFETY} Mode actif : {mode_ia}. Appelle toujours l'utilisateur 'Commandant'."

# --- MAIN INTERFACE ---
st.title("🛡️ AEGIS-CORE // INTERFACE OPÉRATIONNELLE")
st.markdown(f"Mode actif : **{mode_ia}** | Liberté de personnalisation et Protocol Zero actifs.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Entrez votre directive ou idée de projet, Commandant...")
if quick_action:
    prompt = quick_action

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        reponse_finale = ""
        succes = False

        # --- TENTATIVE 1 : GEMINI ---
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
                    stream = client.chat.completions.create(model="openai/gpt-oss-20b", messages=messages_payload, stream=True)
                    
                    def generate_groq_fast():
                        for chunk in stream:
                            content = chunk.choices[0].delta.content
                            if content:
                                for char in content:
                                    yield char
                                    time.sleep(0.0001)

                    reponse_finale = st.write_stream(generate_groq_fast())
                    succes = True
                    break
                except Exception:
                    pass

        if not succes:
            reponse_finale = "❌ Erreur critique du Meta-Router : Canaux indisponibles, Commandant."
            st.markdown(reponse_finale)

        st.session_state.messages.append({"role": "assistant", "content": reponse_finale})
