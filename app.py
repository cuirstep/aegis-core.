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
client_gemini = genai.Client(api_key=gemini_key) if gemini_key else None

# Récupération dynamique de toutes les clés Groq disponibles dans les secrets
groq_keys = []
for i in range(1, 6):  # Permet de gérer jusqu'à 5 clés différentes (GROQ_API_KEY_1, _2, etc.)
    key = st.secrets.get(f"GROQ_API_KEY_{i}", "")
    if not key and i == 1:
        # Rétrocompatibilité avec l'ancienne variable unique
        key = st.secrets.get("GROQ_API_KEY", "")
    if key:
        groq_keys.append(key)

# --- SIDEBAR ---
with st.sidebar:
    st.title("PARAMÈTRES DU SYSTÈME")
    st.markdown("---")
    
    st.markdown("### État du Meta-Router")
    if client_gemini:
        st.success("Moteur Principal : Gemini 2.5 Flash")
    else:
        st.warning("Gemini non configuré")

    if groq_keys:
        st.success(f"Moteur de Secours : Groq ({len(groq_keys)} clé(s) en rotation)")
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

# --- CHAT INPUT & AUTOMATIC ROTATION FALLBACK ---
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
                st.caption("⚠️ *Alerte Meta-Router : Bascule automatique sur les canaux de secours Groq...*")

        # --- TENTATIVE 2 : ROTATION DES CLÉS GROQ ---
        if groq_keys and not succes:
            messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in st.session_state.messages:
                messages_payload.append({"role": m["role"], "content": m["content"]})

            # On essaie chaque clé Groq l'une après l'autre en cas d'échec
            for idx, g_key in enumerate(groq_keys):
                try:
                    temp_client_groq = Groq(api_key=g_key)
                    stream = temp_client_groq.chat.completions.create(
                        model="llama-3.1-8b-instant",  # Modèle actif standard
                        messages=messages_payload,
                        stream=True,
                    )

                    reponse_finale = st.write_stream(chunk.choices[0].delta.content or "" for chunk in stream)
                    succes = True
                    break  # Si ça marche, on sort de la boucle de rotation
                except Exception as e:
                    # Si la clé échoue, on continue vers la clé suivante de la liste
                    continue

        if not succes and not reponse_finale:
            reponse_finale = "❌ Erreur critique : Tous les moteurs et clés de secours sont saturés ou invalides."
            st.markdown(reponse_finale)

        st.session_state.messages.append({"role": "assistant", "content": reponse_finale})
