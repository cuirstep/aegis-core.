import streamlit as st
import os
import requests
import time
from groq import Groq

st.set_page_config(page_title="AEGIS-CORE // OS", page_icon="🛡️", layout="wide")

gemini_key = st.secrets.get("GEMINI_API_KEY", "")
groq_keys = []
for i in range(1, 6):
    key = st.secrets.get(f"GROQ_API_KEY_{i}", "")
    if not key and i == 1:
        key = st.secrets.get("GROQ_API_KEY", "")
    if key:
        groq_keys.append(key)

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

st.title("🛡️ AEGIS-CORE // INTERFACE OPÉRATIONNELLE")
st.markdown("Système d'assistance globale avec rotation de clés et secours automatique.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

SYSTEM_PROMPT = "Tu es AEGIS-CORE, un assistant IA tactique, ultra-polyvalent et réactif. Appelle toujours l'utilisateur 'Commandant'."

if prompt := st.chat_input("Entrez votre directive ou idée de projet, Commandant..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        reponse_finale = ""
        succes = False

        # --- TENTATIVE 1 : GEMINI (avec effet stream et vitesse augmentée) ---
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
                                                    # Vitesse augmentée (délai très court par caractère)
                                                    time.sleep(0.002)
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
                                    time.sleep(0.002)

                    reponse_finale = st.write_stream(generate_groq_stream())
                    succes = True
                    break
                except Exception:
                    continue

        if not succes and not reponse_finale:
            reponse_finale = "❌ Erreur critique : Tous les moteurs et clés de secours sont indisponibles."
            st.markdown(reponse_finale)

        st.session_state.messages.append({"role": "assistant", "content": reponse_finale})
