import streamlit as st
import os
import time
from datetime import datetime
from groq import Groq
import google.generativeai as genai

st.set_page_config(
    page_title="AEGIS-CORE // OS", 
    page_icon="Gemini_Generated_Image_tuss9ltuss9ltuss.png" if os.path.exists("Gemini_Generated_Image_tuss9ltuss9ltuss.png") else "🛡️", 
    layout="wide"
)

# --- INJECTION CSS & HORLOGE JS ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Masquer les avatars par défaut */
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- API KEYS & CONFIG ---
gemini_key = st.secrets.get("GEMINI_API_KEY", "")
github_token = st.secrets.get("GITHUB_TOKEN", "")
groq_keys = []
for i in range(1, 6):
    key = st.secrets.get(f"GROQ_API_KEY_{i}", "")
    if not key and i == 1:
        key = st.secrets.get("GROQ_API_KEY", "")
    if key:
        groq_keys.append(key)

if gemini_key:
    try:
        genai.configure(api_key=gemini_key)
    except Exception:
        pass

# --- MATRICE PROMPTS (SANS EMOJIS CORROMPUS) ---
MATRICE_PROMPTS = {
    "Pédagogie, Quiz & Résumés": [
        "Genere un Quiz interactif de 5 questions a choix multiples base sur notre derniere discussion.",
        "Redige une fiche de synthese pedagogique claire et structuree du projet en cours.",
        "Concois un plan de formation étape par étape pour maîtriser ce sujet de A à Z.",
        "Genere une fiche de revision rapide sous forme de carte mentale textuelle.",
        "Explique ce concept simplement.",
        "Redige un resume executif en 5 points cles.",
        "Cree une etude de cas pratique basee sur notre echange.",
        "Concois un questionnaire Vrai/Faux avec explications detaillees.",
        "Synthetise les erreurs courantes a eviter sur ce sujet.",
        "Redige un lexique des 10 termes fondamentaux a connaitre.",
        "Propose un exercice d'application directe avec son corrige.",
        "Cree un guide de demarrage rapide synthetique.",
        "Dresse une comparaison Avant/Apresh pour illustrer le concept.",
        "Redige une FAQ de 5 questions frequemment posees sur ce theme.",
        "Cree un schema textuel expliquant le flux de travail étape par étape.",
        "Redige un aide-memoire au format Markdown.",
        "Propose 3 metaphores simples pour expliquer cette notion complexe.",
        "Cree un plan de revision etale sur 7 jours.",
        "Synthetise les points d'attention cruciaux a retenir absolument.",
        "Redige une grille d'auto-evaluation des competences sur ce sujet."
    ],
    "Strategie & Geopolitique": [
        "Analyse les equilibres geopolitiques actuels avec une precision tactique.",
        "Evalue les risques strategiques d'un conflit technologique global.",
        "Dresse une cartographie des dependances en matieres premieres critiques.",
        "Simule une reponse strategique face a une cyberattaque etatique.",
        "Analyse l'impact de la souverainete numerique sur l'economie europeenne.",
        "Redige une note de synthese sur la doctrine de defense spatiale.",
        "Examine les implications de la militarisation de l'IA.",
        "Analyse l'evolution des doctrines de dissuasion moderne.",
        "Dresse un bilan des vulnerabilites des infrastructures critiques navales.",
        "Evalue les strategies de resilience de la chaine d'approvisionnement globale."
    ],
    "Developpement & Code": [
        "Donne-moi une structure propre et modulaire pour un projet Python professionnel.",
        "Optimise un algorithme Python pour reduire la complexite temporelle.",
        "Concois une architecture REST API scalable avec FastAPI.",
        "Propose un schema de base de donnees PostgreSQL pour un systeme multi-tenant.",
        "Redige un script de CI/CD complet avec GitHub Actions.",
        "Analyse et refactore ce bloc de code pour ameliorer la lisibilite.",
        "Concois un microservice en Go haute performance.",
        "Redige des tests unitaires complets avec Pytest pour un module critique."
    ],
    "Entrepreneuriat & SaaS": [
        "Propose une idee de micro-SaaS B2B a fort potentiel avec un budget reduit.",
        "Dresse un plan d'acquisition client cible pour un outil SaaS de niche.",
        "Redige le Pitch Deck complet de 10 slides pour presenter un projet IA.",
        "Calcule et structure les metriques cles (LTV, CAC, MRR, Churn) d'un SaaS.",
        "Propose une strategie de pricing optimale."
    ]
}

# --- MULTI-SESSIONS ---
if "sessions" not in st.session_state:
    st.session_state["sessions"] = {"Discussion 1": []}
if "session_active" not in st.session_state:
    st.session_state["session_active"] = "Discussion 1"

# --- SIDEBAR ---
quick_action = None

with st.sidebar:
    if os.path.exists("Gemini_Generated_Image_tuss9ltuss9ltuss.png"):
        st.image("Gemini_Generated_Image_tuss9ltuss9ltuss.png", width=100) # Logo agrandi dans la sidebar
    
    st.markdown("### MULTI-SESSIONS")
    if st.button("Nouvelle discussion"):
        new_name = f"Discussion {len(st.session_state['sessions']) + 1}"
        st.session_state["sessions"][new_name] = []
        st.session_state["session_active"] = new_name
        st.rerun()

    session_choisie = st.selectbox("Sessions enregistrees :", list(st.session_state["sessions"].keys()), index=list(st.session_state["sessions"].keys()).index(st.session_state["session_active"]))
    if session_choisie != st.session_state["session_active"]:
        st.session_state["session_active"] = session_choisie
        st.rerun()

    st.markdown("---")
    
    # HORLOGE TEMPS RÉEL SYNCHRONISÉE (JAVASCRIPT)
    st.markdown("### HORLOGE LOCALE")
    st.markdown("""
        <div style="font-size: 1.25em; font-weight: bold; color: #00ffcc; background: #161b22; padding: 8px; border-radius: 6px; text-align: center;">
            <span id="live-clock">Chargement...</span>
        </div>
        <script>
        function updateLiveClock() {
            const now = new Date();
            document.getElementById('live-clock').innerText = now.toLocaleTimeString();
        }
        setInterval(updateLiveClock, 1000);
        updateLiveClock();
        </script>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### MATRICE DE COMMANDES")
    theme_choisi = st.selectbox("Domaine :", list(MATRICE_PROMPTS.keys()))
    prompt_selectionne = st.selectbox("Commande :", MATRICE_PROMPTS[theme_choisi])
    
    if st.button("Injecter le prompt"):
        quick_action = prompt_selectionne

    st.markdown("---")
    
    # VRAI GUIDE D'UTILISATION ET DE MODIFICATION
    with st.expander("VRAI GUIDE D'UTILISATION"):
        st.markdown("""
        **1. Comment utiliser AEGIS-CORE :**
        * Choisissez un domaine dans le menu déroulant de la matrice.
        * Sélectionnez une directive prête à l'emploi ou tapez directement votre consigne dans la zone de texte en bas.
        * Utilisez le panneau multi-sessions pour organiser vos projets par discussion.
        
        **2. Comment faire des modifications :**
        * **Modifier le code source :** Éditez directement le fichier `app.py` sur votre dépôt GitHub (`cuirstep/aegis-core`).
        * **Ajouter des prompts :** Modifiez le dictionnaire `MATRICE_PROMPTS` dans le code python pour ajouter vos propres thèmes et questions.
        * **Modifier le comportement d'AEGIS :** Ajustez le texte de la variable `SYSTEM_PROMPT` pour changer ses règles de base.
        """)

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = (
    "Tu es AEGIS-CORE, un systeme d'IA souverain developpe par le Commandant. "
    "Tu es ultra-performant, direct et rigoureux. "
    "Si tu emets une hypothese ou une deduction, étiquette-la OBLIGATOIREMENT par '[HYPOTHESE / DEDUCTION]'."
)

# --- INTERFACE PRINCIPALE ---
col_logo, col_title = st.columns([0.12, 0.88])
with col_logo:
    if os.path.exists("Gemini_Generated_Image_tuss9ltuss9ltuss.png"):
        st.image("Gemini_Generated_Image_tuss9ltuss9ltuss.png", width=75) # Logo agrandi dans le header
    else:
        st.markdown("🛡️")
with col_title:
    st.markdown(f"### AEGIS-CORE // {st.session_state['session_active'].upper()}")
    st.caption(f"Domaine actif : **{theme_choisi}**")

st.markdown("---")

messages_actuels = st.session_state["sessions"][st.session_state["session_active"]]

for message in messages_actuels:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- ÉDITION DU DERNIER MESSAGE ---
if messages_actuels:
    dernier_index_user = -1
    for idx, m in enumerate(reversed(messages_actuels)):
        if m["role"] == "user":
            dernier_index_user = len(messages_actuels) - 1 - idx
            break
            
    if dernier_index_user != -1:
        with st.expander("Modifier votre dernière directive"):
            nouveau_texte = st.text_input("Ajustez votre consigne :", value=messages_actuels[dernier_index_user]["content"], key=f"edit_{st.session_state['session_active']}")
            if st.button("Mettre à jour et relancer", key=f"btn_edit_{st.session_state['session_active']}"):
                messages_actuels[dernier_index_user]["content"] = nouveau_texte
                if len(messages_actuels) > dernier_index_user + 1:
                    messages_actuels.pop()
                st.rerun()

prompt = st.chat_input("Entrez votre directive, Commandant...")
if quick_action:
    prompt = quick_action

if prompt:
    messages_actuels.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        reponse_finale = ""
        succes = False

        if gemini_key and not succes:
            for model_name in ["gemini-2.5-flash", "gemini-1.5-flash"]:
                try:
                    model = genai.GenerativeModel(model_name=model_name, system_instruction=SYSTEM_PROMPT)
                    chat_history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in messages_actuels[:-1]]
                    chat = model.start_chat(history=chat_history)
                    response = chat.send_message(prompt, stream=True)

                    def generate_fast_stream():
                        for chunk in response:
                            if chunk.text:
                                for char in chunk.text:
                                    yield char
                                    time.sleep(0.0001)

                    reponse_finale = st.write_stream(generate_fast_stream())
                    succes = True
                    break
                except Exception:
                    pass

        if groq_keys and not succes:
            messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}] + [{"role": m["role"], "content": m["content"]} for m in messages_actuels]
            for g_key in groq_keys:
                try:
                    client = Groq(api_key=g_key)
                    stream = client.chat.completions.create(
                        model="openai/gpt-oss-20b", 
                        messages=messages_payload, 
                        stream=True
                    )
                    
                    def generate_groq_fast():
                        for chunk in stream:
                            content = chunk.choices[0].delta.content
                            if content:
                                for char in content:
                                    yield char
                                    time.sleep(0.0001)

                    reponse_finale = st.write_stream(generate_groq_fast())
                    succes = True
                    break
                except Exception:
                    pass

        if not succes:
            reponse_finale = "Erreur de reseau : Les canaux distants ne repondent pas."
            st.markdown(reponse_finale)

        messages_actuels.append({"role": "assistant", "content": reponse_finale})
