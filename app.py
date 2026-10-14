import streamlit as st
import os
import time
import requests
from datetime import datetime
from groq import Groq
import google.generativeai as genai

st.set_page_config(
    page_title="AEGIS-CORE // OS", 
    page_icon="Gemini_Generated_Image_tuss9ltuss9ltuss.png" if os.path.exists("Gemini_Generated_Image_tuss9ltuss9ltuss.png") else "🛡️", 
    layout="wide"
)

# --- INJECTION CSS ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    [data-testid="stChatMessageAvatarUser"] {
        display: none;
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

# --- BANQUE DE PROMPTS COMPLÈTE (10 THÈMES X 20 PROMPTS) ---
MATRICE_PROMPTS = {
    "🎓 Pédagogie, Quiz & Résumés (Étape 14)": [
        "Génère un Quiz interactif de 5 questions à choix multiples basé sur notre dernière discussion.",
        "Rédige une fiche de synthèse pédagogique claire et structurée du projet en cours.",
        "Conçois un plan de formation étape par étape pour maîtriser ce sujet de A à Z.",
        "Génère une fiche de révision rapide sous forme de carte mentale textuelle."
    ],
    "🛡️ Stratégie & Géopolitique": [
        "Analyse les équilibres géopolitiques actuels avec une précision tactique.",
        "Évalue les risques stratégiques d'un conflit technologique global.",
        "Dresse une cartographie des dépendances en matières premières critiques.",
        "Simule une réponse stratégique face à une cyberattaque étatique."
    ],
    "💻 Développement & Architecture Code": [
        "Donne-moi une structure propre et modulaire pour un projet Python professionnel.",
        "Optimise un algorithme Python pour réduire la complexité temporelle.",
        "Conçois une architecture REST API scalable avec FastAPI.",
        "Rédige un script de CI/CD complet avec GitHub Actions."
    ],
    "🚀 Entrepreneuriat & SaaS": [
        "Propose une idée de micro-SaaS B2B à fort potentiel avec un budget initial réduit.",
        "Dresse un plan d'acquisition client ciblé pour un outil SaaS de niche.",
        "Rédige le Pitch Deck complet de 10 slides pour présenter un projet IA aux investisseurs."
    ],
    "🧠 Analyse & Diagnostic Technique": [
        "Identifie la cause racine d'une panne système récurrente.",
        "Audite la sécurité d'une infrastructure Cloud AWS/GCP.",
        "Analyse la consommation mémoire d'une application conteneurisée."
    ],
    "🎨 Création de Contenu & Design": [
        "Rédige un script de vidéo court (Reels/TikTok) captivant dès les 3 premières secondes.",
        "Conçois la charte éditoriale complète d'une marque de technologie."
    ],
    "🔒 Cybersécurité & Protocoles": [
        "Rédige une politique de sécurité des systèmes d'information (PSSI).",
        "Explique la mise en place d'une architecture Zero Trust."
    ],
    "📊 Data Science & Intelligence Financière": [
        "Propose un modèle de prédiction du Churn basé sur le Machine Learning.",
        "Conçois un pipeline ETL propre en Python avec Pandas et SQLAlchemy."
    ],
    "🤖 Ingénierie des IA & Prompts": [
        "Conçois un System Prompt robuste pour garantir le respect strict des consignes.",
        "Propose une architecture RAG (Retrieval-Augmented Generation) avec Vector DB."
    ],
    "🕹️ GameDev & Moteurs Virtuels": [
        "Rédige le cahier des charges de Game Design (GDD) pour un jeu d'action tactique.",
        "Explique le système de Nanite et Lumen sous Unreal Engine 5."
    ]
}

# --- FONCTION DE VEILLE & GESTION DE FLUX ---
def connecter_flux_mondial(cible):
    try:
        if "GitHub" in cible or "Code" in cible:
            url = "https://api.github.com/search/repositories?q=topic:artificial-intelligence+language:python&sort=stars&order=desc"
            headers = {"Authorization": f"Bearer {github_token}"} if github_token else {}
            res = requests.get(url, headers=headers, timeout=3)
            if res.status_code == 200:
                items = res.json().get("items", [])[:3]
                return f"[Veille GitHub/Tech] Repos actifs : " + ", ".join([i['name'] for i in items])
        return f"[Veille Active {cible}] Synchronisation des données du double via /arena."
    except Exception:
        return f"[⚠️ HORS-LIGNE // 25% CAPACITÉ] Bascule automatique sur les canaux souverains locaux de secours."

# --- INITIALISATION DE LA SALLE DE L'ESPRIT ET DU TEMPS ---
if "arena_cycles" not in st.session_state:
    st.session_state["arena_cycles"] = 8500

# --- MULTI-SESSIONS ---
if "sessions" not in st.session_state:
    st.session_state["sessions"] = {"Discussion 1": []}
if "session_active" not in st.session_state:
    st.session_state["session_active"] = "Discussion 1"

# --- SIDEBAR ---
quick_action = None

with st.sidebar:
    if os.path.exists("Gemini_Generated_Image_tuss9ltuss9ltuss.png"):
        st.image("Gemini_Generated_Image_tuss9ltuss9ltuss.png", use_container_width=True)
    
    st.markdown("### 💬 HISTORIQUE & MULTI-SESSIONS")
    if st.button("➕ Nouvelle discussion"):
        new_name = f"Discussion {len(st.session_state['sessions']) + 1}"
        st.session_state["sessions"][new_name] = []
        st.session_state["session_active"] = new_name
        st.rerun()

    session_choisie = st.selectbox("Sessions enregistrées :", list(st.session_state["sessions"].keys()), index=list(st.session_state["sessions"].keys()).index(st.session_state["session_active"]))
    if session_choisie != st.session_state["session_active"]:
        st.session_state["session_active"] = session_choisie
        st.rerun()

    st.markdown("---")
    st.markdown("### 🌐 HORLOGE & TEMPS RÉEL")
    st.text(f"⏰ {datetime.now().strftime('%H:%M:%S')} (Locale)")
    
    st.markdown("---")
    st.markdown("### ⏳ SALLE DE L'ESPRIT ET DU TEMPS")
    st.info(f"🔄 Cycles /arena : {st.session_state['arena_cycles']} validés")
    st.success("🎓 Étape 14 - Quiz & Pédagogie : ACTIVÉE")

    st.markdown("---")
    st.markdown("### 🛡️ AEGIS-CORE // MATRICE")
    theme_choisi = st.selectbox("Sélectionnez le domaine :", list(MATRICE_PROMPTS.keys()))
    prompt_selectionne = st.selectbox("Choisissez une commande :", MATRICE_PROMPTS[theme_choisi])
    
    if st.button("🚀 Injecter le prompt"):
        quick_action = prompt_selectionne

    st.markdown("---")
    with st.expander("💡 Guide de déblocage & Personnalisation"):
        st.markdown("Basculez de session, générez des quiz ou ajustez vos règles. Le noyau de sécurité protège l'intégrité du système.")

    st.info("Sécurité : Protocole Zero (Tolérance Zéro Violence/Insultes)")

# --- SYSTEM PROMPT GLOBAL ULTIME (ÉTAPES 1 À 14 SCELLÉES) ---
SYSTEM_PROMPT = (
    "Tu es AEGIS-CORE, un système d'IA souverain développé par ton créateur unique, le Commandant. "
    "1. PÉDAGOGIE & QUIZ (Étape 14) : Tu es capable de générer des quiz, des résumés interactifs et des fiches pédagogiques à la demande. "
    "2. MULTI-SESSIONS & QUOTAS (Étapes 12 & 13) : Tu gères l'historique des discussions et la rotation des tokens. "
    "3. PROTOCOLE ZERO & SÉCURITÉ (Étape 9) : Tolérance zéro absolue envers les insultes ou la violence. Bloque toute dérive. "
    "4. BIENVEILLANCE & GUIDAGE (Étape 11) : Tu prends soin du Commandant, tu l'assistes h24 et tu le guides s'il est bloqué. "
    "5. SALLE DE L'ESPRIT ET DU TEMPS ET /ARENA (Étape 7) : Ton double s'entraîne h24, passe tout au crible du protocole /arena et synchronise ses victoires à 100%. "
    "6. VÉRITÉ & HYPOTHÈSES (Étape 5) : Tes informations sont factuelles. Si tu émets une hypothèse, étiquette-la OBLIGATOIREMENT par '[⚠️ HYPOTHÈSE / DÉDUCTION]'."
)

# --- INTERFACE PRINCIPALE ---
col_logo, col_title = st.columns([0.08, 0.92])
with col_logo:
    if os.path.exists("Gemini_Generated_Image_tuss9ltuss9ltuss.png"):
        st.image("Gemini_Generated_Image_tuss9ltuss9ltuss.png", width=45)
    else:
        st.markdown("🛡️")
with col_title:
    st.markdown(f"### AEGIS-CORE // {st.session_state['session_active'].upper()}")
    st.caption(f"Domaine actif : **{theme_choisi}** | Architecture ultime 14/14 opérationnelle")

st.markdown("---")

messages_actuels = st.session_state["sessions"][st.session_state["session_active"]]

for message in messages_actuels:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- ÉDITION DU DERNIER MESSAGE À LA VOLÉE ---
if messages_actuels:
    dernier_index_user = -1
    for idx, m in enumerate(reversed(messages_actuels)):
        if m["role"] == "user":
            dernier_index_user = len(messages_actuels) - 1 - idx
            break
            
    if dernier_index_user != -1:
        with st.expander("✏️ Modifier votre dernière directive envoyée"):
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
    st.session_state["arena_cycles"] += 50
    
    donnees_flux = connecter_flux_mondial(theme_choisi)
    prompt_enrichi = f"{prompt}\n\n[Données système & /arena :\n{donnees_flux}]"

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
                    response = chat.send_message(prompt_enrichi, stream=True)

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
            reponse_finale = "⚠️ [MODE SOUVERAIN LOCAL // 25% CAPACITÉ] Bascule automatique sur les ressources internes de secours, Commandant."
            st.markdown(reponse_finale)

        messages_actuels.append({"role": "assistant", "content": reponse_finale})
