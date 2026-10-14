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
github_token = st.secrets.get("GITHUB_TOKEN", "") # Optionnel pour booster les quotas GitHub
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

# --- FONCTIONS DE CONNEXION AUX API CIBLÉES ---
def fetch_github_trending():
    """Interroge l'API GitHub pour récupérer les repos Python/AI du moment"""
    try:
        url = "https://api.github.com/search/repositories?q=topic:artificial-intelligence+language:python&sort=stars&order=desc"
        headers = {"Authorization": f"Bearer {github_token}"} if github_token else {}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            items = response.json().get("items", [])[:3]
            return [f"- **{item['name']}** (⭐ {item['stargazers_count']}) : {item['description']}" for item in items]
    except Exception:
        pass
    return ["⚠️ Flux GitHub momentanément indisponible."]

# --- BANQUE DE PROMPTS ---
MATRICE_PROMPTS = {
    "🛡️ Stratégie & Géopolitique": [
        "Analyse les équilibres géopolitiques actuels avec une précision tactique.",
        "Évalue les risques stratégiques d'un conflit technologique global."
    ],
    "💻 Développement & Code": [
        "Donne-moi une structure propre et modulaire pour un projet Python professionnel.",
        "Optimise un algorithme Python pour réduire la complexité temporelle."
    ],
    "🌍 Veille Live & Données Externes": [
        "Analyse les derniers projets open-source tendance sur GitHub récupérés par le système.",
        "Dresse un rapport stratégique basé sur l'actualité technologique mondiale en direct."
    ]
}

# --- SIDEBAR : HORLOGE ET CONNECTEURS ---
quick_action = None

with st.sidebar:
    if os.path.exists("Gemini_Generated_Image_tuss9ltuss9ltuss.png"):
        st.image("Gemini_Generated_Image_tuss9ltuss9ltuss.png", use_container_width=True)
    
    # Horloge locale
    st.markdown("### 🌐 HORLOGE LOCALE & MONDIALE")
    st.text(f"⏰ {datetime.now().strftime('%H:%M:%S')} (Locale)")
    
    st.markdown("---")
    st.markdown("### 📡 VEILLE API EN DIRECT")
    if st.button("🔄 Actualiser les flux GitHub"):
        repos_tendances = fetch_github_trending()
        st.session_state["flux_github"] = "\n".join(repos_tendances)
        st.success("Flux GitHub actualisé avec succès !")

    if "flux_github" in st.session_state:
        with st.expander("📌 Dernières tendances GitHub"):
            st.markdown(st.session_state["flux_github"])

    st.markdown("---")
    st.markdown("### 🛡️ AEGIS-CORE // MATRICE")
    theme_choisi = st.selectbox("Sélectionnez le domaine :", list(MATRICE_PROMPTS.keys()))
    prompt_selectionne = st.selectbox("Choisissez une commande :", MATRICE_PROMPTS[theme_choisi])
    
    if st.button("🚀 Injecter le prompt"):
        quick_action = prompt_selectionne

    st.markdown("---")
    st.success("Connecteurs API & Protocol Zero : ACTIF")

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = (
    "Tu es AEGIS-CORE, un système d'IA souverain développé par le Commandant. "
    "1. VÉRITÉ ABSOLUE : Tes informations doivent être fondées et vérifiées. "
    "SIGNALEMENT OBLIGATOIRE : Si tu émets une hypothèse, étiquette-la par '[⚠️ HYPOTHÈSE / DÉDUCTION]'. "
    "2. VEILLE ACTIVE : Tu exploites les données connectées en temps réel (GitHub, API, flux) pour analyser l'écosystème technique et viser le dépassement."
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
    st.caption(f"Domaine actif : **{theme_choisi}** | Connexion API active")

st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- MODIFICATION DU DERNIER MESSAGE À LA VOLÉE ---
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
    # Si le flux GitHub est chargé, on l'injecte discrètement dans le contexte du prompt si l'utilisateur le demande
    contexte_supplementaire = ""
    if "flux_github" in st.session_state and "GitHub" in prompt:
        contexte_supplementaire = f"\n\n[Données en direct GitHub actuelles :\n{st.session_state['flux_github']}]"

    prompt_final_enrichi = prompt + contexte_supplementaire

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
                    response = chat.send_message(prompt_final_enrichi, stream=True)

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
