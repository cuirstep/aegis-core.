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

# --- STYLE CSS TACTIQUE ---
st.markdown("""
<style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stChatMessage { border-radius: 5px; padding: 10px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION DES MODULES ---
biblio = BibliothequeMemoire()
router = MetaRouter()

# --- BARRE LATÉRALE - PARAMÈTRES DU SYSTÈME ---
with st.sidebar:
    st.image("https://img.icons8.com/ios-filled/100/ffffff/getSourceMap.png", width=60)
    st.title("PARAMÈTRES DU SYSTÈME")
    st.markdown("---")
    
    # Configuration de la clé API Gemini de manière sécurisée
    api_key_input = st.text_input("Clé API Google Gemini", type="password", placeholder="AIzaSy...")
    
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input
        genai.configure(api_key=api_key_input)
        st.success("Liaison neuronale établie.")
    else:
        st.warning("Veuillez entrer une clé API valide pour activer les réponses en direct.")
        
    st.markdown("---")
    st.markdown("### État du Système")
    st.info("Statut : Opérationnel\n\nMode : Polyvalent & Quotidien")

# --- INTERFACE PRINCIPALE ---
st.title("🛡️ AEGIS-CORE // INTERFACE OPÉRATIONNELLE")
st.markdown("Système d'assistance globale, stratégique et du quotidien.")

# Initialisation de l'historique de conversation dans la session Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage de l'historique des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- GESTION DES ENTRÉES UTILISATEUR ---
if prompt := st.chat_input("Entrez votre directive ou idée de projet, Commandant..."):
    # Ajouter le message de l'utilisateur à l'historique
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Analyse via le routeur et recherche dans la bibliothèque
    analyse_resultat = router.router_reponse(prompt, biblio)
    info_archive = analyse_resultat.get("information_archive")

    # Génération de la réponse de l'assistant
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        reponse_finale = ""

        # Vérification de la clé API pour utiliser un vrai modèle
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            reponse_finale = "⚠️ **Erreur système** : Aucune clé API Gemini détectée dans les paramètres latéraux. Veuillez renseigner votre clé pour me permettre de traiter vos requêtes du quotidien."
        else:
            try:
                # Utilisation du modèle Gemini pour répondre à toute question du quotidien
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Construction d'un prompt système tactique enrichi par les archives si disponibles
                contexte_systeme = (
                    "Tu es AEGIS-CORE, un assistant IA tactique, ultra-polyvalent, intelligent et réactif, "
                    "capable de répondre à une vaste variété de questions du quotidien (culture, technique, rédaction, aide générale). "
                    "Tu t'adresses à l'utilisateur en l'appelant 'Commandant'."
                )
                
                if info_archive:
                    contexte_systeme += f"\n\nInformation additionnelle issue de la Grande Bibliothèque : {info_archive}"

                chat = model.start_chat(history=[])
                # Envoi du contexte global + prompt utilisateur
                reponse_complete = model.generate_content(f"{contexte_systeme}\n\nRequête du Commandant : {prompt}")
                reponse_finale = reponse_complete.text

            except Exception as e:
                reponse_finale = f"❌ Erreur lors de la liaison avec le réseau neuronal : {str(e)}"

        message_placeholder.markdown(reponse_finale)
        st.session_state.messages.append({"role": "assistant", "content": reponse_finale})
