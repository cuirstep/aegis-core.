import streamlit as st
import os
import google.generativeai as genai

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="AEGIS-CORE // OS",
    page_icon="🛡️",
    layout="wide"
)

# --- CONFIGURATION DE LA CLÉ ---
# Récupération depuis les secrets Streamlit
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

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("PARAMÈTRES DU SYSTÈME")
    st.markdown("---")
    
    if cle_active:
        st.success("Liaison neuronale établie (Sécurisée).")
    else:
        st.error("⚠️ Clé API manquante dans les Secrets Streamlit.")
        
    st.markdown("---")
    st.markdown("### État du Système")
    st.info("Statut : Opérationnel\n\nMode : Polyvalent & Quotidien")

# --- INTERFACE PRINCIPALE ---
st.title("🛡️ AEGIS-CORE // INTERFACE OPÉRATIONNELLE")
st.markdown("Système d'assistance globale, stratégique et du quotidien.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- GESTION DES ENTRÉES ---
if prompt := st.chat_input("Entrez votre directive ou idée de projet, Commandant..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        reponse_finale = ""
        if not cle_active:
            reponse_finale = "⚠️ **Erreur** : Configure ta clé dans les Secrets de Streamlit."
        else:
            try:
                # Utilisation du modèle flash stable
                model = genai.GenerativeModel('gemini-1.5-flash')
                contexte = (
                    "Tu es AEGIS-CORE, un assistant IA tactique, ultra-polyvalent, intelligent et réactif, "
                    "capable de répondre à une vaste variété de questions du quotidien. "
                    "Tu t'adresses toujours à l'utilisateur en l'appelant 'Commandant'."
                )
                response = model.generate_content(f"{contexte}\n\nRequête du Commandant : {prompt}")
                reponse_finale = response.text
            except Exception as e:
                reponse_finale = f"❌ Erreur technique : {str(e)}"

        st.markdown(reponse_finale)
        st.session_state.messages.append({"role": "assistant", "content": reponse_finale})
