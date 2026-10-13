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
    
    /* Masquer l'avatar utilisateur par défaut */
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

# --- BANQUE DE PROMPTS (10 THÈMES X 20 PROMPTS) ---
MATRICE_PROMPTS = {
    "🛡️ Stratégie & Géopolitique": [
        "Analyse les équilibres géopolitiques actuels avec une précision tactique.",
        "Évalue les risques stratégiques d'un conflit technologique global.",
        "Dresse une cartographie des dépendances en matières premières critiques.",
        "Simule une réponse stratégique face à une cyberattaque étatique.",
        "Analyse l'impact de la souveraineté numérique sur l'économie européenne.",
        "Rédige une note de synthèse sur la doctrine de défense spatiale.",
        "Examine les implications de la militarisation de l'IA.",
        "Analyse l'évolution des doctrines de dissuasion moderne.",
        "Dresse un bilan des vulnérabilités des infrastructures critiques navales.",
        "Évalue les stratégies de résilience de la chaîne d'approvisionnement globale.",
        "Analyse les enjeux stratégiques des câbles sous-marins de télécommunication.",
        "Propose un plan d'action pour sécuriser les données sensibles d'un État.",
        "Rédige un scénario de gestion de crise face à une panne électrique majeure.",
        "Analyse les stratégies de souveraineté alimentaire d'une nation insulaire.",
        "Évalue l'impact des monnaies numériques de banque centrale (MNBC) sur le commerce international.",
        "Propose une grille d'analyse des alliances géopolitiques émergentes.",
        "Rédige un rapport d'évaluation des menaces hybrides et désinformation.",
        "Analyse la géopolitique des semi-conducteurs en Asie-Pacifique.",
        "Examine le rôle de l'intelligence artificielle dans la surveillance des frontières.",
        "Rédige une doctrine de réponse rapide pour un poste de commandement."
    ],
    "💻 Développement & Architecture Code": [
        "Donne-moi une structure propre et modulaire pour un projet Python professionnel.",
        "Optimise un algorithme Python pour réduire la complexité temporelle.",
        "Conçois une architecture REST API scalable avec FastAPI.",
        "Propose un schéma de base de données PostgreSQL pour un système multi-tenant.",
        "Rédige un script de CI/CD complet avec GitHub Actions.",
        "Analyse et réfactore ce bloc de code pour améliorer la lisibilité.",
        "Conçois un microservice en Go haute performance.",
        "Rédige des tests unitaires complets avec Pytest pour un module critique.",
        "Propose une architecture microservices basée sur des événements (Kafka).",
        "Rédige un script Dockerfile optimisé et multi-stage build.",
        "Explique et implémente le pattern Singleton et Factory en Python.",
        "Conçois une stratégie de gestion des erreurs et logging centralisé.",
        "Crée une classe Python abstraite pour gérer divers moteurs de base de données.",
        "Optimise une requête SQL complexe avec des index appropriés.",
        "Rédige un script Web Scraping robuste avec gestion des proxies et retries.",
        "Implémente un système de cache Redis pour accélérer les requêtes d'API.",
        "Explique les meilleures pratiques de sécurité pour prévenir l'injection SQL et XSS.",
        "Rédige une documentation Swagger/OpenAPI claire pour un service Web.",
        "Analyse les goulots d'étranglement de mémoire dans une application Python.",
        "Propose une migration propre d'un monolithe vers une architecture serverless."
    ],
    "🚀 Entrepreneuriat & SaaS": [
        "Propose une idée de micro-SaaS B2B à fort potentiel avec un budget initial réduit.",
        "Dresse un plan d'acquisition client ciblé pour un outil SaaS de niche.",
        "Rédige le Pitch Deck complet de 10 slides pour présenter un projet IA aux investisseurs.",
        "Calcule et structure les métriques clés (LTV, CAC, MRR, Churn) d'un SaaS.",
        "Propose une stratégie de pricing optimale (Freemium vs Tiered Pricing).",
        "Rédige le script d'une vidéo explicative de 60 secondes pour un produit Tech.",
        "Analyse la concurrence et identifie un océan bleu dans le secteur de la EdTech.",
        "Propose un plan de lancement Product Hunt étape par étape.",
        "Rédige la séquence d'emails de bienvenue automatisée pour convertir les utilisateurs gratuits.",
        "Structure un cahier des charges MVP pour une application mobile.",
        "Analyse les canaux d'acquisition
