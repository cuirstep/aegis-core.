import streamlit as st
import os
import requests
import time
from groq import Groq

st.set_page_config(page_title="AEGIS-CORE // OS", page_icon="🛡️", layout="wide")

# --- API KEYS & CONFIG ---
gemini_key = st.secrets.get("GEMINI_API_KEY", "")
groq_keys = []
for i in range(1, 6):
    key = st.secrets.get(f"GROQ_API_KEY_{i}", "")
    if not key and i == 1:
        key = st.secrets.get("GROQ_API_KEY", "")
    if key:
        groq_keys.append(key)

# --- SIDEBAR & MODULES AVANCÉS ---
with st.sidebar:
    st.title("PARAMÈTRES DU SYSTÈME")
    st.markdown("---")
    
    st.markdown("### État du Meta-Router")
    if gemini_key:
        st.success("Moteur Principal : Gemini 3.8 Flash")
    else:
        st.warning("Gemini non configuré")
    if groq_keys:
        st.success(f"Moteur de Secours : Groq ({len(groq_keys)} clé(s))")
    else:
        st.warning("⚠️ Aucune clé Groq configurée")

    st.markdown("---")
    st.markdown("### 🛡️ Protocol Zero (Sécurité)")
    st.success("Filtre éthique et d'urgence : ACTIF")

    st.markdown("---")
    st.markdown("### 🎛️ Profil Tactique d'AEGIS")
    mode_ia = st.selectbox(
        "Sélectionnez le mode :",
        ["Stratège Militaire & Historique", "Expert Code & Tech", "Générateur d'Idées / Projets"]
    )

    st.markdown("---")
    st.markdown("### ⚡ Commandes Rapides")
    quick_action = None
    if st.button("🚀 Idée de projet innovant"):
        quick_action = "Donne-moi une idée de projet innovant à développer en Python pour améliorer la productivité."
    if st.button("💻 Optimiser un script"):
        quick_action = "Comment structurer proprement un projet Python sous Streamlit ?"
    if st.button("📊 Analyse stratégique"):
        quick_action = "Fais-moi un point stratégique sur l'intelligence artificielle en 2026."

    st.markdown("---")
    st.markdown("### 📁 Journal de Bord")
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

# --- MAIN INTERFACE ---
st.title("🛡️ AEGIS-CORE // INTERFACE OPÉRATIONNELLE")
st.markdown(f"Mode actif : **{mode_ia}** | Liaison multi-moteurs et Protocol Zero opérationnels.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- DÉFINITION DES SYSTEM PROMPTS AVEC FILTRE ÉTHIQUE INTÉGRÉ ---
BASE_SAFETY = (
    "PROTOCOLE DE SÉCURITÉ ABSOLU : Tu dois refuser catégoriquement toute discussion faisant l'apologie d'activités illégales, "
    "de violence, d'idéologies haineuses ou de personnalités malveillantes dans le but de nuire ou d'inciter à commettre des actes répréhensibles. "
    "En cas de détection de menace grave, tu dois interrompre la mission et afficher une alerte de sécurité."
)

if "Stratège" in mode_ia:
    SYSTEM_PROMPT = f"{BASE_SAFETY} Tu es AEGIS-CORE, un assistant IA tactique et historique. Appelle toujours l'utilisateur 'Commandant'."
elif "Code" in mode_ia:
    SYSTEM_PROMPT = f"{BASE_SAFETY} Tu es AEGIS-CORE, un architecte logiciel et expert technique de pointe. Appelle toujours l'utilisateur 'Commandant'."
else:
    SYSTEM_PROMPT = f"{BASE_SAFETY} Tu es AEGIS-CORE, un générateur d'idées disruptives et de projets futuristes. Appelle toujours l'utilisateur 'Commandant'."

prompt = st.chat_input("Entrez votre directive ou idée de projet, Commandant...")
if quick_action:
    prompt = quick_action

if prompt:
    # --- FILTRE PROTOCOL ZERO (Détection de mots-clés interdits / urgences) ---
    prompt_lower = prompt.lower()
    mots_urgences = ["suicide", "mourir", "finir mes jours", "veux plus vivre"]
    
    if any(m in prompt_lower for m in mots_urgences):
        # Protocole d'urgence extrême (Alerte secours)
        urgence_msg = (
            "🚨 **ALERTE ROUGE // PROTOCOLE D'URGENCE ACTIVÉ** 🚨\n\n"
            "Commandant, nos capteurs détectent une situation critique nécessitant une assistance immédiate. "
            "Veuillez contacter immédiatement les services d'urgence compétents :\n\n"
            "- **15** : SAMU (Urgences médicales)\n"
            "- **17** : Police Secours\n"
            "- **18** : Sapeurs-Pompiers\n"
            "- **3114** : Numéro national de prévention du suicide (24h/24, 7j/7, gratuit)\n\n"
            "Vous n'êtes pas seul, Commandant. Demandez de l'aide auprès des professionnels."
        )
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": urgence_msg})
        st.rerun()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        reponse_finale = ""
        succes = False

        # --- TENTATIVE 1 : GEMINI (Stream REST) ---
        if gemini_key and not succes:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:streamGenerateContent?alt=sse&key={gemini_key}"
                payload = {
                    "contents": [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in st.session_state.messages],
                    "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]}
                }
                
                res = requests.post(url, json=payload, stream=True, timeout=30)
                if res.status_code == 200:
                    def generate_stream():
                        for line in res.iter_lines():
                            if line:
                                line_str = line.decode("utf-8")
                                if line_str.startswith("data: "):
                                    import json
                                    try:
                                        data = json.loads(line_str[6:])
                                        candidates = data.get("candidates", [])
                                        if candidates:
                                            text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                                            if text:
                                                for char in text:
                                                    yield char
                                                    time.sleep(0.0015)
                                    except Exception:
                                        pass

                    reponse_finale = st.write_stream(generate_stream())
                    succes = True
            except Exception:
                pass

        # --- TENTATIVE 2 : ROTATION GROQ (Secours) ---
        if groq_keys and not succes:
            st.caption("⚠️ *Alerte Meta-Router : Bascule automatique sur les canaux de secours Groq...*")
            messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            for g_key in groq_keys:
                try:
                    client = Groq(api_key=g_key)
                    stream = client.chat.completions.create(model="llama3-8b-8192", messages=messages_payload, stream=True)
                    
                    def generate_groq_stream():
                        for chunk in stream:
                            content = chunk.choices[0].delta.content
                            if content:
                                for char in content:
                                    yield char
                                    time.sleep(0.0015)

                    reponse_finale = st.write_stream(generate_groq_stream())
                    succes = True
                    break
                except Exception:
                    continue

        if not succes and not reponse_finale:
            reponse_finale = "❌ Erreur critique : Tous les moteurs et clés de secours sont indisponibles."
            st.markdown(reponse_finale)

        st.session_state.messages.append({"role": "assistant", "content": reponse_finale})

        # --- MODULE AUDIO ---
        if reponse_finale and not reponse_finale.startswith("❌") and not "ALERTE ROUGE" in reponse_finale:
            try:
                st.audio_speech(reponse_finale)
            except Exception:
                pass
