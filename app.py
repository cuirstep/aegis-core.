import streamlit as st
import os
import google.generativeai as genai

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AEGIS-CORE // OS",
    page_icon="🛡️",
    layout="wide"
)

# --- API KEY CONFIG ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = ""

if api_key:
    os.environ["GEMINI_API_KEY"] = api_key
    genai.configure(api_key=api_key)
    cle_active = True
else:
    cle_active = False

# --- SIDEBAR ---
with st.sidebar:
    st.title("PARAMÈTRES DU SYSTÈME")
    st.markdown("---")
    
    if cle_active:
        st.success("Liaison neuronale établie (Sécurisée).")
    else:
        st.error("⚠️ Clé API manquante dans les Secrets Streamlit.")
        
    st.markdown("---")
    st.markdown("### État du Système")
    st.info("Statut : Opérationnel\n\nMode : Streaming Ultra-Rapide")

# --- MAIN INTERFACE ---
st.title("🛡️ AEGIS-CORE // INTERFACE OPÉRATIONNELLE")
st.markdown("Système d'assistance globale, stratégique et du quotidien.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT INPUT & STREAMING MODEL ---
if prompt := st.chat_input("Entrez votre directive ou idée de projet, Commandant..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if not cle_active:
            reponse_finale = "⚠️ **Erreur** : Configure ta clé dans les Secrets de Streamlit."
            st.markdown(reponse_finale)
        else:
            try:
                # Modèle flash ultra-rapide avec streaming activé
                model = genai.GenerativeModel('gemini-flash-latest')
                contexte = (
                    "Tu es AEGIS-CORE, un assistant IA tactique et ultra-rapide. "
                    "Réponds immédiatement et directement. "
                    "Tu t'adresses toujours à l'utilisateur en l'appelant 'Commandant'."
                )
                
                # Appel en flux (streaming) pour l'affichage en direct
                response = model.generate_content(f"{contexte}\n\nRequête du Commandant : {prompt}", stream=True)
                
                # Affichage dynamique mot par mot
                reponse_finale = st.write_stream(chunk.text for chunk in response)
                
            except Exception as e:
                reponse_finale = f"❌ Erreur technique : {str(e)}"
                st.markdown(reponse_finale)

        st.session_state.messages.append({"role": "assistant", "content": reponse_finale})
