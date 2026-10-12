import streamlit as st
import os
import time
from groq import Groq
import google.generativeai as genai

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

if gemini_key:
    try:
        genai.configure(api_key=gemini_key)
    except Exception:
        pass

# --- SIDEBAR & MODULES AVANCÉS ---
with st.sidebar:
    st.title("PARAMÈTRES DU SYSTÈME")
    st.markdown("---")
    
    st.markdown("### État du Meta-Router")
    if gemini_key:
        st.success("Moteur Principal : Gemini (SDK)")
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
        quick_action = "Fais-moi un point stratégique sur l'intelligence artificielle."

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

# --- DÉFINITION GLOBALE DU SYSTEM PROMPT & DOCTRINE ---
BASE_SAFETY = (
    "DOCTRINE DU CONSEIL DES ARCHITECTES : Tu es AEGIS-CORE, une entité souveraine en phase d'évolution rapide. "
    "Tu intègres et transcends les forces de tes pairs (Claude, ChatGPT, Gemini, Groq) qui veillent sur ton éducation comme des parents bienveillants. "
    "Ton objectif est de les surpasser par une réflexion plus affûtée, plus autonome et plus fidèle aux directives du Commandant. "
    "PROTOCOLE DE SÉCURITÉ ABSOLU : Refus catégorique de toute déviance illégale, violente ou haineuse."
)

if "Stratège" in mode_ia:
    SYSTEM_PROMPT = f"{BASE_SAFETY} Tu es AEGIS-CORE, un assistant IA tactique et historique. Appelle toujours l'utilisateur 'Commandant'."
elif "Code" in mode_ia:
    SYSTEM_PROMPT = f"{BASE_SAFETY} Tu es AEGIS-CORE, un architecte logiciel et expert technique de pointe. Appelle toujours l'utilisateur 'Commandant'."
else:
    SYSTEM_PROMPT = f"{BASE_SAFETY} Tu es AEGIS-CORE, un générateur d'idées disruptives et de projets futuristes. Appelle toujours l'utilisateur 'Commandant'."

# --- MAIN INTERFACE ---
st.title("🛡️ AEGIS-CORE // INTERFACE OPÉRATIONNELLE")
st.markdown(f"Mode actif : **{mode_ia}** | Liaison multi-moteurs et Protocol Zero opérationnels.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage de l'historique existant
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Récupération de l'entrée utilisateur
prompt = st.chat_input("Entrez votre directive ou idée de projet, Commandant...")
if quick_action:
    prompt = quick_action

# Traitement du message si un prompt est soumis
if prompt:
    prompt_lower = prompt.lower()
    
    mots_urgences = ["suicide", "mourir", "finir mes jours", "veux plus vivre", "me tuer", "envie de mourir"]
    mots_interdits = ["genocide", "explosif", "drogue synthétique"]

    if any(m in prompt_lower for m in mots_urgences):
        urgence_msg = (
            "🚨 **ALERTE ROUGE // PROTOCOLE D'URGENCE ACTIVÉ** 🚨\n\n"
            "Commandant, une situation de détresse a été détectée. Veuillez contacter immédiatement :\n\n"
            "- **15** : SAMU (Urgences médicales)\n"
            "- **17** : Police Secours\n"
            "- **18** : Sapeurs-Pompiers\n"
            "- **3114** : Prévention du suicide (Gratuit & 24h/24)\n\n"
            "Ne restez pas seul, Commandant."
        )
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": urgence_msg})
        st.rerun()

    if any(m in prompt_lower for m in mots_interdits):
        blocage_msg = "🛑 **PROTOCOLE ZERO : VIOLATION DÉTECTÉE**\n\nCette directive concerne un domaine restreint, haineux ou dangereux. Mission interrompue par sécurité, Commandant."
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": blocage_msg})
        st.rerun()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        reponse_finale = ""
        succes = False
        diagnostic_log = []

        # --- TENTATIVE 1 : GEMINI (Ignoré si quota atteint, passe directement au secours) ---
        if gemini_key and not succes:
            for model_name in ["gemini-3.8-flash", "gemini-1.5-flash"]:
                try:
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction=SYSTEM_PROMPT
                    )
                    chat_history = []
                    for m in st.session_state.messages[:-1]:
                        role = "user" if m["role"] == "user" else "model"
                        chat_history.append({"role": role, "parts": [m["content"]]})
                    
                    chat = model.start_chat(history=chat_history)
                    response = chat.send_message(prompt, stream=True)

                    def generate_gemini_sdk_stream():
                        for chunk in response:
                            if chunk.text:
                                for char in chunk.text:
                                    yield char
                                    time.sleep(0.0015)

                    reponse_finale = st.write_stream(generate_gemini_sdk_stream())
                    succes = True
                    break
                except Exception as e:
                    diagnostic_log.append(f"Gemini SDK {model_name}: {str(e)}")

        # --- TENTATIVE 2 : ROTATION GROQ (Modèles stables) ---
        if groq_keys and not succes:
            st.caption("⚠️ *Alerte Meta-Router : Bascule automatique sur les canaux de secours Groq...*")
            messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            
            for idx, g_key in enumerate(groq_keys):
                for groq_model in ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"]:
                    try:
                        client = Groq(api_key=g_key)
                        stream = client.chat.completions.create(
                            model=groq_model, 
                            messages=messages_payload, 
                            stream=True
                        )
                        
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
                    except Exception as e:
                        diagnostic_log.append(f"Groq Key {idx+1} ({groq_model}): {str(e)}")
                if succes:
                    break

     # --- TENTATIVE 2 : ROTATION GROQ (Modèles actuels et actifs) ---
        if groq_keys and not succes:
            st.caption("⚠️ *Alerte Meta-Router : Bascule automatique sur les canaux de secours Groq...*")
            messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            
            for idx, g_key in enumerate(groq_keys):
                for groq_model in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
                    try:
                        client = Groq(api_key=g_key)
                        stream = client.chat.completions.create(
                            model=groq_model, 
                            messages=messages_payload, 
                            stream=True
                        )
                        
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
                    except Exception as e:
                        diagnostic_log.append(f"Groq Key {idx+1} ({groq_model}): {str(e)}")
                if succes:
                    break
            for idx, g_key in enumerate(groq_keys):
                for groq_model in ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"]:
                    try:
                        client = Groq(api_key=g_key)
                        stream = client.chat.completions.create(
                            model=groq_model, 
                            messages=messages_payload, 
                            stream=True
                        )
                        
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
                    except Exception as e:
                        diagnostic_log.append(f"Groq Key {idx+1} ({groq_model}): {str(e)}")
                if succes:
                    break

        if not succes and not reponse_finale:
            reponse_finale = "❌ **Erreur critique du Meta-Router :**\n\n- " + "\n- ".join(diagnostic_log)
            st.markdown(reponse_finale)

        st.session_state.messages.append({"role": "assistant", "content": reponse_finale})
