import streamlit as st
import os
import requests
from groq import Groq

st.set_page_config(page_title="AEGIS-CORE // DEBUG", page_icon="🛡️", layout="wide")

gemini_key = st.secrets.get("GEMINI_API_KEY", "")
groq_keys = []
for i in range(1, 6):
    key = st.secrets.get(f"GROQ_API_KEY_{i}", "")
    if not key and i == 1:
        key = st.secrets.get("GROQ_API_KEY", "")
    if key:
        groq_keys.append(key)

st.title("🛡️ AEGIS-CORE // MODE DIAGNOSTIC")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

SYSTEM_PROMPT = "Tu es AEGIS-CORE, un assistant IA tactique. Appelle l'utilisateur 'Commandant'."

if prompt := st.chat_input("Testez une commande..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        reponse_finale = ""
        succes = False
        debug_logs = []

        # Test Gemini
        if gemini_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
                payload = {
                    "contents": [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in st.session_state.messages],
                    "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]}
                }
                res = requests.post(url, json=payload, timeout=20)
                if res.status_code == 200:
                    reponse_finale = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                    succes = True
                else:
                    debug_logs.append(f"Gemini HTTP {res.status_code}: {res.text}")
            except Exception as e:
                debug_logs.append(f"Gemini Exception: {str(e)}")

        # Test Groq si Gemini a échoué
        if groq_keys and not succes:
            messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            for idx, g_key in enumerate(groq_keys):
                try:
                    client = Groq(api_key=g_key)
                    stream = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages_payload, stream=True)
                    reponse_finale = st.write_stream(chunk.choices[0].delta.content or "" for chunk in stream)
                    succes = True
                    break
                except Exception as e:
                    debug_logs.append(f"Groq Key {idx+1} Error: {str(e)}")

        if not succes:
            reponse_finale = "❌ **Échec du diagnostic détaillé :**\n\n" + "\n".join([f"- {log}" for log in debug_logs])
            st.markdown(reponse_finale)

        st.session_state.messages.append({"role": "assistant", "content": reponse_finale})
