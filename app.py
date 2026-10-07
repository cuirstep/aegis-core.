import streamlit as st
import json
import os

# Configuration de la page et du style tactique
st.set_page_config(page_title="AEGIS-CORE OS", page_icon="🛡️", layout="wide")

st.title("🛡️ AEGIS-CORE // INTERFACE OPÉRATIONNELLE")
st.sidebar.title("Paramètres du Système")

# 1. Chargement de la base de connaissances (les profils, la mémoire)
def charger_base_connaissances():
    if os.path.exists("base_de_connaissances.json"):
        with open("base_de_connaissances.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

kb_data = charger_base_connaissances()

# 2. Initialisation de l'historique de conversation dynamique (La mémoire de session)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": "Tu es AEGIS-CORE, un OS IA militaire et stratégique d'élite. Tu aides le Commandant avec rigueur, précision, en structurant les projets étape par étape et en adoptant un ton professionnel, engagé et tactique."
        }
    ]

# Affichage de l'historique des messages dans l'interface
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 3. Zone de saisie pour discuter avec l'IA comme un grand modèle
if prompt := st.chat_input("Entrez votre directive ou idée de projet, Commandant..."):
    # Ajout du message de l'utilisateur à l'historique
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Simulation / Appel de la réponse de l'IA (Ici tu brancheras ton API GPT/Claude ou ton modèle local)
    with st.chat_message("assistant"):
        # Exemple de réponse structurée inspirée de ton prompt système
        reponse_aegis = f"Reçu, Commandant. Analyse de la directive : '{prompt}'. En tant qu'AEGIS-CORE, je structure le projet par étapes tactiques..."
        st.markdown(reponse_aegis)
        
        # Ajout de la réponse à l'historique dynamique
        st.session_state.messages.append({"role": "assistant", "content": reponse_aegis})
