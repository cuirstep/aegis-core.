import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="AEGIS-CORE | Interface",
    page_icon="⚡",
    layout="centered"
)

# Style CSS personnalisé : Noir profond et Or épuré
st.markdown("""
    <style>
    /* Fond global de l'application en noir profond */
    .stApp {
        background-color: #0B0B0C;
        color: #E0E0E0;
    }
    
    /* En-tête du système */
    .header-title {
        font-family: 'Helvetica Neue', sans-serif;
        color: #D4AF37;
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: 2px;
        margin-bottom: 0px;
    }
    .header-subtitle {
        text-align: center;
        color: #888888;
        font-size: 0.9rem;
        margin-bottom: 30px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Style des bulles de chat utilisateur */
    .stChatMessage[data-testid="stChatMessage-user"] {
        background-color: #161618;
        border: 1px solid #333333;
        border-radius: 8px;
    }

    /* Style des bulles de chat de l'IA (accents dorés) */
    .stChatMessage[data-testid="stChatMessage-assistant"] {
        background-color: #121214;
        border: 1px solid #D4AF37;
        border-radius: 8px;
    }

    /* Zone de saisie de texte */
    .stChatInput input {
        background-color: #161618 !important;
        color: #FFFFFF !important;
        border: 1px solid #D4AF37 !important;
        border-radius: 6px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Titre visuel de l'interface
st.markdown('<p class="header-title">AEGIS-CORE</p>', unsafe_allow_html=True)
st.markdown('<p class="header-subtitle">Système d\'Intelligence Artificielle Distribué — v2.0</p>', unsafe_allow_html=True)

# Initialisation de l'historique des messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Salutations, Commandant. Systèmes opérationnels. En attente de votre directive."}
    ]

# Affichage des messages du chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Réaction à la saisie de l'utilisateur
if prompt := st.chat_input("Entrez votre directive pour AEGIS..."):
    # Ajout du message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Réponse simulée de l'IA (en attendant de brancher router.py)
    response = f"Analyse de la directive : '{prompt}'. Meta-Router et Quintuple Contrôle validés. Traitement en cours par AEGIS-CORE."
    
    with st.chat_message("assistant"):
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
