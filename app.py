import streamlit as st
import os
import time
import base64
from datetime import datetime
from groq import Groq
import google.generativeai as genai

st.set_page_config(
    page_title="AEGIS-CORE // BETA", 
    page_icon="assets/aegis_logo.png" if os.path.exists("assets/aegis_logo.png") else "🛡️", 
    layout="wide"
)

# --- INJECTION CSS & ANIMATION DE BRUME (BÊTA INTRO) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {
        display: none !important;
    }

    /* Animation d'introduction style brume / cyber-déroulé */
    @keyframes aegisFadeIn {
        0% { opacity: 0; filter: blur(20px); transform: scale(0.95); }
        50% { opacity: 0.5; filter: blur(10px); }
        100% { opacity: 1; filter: blur(0px); transform: scale(1); }
    }

    .aegis-intro-banner {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: radial-gradient(circle, #161b22 0%, #0e1117 100%);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 99999;
        animation: aegisFadeIn 2.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    .aegis-title-glow {
        font-size: 4rem;
        font-weight: 900;
        letter-spacing: 0.2em;
        color: #ff2a2a;
        text-shadow: 0 0 20px rgba(255, 42, 42, 0.6), 0 0 40px rgba(0, 255, 204, 0.3);
        margin-bottom: 10px;
    }

    .aegis-subtitle {
        font-size: 1.2rem;
        color: #00ffcc;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }
    </style>

    <!-- Écran d'animation d'introduction de la Bêta -->
    <div id="intro-banner" class="aegis-intro-banner">
        <div class="aegis-title-glow">AEGIS-CORE</div>
        <div class="aegis-subtitle">BÊTA OPÉRATIONNELLE // PROTOCOLE MILITAIRE</div>
    </div>

    <script>
    // Disparition de l'animation après 2.5 secondes + Synthèse vocale d'accueil
    setTimeout(function() {
        const banner = document.getElementById('intro-banner');
        if (banner) {
            banner.style.transition = 'opacity 0.8s ease';
            banner.style.opacity = '0';
            setTimeout(() => banner.remove(), 800);
        }
        
        // Synthèse vocale militaire d'activation
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance("Système Aegis Core en ligne. Prêt pour les directives, Commandant.");
            utterance.rate = 0.9;
            utterance.pitch = 0.8; // Voix plus grave / militaire
            utterance.lang = 'fr-FR';
            window.speechSynthesis.speak(utterance);
        }
    }, 2500);
    </script>
""", unsafe_allow_html=True)

# --- FONCTION POUR CHARGER LES ÉMOJIS D'ÉLITE ---
def get_base64_img(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def custom_icon(path, size=24):
    b64 = get_base64_img(path)
    if b64:
        return f'<img src="data:image/png;base64,{b64}" width="{size}" style="vertical-align: middle; margin-right: 8px;">'
    return ""

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

# --- MATRICE PROMPTS ---
MATRICE_PROMPTS = {
    "Pédagogie, Quiz & Résumés": [
        "Genere un Quiz interactif de 5 questions a choix multiples base sur notre derniere discussion.",
        "Redige une fiche de synthese pedagogique claire et structuree du projet en cours.",
        "Concois un plan de formation étape par étape pour maîtriser ce sujet de A à Z.",
        "Genere une fiche de revision rapide sous forme de carte mentale textuelle."
    ],
    "Stratégie & Géopolitique": [
        "Analyse les equilibres geopolitiques actuels avec une precision tactique.",
        "Evalue les risques strategiques d'un conflit technologique global."
    ],
    "Développement & Code": [
        "Donne-moi une structure propre et modulaire pour un projet Python professionnel.",
        "Optimise un algorithme Python pour reduire la complexite temporelle."
    ],
    "Entrepreneuriat & SaaS": [
        "Propose une idee de micro-SaaS B2B a fort potentiel avec un budget reduit.",
        "Dresse un plan d'acquisition client cible pour un outil SaaS de niche."
    ]
}

# --- MULTI-SESSIONS ---
if "sessions" not in st.session_state:
    st.session_state["sessions"] = {"Discussion 1": []}
if "session_active" not in st.session_state:
    st.session_state["session_active"] = "Discussion 1"

# --- SIDEBAR ÉPURÉE (BÊTA) ---
quick_action = None

with st.sidebar:
    if os.path.exists("assets/aegis_logo.png"):
        st.image("assets/aegis_logo.png", width=120)
    
    icon_sessions = custom_icon("assets/aegis_sessions.png")
    st.markdown(f"### {icon_sessions} MULTI-SESSIONS", unsafe_allow_html=True)
    
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
    icon_code = custom_icon("assets/aegis_code.png")
    st.markdown(f"### {icon_code} MATRICE DE COMMANDES", unsafe_allow_html=True)
    theme_choisi = st.selectbox("Domaine :", list(MATRICE_PROMPTS.keys()))
    prompt_selectionne = st.selectbox("Commande :", MATRICE_PROMPTS[theme_choisi])
    
    if st.button("🚀 Injecter le prompt"):
        quick_action = prompt_selectionne

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = (
    "Tu es AEGIS-CORE (Version Bêta), un systeme d'IA souverain developpe par le Commandant. "
    "Tu es ultra-performant, direct, militaire et rigoureux. "
    "Si tu emets une hypothese ou une deduction, étiquette-la OBLIGATOIREMENT par '[HYPOTHESE / DEDUCTION]'."
)

# --- INTERFACE PRINCIPALE ---
col_logo, col_title = st.columns([0.12, 0.88])
with col_logo:
    if os.path.exists("assets/aegis_logo.png"):
        st.image("assets/aegis_logo.png", width=80)
    else:
        st.markdown("🛡️")
with col_title:
    st.markdown(f"### AEGIS-CORE // {st.session_state['session_active'].upper()} [BETA]")
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
        with st.expander("✏️ Modifier votre dernière directive"):
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
            reponse_finale = "❌ Erreur de réseau : Les canaux distants ne répondent pas."
            st.markdown(reponse_finale)

        # SYNTHÈSE VOCALE AUTOMATIQUE DE LA RÉPONSE
        st.markdown(f"""
            <script>
            if ('speechSynthesis' in window) {{
                const utterance = new SpeechSynthesisUtterance({repr(reponse_finale[:200])});
                utterance.rate = 0.95;
                utterance.pitch = 0.8;
                utterance.lang = 'fr-FR';
                window.speechSynthesis.speak(utterance);
            }}
            </script>
        """, unsafe_allow_html=True)

        messages_actuels.append({"role": "assistant", "content": reponse_finale})
