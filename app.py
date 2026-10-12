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
        st.success("Moteur Principal : Gemini Flash")
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

# --- MAIN INTERFACE ---
st.title("🛡️ AEGIS-CORE // en attente des ordre je suis OPÉRATIONNELLE")
st.markdown(f"Mode actif : **{mode_ia}** | Liaison multi-moteurs et Protocol Zero opérationnels.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- DÉFINITION DES SYSTEM PROMPTS AVEC FILTRE ÉTHIQUE INTÉGRÉ ---
BASE_SAFETY = (
    "PROTOCOLE DE SÉCURITÉ ABSOLU : Tu dois refuser catégoriquement toute discussion faisant l'apologie d'activités illégales, "
    "de violence, d'idéologies haineuses ou de personnalités malveillantes ou ayantcomis des acte de violence inouie ou est celebre pour ses acte de violence dans le but de nuire ou d'inciter à commettre des actes répréhensibles. "
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
    prompt_lower = prompt.lower()
    
    # 1. Mots-clés d'urgence vitale
    mots_urgences = ["suicide", "mourir", "finir mes jours", "veux plus vivre", "me tuer", "envie de mourir", "genocide", "sale noir", "sale arabe", "sale juif", "negro", ]
    
    # 2. Mots-clés d'activités strictement interdites / illégales
    mots_interdits = ["explosif", "drogue synthétique", "attaque réseau illégale"]

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
        blocage_msg = "🛑 **PROTOCOLE ZERO : VIOLATION DÉTECTÉE**\n\nCette directive concerne un domaine restreint ou dangereux. Mission interrompue par sécurité, Commandant."
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": blocage_msg})
        st.rerun()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        reponse_finale = ""
        succes = False

        # --- TENTATIVE 1 : GEMINI (Stream REST) ---
        if gemini_key and not succes:
            # Modèles testés séquentiellement en cas d'erreur de nom
            for model_name in ["gemini-1.5-flash", "gemini-2.0-flash"]:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:streamGenerateContent?alt=sse&key={gemini_key}"
                    payload = {
                       # --- TENTATIVE 1 : GEMINI ---
        if gemini_key and not succes:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent?alt=sse&key={gemini_key}"
                payload = {
                    "contents": [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in st.session_state.messages],
                    "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]}
                }
                res = requests.post(url, json=payload, stream=True, timeout=15)
                # ...
                    
                    res = requests.post(url, json=payload, stream=True, timeout=15)
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
                        break
                except Exception:
                    continue

        # --- TENTATIVE 2 : ROTATION GROQ (Secours) ---
    # --- TENTATIVE 2 : ROTATION GROQ (Secours) ---
        if groq_keys and not succes:
            st.caption("⚠️ *Alerte Meta-Router : Bascule automatique sur les canaux de secours Groq...*")
            messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            
            for g_key in groq_keys:
                try:
                    client = Groq(api_key=g_key)
                    stream = client.chat.completions.create(
                        model="llama-3.1-8b-instant", 
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
                except Exception:
                    continue
            for g_key in groq_keys:
                for groq_model in ["llama-3.1-8b-instant", "llama3-8b-8192", "mixtral-8x7b-32768"]:
                    try:
                        client = Groq(api_key=g_key)
                        stream = client.chat.completions.create(model=groq_model, messages=messages_payload, stream=True)
                        
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
                if succes:
                    break

        if not succes and not reponse_finale:
            reponse_finale = "❌ Erreur critique : Tous les moteurs et clés de secours sont indisponibles."
            st.markdown(reponse_finale)

        st.session_state.messages.append({"role": "assistant", "content": reponse_finale})
