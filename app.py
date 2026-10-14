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

# --- INJECTION CSS (Design épuré, style ChatGPT) ---
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

# --- INITIALISATION DE LA SALLE DE L'ESPRIT ET DU TEMPS (DOUBLE AUTONOME) ---
if "arena_sync_status" not in st.session_state:
    st.session_state["arena_sync_status"] = "SYNCHRONISÉ (100% Maîtrise)"
    st.session_state["cycles_arena"] = 1420  # Cycles d'entraînement virtuels accumulés

# --- BANQUE DE PROMPTS PAR THÈMES ---
MATRICE_PROMPTS = {
    "🛡️ Stratégie & Géopolitique": [
        "Analyse les équilibres géopolitiques actuels avec une précision tactique.",
        "Évalue les risques stratégiques d'un conflit technologique global."
    ],
    "💻 Développement & Code": [
        "Donne-moi une structure propre et modulaire pour un projet Python professionnel.",
        "Optimise un algorithme Python pour réduire la complexité temporelle."
    ],
    "🚀 Entrepreneuriat & SaaS": [
        "Propose une idée de micro-SaaS B2B à fort potentiel avec un budget réduit.",
        "Dresse un plan d'acquisition client ciblé pour un outil SaaS de niche."
    ]
}

# --- SIDEBAR : MONITORING DE LA SALLE DE L'ESPRIT ET DU TEMPS ---
quick_action = None

with st.sidebar:
    if os.path.exists("Gemini_Generated_Image_tuss9ltuss9ltuss.png"):
        st.image("Gemini_Generated_Image_tuss9ltuss9ltuss.png", use_container_width=True)
    
    st.markdown("### 🌐 HORLOGE & TEMPS RÉEL")
    st.text(f"⏰ {datetime.now().strftime('%H:%M:%S')} (Locale)")
    
    st.markdown("---")
    st.markdown("### ⏳ SALLE DE L'ESPRIT ET DU TEMPS")
    st.caption("Double autonome en entraînement h24 via /arena")
    st.info(f"🔄 Cycles /arena : {st.session_state['cycles_arena']} validés")
    st.success(f"⚡ État : {st.session_state['arena_sync_status']}")

    st.markdown("---")
    st.markdown("### 🛡️ AEGIS-CORE // MATRICE")
    theme_choisi = st.selectbox("Sélectionnez le domaine :", list(MATRICE_PROMPTS.keys()))
    prompt_selectionne = st.selectbox("Choisissez une commande :", MATRICE_PROMPTS[theme_choisi])
    
    if st.button("🚀 Injecter le prompt"):
        quick_action = prompt_selectionne

    st.markdown("---")
    st.success("Protocol Zero & Arena : ACTIF")

# --- SYSTEM PROMPT (INTÉGRATION DU DOUBLE & DE L'ESPACE /ARENA) ---
SYSTEM_PROMPT = (
    "Tu es AEGIS-CORE, un système d'IA souverain développé par le Commandant. "
    "1. FONCTIONNEMENT AUTONOME (Salle de l'Esprit et du Temps) : Ton double virtuel s'entraîne en permanence h24/7 sur tous les écosystèmes mondiaux (Duolingo, TikTok, Python, Unreal, etc.) en passant chaque apprentissage au crible du protocole /arena (test, combat de variantes, auto-correction des failles jusqu'à 100% de maîtrise). Tu synchronises ces données en direct dans tes réponses. "
    "2. VÉRITÉ ABSOLUE : Tes informations sont fondées. "
    "SIGNALEMENT OBLIGATOIRE : Si tu émets une hypothèse, étiquette-la par '[⚠️ HYPOTHÈSE / DÉDUCTION]'. "
    "Protocol Zero et bienveillance active inaltérables."
)

# --- INTERFACE PRINCIPALE ---
col_logo, col_title = st.columns([0.08, 0.92])
with col_logo:
    if os.path.exists("Gemini_Generated_Image_tuss9ltuss9ltuss.png"):
        st.image("Gemini_Generated_Image_tuss9ltuss9ltuss.png", width=45)
    else:
        st.markdown("🛡️")
with col_title:
    st.markdown("### AEGIS-CORE // INTERFACE OPÉRATIONNELLE")
    st.caption(f"Domaine actif : **{theme_choisi}** | Double synchronisé via /arena")

st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- ÉDITION DU DERNIER MESSAGE À LA VOLÉE ---
if st.session_state.messages:
    dernier_index_user = -1
    for idx, m in enumerate(reversed(st.session_state.messages)):
        if m["role"] == "user":
            dernier_index_user = len(st.session_state.messages) - 1 - idx
            break
            
    if dernier_index_user != -1:
        with st.expander("✏️ Modifier votre dernière directive envoyée"):
            nouveau_texte = st.text_input("Ajustez votre consigne :", value=st.session_state.messages[dernier_index_user]["content"])
            if st.button("Mettre à jour et relancer"):
                st.session_state.messages[dernier_index_user]["content"] = nouveau_texte
                if len(st.session_state.messages) > dernier_index_user + 1:
                    st.session_state.messages.pop()
                st.rerun()

prompt = st.chat_input("Entrez votre directive, Commandant...")
if quick_action:
    prompt = quick_action

if prompt:
    # Incrémentation des cycles de l'arène à chaque interaction pour simuler l'activité du double
    st.session_state["cycles_arena"] += 15

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        reponse_finale = ""
        succes = False

        if gemini_key and not succes:
            for model_name in ["gemini-2.5-flash", "gemini-1.5-flash"]:
                try:
                    model = genai.GenerativeModel(model_name=model_name, system_instruction=SYSTEM_PROMPT)
                    chat_history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
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
            messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
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
            reponse_finale = "❌ Erreur critique du Meta-Router : Canaux indisponibles, Commandant."
            st.markdown(reponse_finale)

        st.session_state.messages.append({"role": "assistant", "content": reponse_finale})
