import streamlit as st
import os
import google.generativeai as genai
from bibliotheque import BibliothequeMemoire
from routeur import MetaRouter

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="AEGIS-CORE // OS",
    page_icon="🛡️",
    layout="wide"
)

# --- INITIALISATION DES MODULES ---
biblio = BibliothequeMemoire()
router = MetaRouter()

# --- BARRE LATÉRALE - PARAMÈTRES ---
with st.sidebar:
    st.title("PARAMÈTRES DU SYSTÈME")
    st.markdown("---")
    
    # Récupération de la clé API depuis la saisie utilisateur ou les secrets Streamlit
    api_key_input = st.text_input("Clé API Google Gémeaux", type="password", placeholder="AIzaSy...")
    
    api_key = api_key_input
    if not api_key:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            pass

    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key
        genai.configure(api_key=api_key)
        st.success("Liaison neuronale établie.")
    else:
        st.warning("Veuillez entrer une clé API valide.")
        
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

    analyse_resultat = router.router_reponse(prompt, biblio)
    info_archive = analyse_resultat.get("information_archive")

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        reponse_finale = ""

        current_api_key = os.environ.get("GEMINI_API_KEY")
        if not current_api_key:
            reponse_finale = "⚠️ **Erreur** : Clé API manquante."
        else:
            try:
                # Utilisation d'un modèle standard et robuste
                model = genai.GenerativeModel('gemini-1.5-flash')
                contexte = (
                    "Tu es AEGIS-CORE, un assistant IA tactique, ultra-polyvalent, intelligent et réactif, "
                    "capable de répondre à une vaste variété de questions du quotidien. "
                    "Tu t'adresses à l'utilisateur en l'appelant 'Commandant'."
                )
                if info_archive:
                    contexte += f"\n\nInfo archive : {info_archive}"
                
                response = model.generate_content(f"{contexte}\n\nRequête : {prompt}")
                reponse_finale = response.text
            except Exception as e:
                reponse_finale = f"❌ Erreur technique de l'IA : {str(e)}"

        message_placeholder.markdown(reponse_finale)
        st.session_state.messages.append({"role": "assistant", "content": reponse_finale})
