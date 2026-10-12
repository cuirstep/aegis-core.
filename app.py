import streamlit as st
import os
import requests
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

        # --- TENTATIVE 1 : GEMINI ---
        if gemini_key and not succes:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={gemini_key}"
                payload = {
                    "contents": [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in st.session_state.messages],
                    "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]}
                }
                res = requests.post(url, json=payload, timeout=30)
                if res.status_code == 200:
                    reponse_finale = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                    st.markdown(reponse_finale)
                    succes = True
            except Exception:
                pass

        # --- TENTATIVE 2 : ROTATION GROQ ---
        if groq_keys and not succes:
            st.caption("⚠️ *Alerte Meta-Router : Bascule automatique sur les canaux de secours Groq...*")
            messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            for g_key in groq_keys:
                try:
                    client = Groq(api_key=g_key)
                    stream = client.chat.completions.create(model="llama3-8b-8192", messages=messages_payload, stream=True)
                    reponse_finale = st.write_stream(chunk.choices[0].delta.content or "" for chunk in stream)
                    succes = True
                    break
                except Exception:
                    continue

        if not succes and not reponse_finale:
            reponse_finale = "❌ Erreur critique : Tous les moteurs et clés de secours sont indisponibles."
            st.markdown(reponse_finale)

        st.session_state.messages.append({"role": "assistant", "content": reponse_finale})
