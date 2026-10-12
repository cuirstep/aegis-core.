import streamlit as st
import os
import requests
from groq import Groq

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AEGIS-CORE // OS",
    page_icon="🛡️",
    layout="wide"
)

# --- API KEYS & CONFIG ---
gemini_key = st.secrets.get("GEMINI_API_KEY", "")

groq_keys = []
for i in range(1, 6):
    key = st.secrets.get(f"GROQ_API_KEY_{i}", "")
    if not key and i == 1:
        key = st.secrets.get("GROQ_API_KEY", "")
    if key:
        groq_keys.append(key)

# --- SIDEBAR ---
with st.sidebar:
    st.title("PARAMÈTRES DU SYSTÈME")
    st.markdown("---")
    
    st.markdown("### État du Meta-Router")
    if gemini_key:
        st.success("Moteur Principal : Gemini 2.5 Flash")
    else:
        st.warning("Gemini non configuré")

    if groq_keys:
        st.success(f"Moteur de Secours : Groq ({len(groq_keys)} clé(s))")
    else:
        st.warning("⚠️ Aucune clé Groq configurée")

    st.markdown("---")
    st.markdown("### Grande Bibliothèque")
    nb_messages = len(st.session_state.get("messages", []))
    st.info(f"Mémoire contextuelle : {nb_messages} échanges archivés")

# --- MAIN INTERFACE ---
st.title("🛡️ AEGIS-CORE // INTERFACE OPÉRATIONNELLE")
st.markdown("Système d'assistance globale avec rotation de clés et secours automatique.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Prompt Système
SYSTEM_PROMPT = (
    "Tu es AEGIS-CORE, un assistant IA tactique, ultra-polyvalent et réactif. "
    "Tu assistes le Commandant dans ses projets, calculs, réflexions et créations. "
    "Tu t'adresses toujours à l'utilisateur en l'appelant 'Commandant'."
)

# --- CHAT INPUT & FALLBACK LOGIC ---
if prompt := st.chat_input("Entrez votre directive ou idée de projet, Commandant..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        reponse_finale = ""
        succes = False

        # --- TENTATIVE 1 : GEMINI (via API REST directe) ---
        if gemini_key and not succes:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
                
                # Construction de l'historique des messages pour l'API
                formatted_contents = []
                for m in st.session_state.messages:
                    role = "user" if m["role"] == "user" else "model"
                    formatted_contents.append({
                        "role": role,
                        "parts": [{"text": m["content"]}]
                    })

                payload = {
                    "contents": formatted_contents,
                    "system_instruction": {
                        "parts": [{"text": SYSTEM_PROMPT}]
                    }
                }

                response = requests.post(url, json=payload, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    reponse_finale = data["candidates"][0]["content"]["parts"][0]["text"]
                    st.markdown(reponse_finale)
                    succes = True
                else:
                    raise Exception(f"Erreur HTTP {response.status_code}")

            except Exception as e:
                st.caption("⚠️ *Alerte Meta-Router : Bascule automatique sur les canaux de secours Groq...*")

        # --- TENTATIVE 2 : ROTATION DES CLÉS GROQ ---
        if groq_keys and not succes:
            messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in st.session_state.messages:
                messages_payload.append({"role": m["role"], "content": m["content"]})

            for g_key in groq_keys:
                try:
                    temp_client_groq = Groq(api_key=g_key)
                    stream = temp_client_groq.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=messages_payload,
                        stream=True,
                    )

                    reponse_finale = st.write_stream(chunk.choices[0].delta.content or "" for chunk in stream)
                    succes = True
                    break
                except Exception:
                    continue

        if not succes and not reponse_finale:
            reponse_finale = "❌ Erreur critique : Tous les moteurs et clés de secours sont indisponibles."
            st.markdown(reponse_finale)

        st.session_state.messages.append({"role": "assistant", "content": reponse_finale})
