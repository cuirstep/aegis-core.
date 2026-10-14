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

# --- BANQUE DE PROMPTS COMPLÈTE ---
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

# --- FONCTION DE VEILLE & FLUX ---
def connecter_flux_mondial(cible):
    try:
