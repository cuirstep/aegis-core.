import streamlit as st
import os
from google import genai
from groq import Groq

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AEGIS-CORE // OS",
    page_icon="🛡️",
    layout="wide"
)

# --- API KEYS & CLIENTS INITIALIZATION ---
gemini_key = st.secrets.get("GEMINI_API_KEY", "")
groq_key = st.secrets.get("GROQ_API_KEY", "")

# Initialisation correcte du client Google GenAI
client_gemini = genai.Client(api_key=gemini_key) if gemini_key else None
client_groq = Groq(api_key=groq_key) if groq_key else None

# --- SIDEBAR ---
with st.sidebar:
    st.title("PARAMÈTRES DU SYSTÈME")
    st.markdown("---")
    
    st.markdown("### État du Meta-Router")
    if client_gemini:
        st.success("Moteur Principal : Gemini 2.5 Flash")
    else:
        st.warning("Gemini non configuré")

    if client_groq:
        st.success("Moteur de Secours (Fallback) : Groq / Llama 3")
    else:
        st.warning("Groq non configuré")

    st.markdown("---")
    st.markdown("### Grande Bibliothèque")
    nb_messages = len(st.session_state.get("messages", []))
    st.info(f"Mémoire contextuelle : {nb_messages} échanges archivés")

# --- MAIN INTERFACE ---
st.title("🛡️ AEGIS-CORE // INTERFACE OPÉRATIONNELLE")
st.markdown("Système d'assistance globale avec bascule automatique de secours.")

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

# --- CHAT INPUT & AUTOMATIC FALLBACK ---
if prompt := st.chat_input("Entrez votre directive ou idée de projet, Commandant..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        reponse_finale = ""
        succes = False

        # --- TENTATIVE 1 : GEMINI ---
        if client_gemini and not succes:
            try:
                contents = []
                for m in st.session_state.messages:
                    role_gemini = "user" if m["role"] == "user" else "model"
                    contents.append({"role": role_gemini, "parts": [{"text": m["content"]}]})

                response = client_gemini.models.generate_content_stream(
                    model="gemini-2.5-flash",
                    contents=contents,
                    config={"system_instruction": SYSTEM_PROMPT}
                )

                def stream_gemini():
                    for chunk in response:
                        if chunk.text:
                            yield chunk.text

                reponse_finale = st.write_stream(stream_gemini())
                succes = True

            except Exception as e:
                st.caption("⚠️ *Alerte Meta-Router : Bascule automatique sur le moteur de secours Groq...*")

        # --- TENTATIVE 2 : GROQ (FALLBACK) ---
        if client_groq and not succes:
            try:
                messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}]
                for m in st.session_state.messages:
                    messages_payload.append({"role": m["role"], "content": m["content"]})

                stream = client_groq.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=messages_payload,
                    stream=True,
                )

                reponse_finale = st.write_stream(chunk.choices[0].delta.content or "" for chunk in stream)
                succes = True

            except Exception as e:
                reponse_finale = f"❌ Erreur critique : Tous les moteurs sont indisponibles. ({str(e)})"
                st.markdown(reponse_finale)

        if not succes and not reponse_finale:
            reponse_finale = "⚠️ Aucune clé API valide n'a été configurée dans Streamlit Cloud."
            st.markdown(reponse_finale)

        st.session_state.messages.append({"role": "assistant", "content": reponse_finale})
