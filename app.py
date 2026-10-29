import os
import json
import base64
import time
import requests
import io
import streamlit as st
from llm_router import route_and_generate

def text_to_speech_elevenlabs(text, langue="fr"):
    api_key = st.secrets.get("ELEVENLABS_API_KEY", "")
    if not api_key:
        return None
        
    voix_par_langue = {
        "fr": "xclXfpLYbMIBNgiHTm8S",
        "en": "DODLEQrClDo8wCz460ld",
        "es": "U9TSK9KHMlMU2qkeXlQP",
        "ar": "Ywuz3KyW2N5pqKNpwcCL",
        "pt": "IKpiSijWzlhOL6uX83EH"
    }
    
    voice_id = voix_par_langue.get(langue, "xclXfpLYbMIBNgiHTm8S")
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.content
    except Exception:
        pass
    return None
    
from database import init_db, register_user, verify_user, init_chat_db, save_user_session, load_user_sessions

st.set_page_config(
    page_title="AEGIS-CORE // BETA", 
    page_icon="🛡️", 
    layout="wide"
)

init_db()
init_chat_db()

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# Chargement de la session persistance SQLite
if "sessions" not in st.session_state:
    if st.session_state.current_user:
        loaded = load_user_sessions(st.session_state.current_user)
        st.session_state["sessions"] = loaded if loaded else {"Discussion 1": []}
    else:
        st.session_state["sessions"] = {"Discussion 1": []}

if "session_active" not in st.session_state or st.session_state["session_active"] not in st.session_state["sessions"]:
    st.session_state["session_active"] = list(st.session_state["sessions"].keys())[0]

# --- INJECTION CSS & ANIMATION DE DÉMARRAGE ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    [data-testid="stChatMessageAvatarUser"], 
    [data-testid="stChatMessageAvatarAssistant"],
    .stChatMessageAvatar,
    div[data-testid="chatAvatarIcon-user"],
    div[data-testid="chatAvatarIcon-assistant"] {
        display: none !important;
        visibility: hidden !important;
        width: 0px !important;
        height: 0px !important;
        margin: 0px !important;
        padding: 0px !important;
    }
    
    @keyframes brumeFadeOut {
        0% { opacity: 1; filter: blur(0px); visibility: visible; }
        70% { opacity: 1; filter: blur(3px); visibility: visible; }
        100% { opacity: 0; filter: blur(15px); visibility: hidden; pointer-events: none; }
    }

    .intro-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background-color: #000000;
        color: #ffffff;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 999999;
        animation: brumeFadeOut 2.0s cubic-bezier(0.4, 0, 0.2, 1) forwards;
        font-family: monospace;
        letter-spacing: 8px;
        font-size: 3em;
        font-weight: bold;
    }
    
    .intro-sub {
        font-size: 0.35em;
        letter-spacing: 4px;
        color: #888888;
        margin-top: 10px;
    }
    </style>

    <div class="intro-overlay">
        AEGIS-CORE
        <div class="intro-sub">// PROTOCOLE BETA INITIALISE //</div>
    </div>
""", unsafe_allow_html=True)

# --- MATRICE PROMPTS (20 THÈMES X 20 PROPOSITIONS) ---
MATRICE_PROMPTS = {
    "Pédagogie, Quiz & Résumés": [
        "Génère un Quiz interactif de 5 questions à choix multiples basé sur notre dernière discussion.",
        "Rédige une fiche de synthèse pédagogique claire et structurée du projet en cours.",
        "Conçois un plan de formation étape par étape pour maîtriser ce sujet de A à Z.",
        "Génère une fiche de révision rapide sous forme de carte mentale textuelle.",
        "Explique ce concept avec une analogie simple issue du monde réel.",
        "Crée un exercice pratique guidé avec des indices progressifs.",
        "Fais un résumé exécutif en 3 points clés percutants.",
        "Identifie les 3 erreurs les plus fréquentes sur ce sujet et comment les éviter.",
        "Prépare une liste de questions/réponses (FAQ) orientée mise en pratique.",
        "Structure un plan de cours complet pour un séminaire de formation de 2 heures.",
        "Formule un résumé sous forme de bullet points ultra-synthétiques.",
        "Rédige un mémento technique pour mémoriser les notions indispensables.",
        "Crée un cas pratique orienté mise en situation professionnelle.",
        "Propose un arbre de décision textuel pour résoudre un problème type.",
        "Rédige une introduction captivante pour un exposé sur ce sujet.",
        "Établis une chronologie historique des évolutions majeures de ce domaine.",
        "Conçois un glossaire des 10 termes techniques incontournables.",
        "Rédige une conclusion percutante résumant les enjeux futurs.",
        "Prépare un auto-test d'évaluation des acquis avec corrigé détaillé.",
        "Synthétise les avis divergents et les controverses autour de ce sujet."
    ],
    "Développement & Code": [
        "Donne-moi une structure propre et modulaire pour un projet Python professionnel.",
        "Optimise un algorithme Python pour réduire la complexité temporelle.",
        "Conçois une architecture REST API scalable avec FastAPI.",
        "Écris les tests unitaires complets (pytest) pour ce module.",
        "Réalise une revue de code rigoureuse en signalant les failles de sécurité potentielles.",
        "Génère un script d'automatisation robuste avec gestion des exceptions et logs.",
        "Propose une modélisation de base de données relationnelle optimisée.",
        "Conçois un pipeline de traitement de données asynchrone performant.",
        "Rédige la documentation technique complète au format Markdown.",
        "Implémente un système de cache intelligent pour alléger les requêtes.",
        "Convertis ce bloc de code en une classe orientée objet propre.",
        "Rédige un Dockerfile et un docker-compose optimisés pour cette application.",
        "Écris une fonction de validation de données entrantes avec Pydantic.",
        "Mets en place un système de journalisation (logging) avancé.",
        "Propose une stratégie de gestion des variables d'environnement sécurisée.",
        "Rédige un script de migration de base de données propre.",
        "Développe un middleware d'authentification par JWT sécurisé.",
        "Optimise les requêtes SQL pour éviter les goulots d'étranglement.",
        "Crée un composant d'interface réutilisable et propre.",
        "Rédige un guide de déploiement pas à pas sur serveur Linux."
    ],
    "Cybersécurité & Protocoles": [
        "Rédige une politique de sécurité des systèmes d'information.",
        "Explique la mise en place d'une architecture Zero Trust.",
        "Réalise une analyse de risques selon la méthodologie EBIOS / ISO 27005.",
        "Établis un plan de réponse à incident (Incident Response Plan) détaillé.",
        "Vérifie la conformité des configurations réseau face aux standards actuels.",
        "Simule une phase de modélisation des menaces (Threat Modeling) STRIDE.",
        "Rédige les directives de durcissement (Hardening) pour les serveurs Linux.",
        "Mets en place une stratégie de gestion des correctifs (Patch Management).",
        "Audite ce script pour détecter d'éventuelles vulnérabilités d'injection ou fuites de données.",
        "Conçois une procédure d'authentification forte multi-facteurs (MFA).",
        "Rédige une charte d'utilisation des ressources informatiques.",
        "Établis un protocole de gestion des mots de passe et coffres-forts numériques.",
        "Analyse les vecteurs d'attaque potentiels d'une application web.",
        "Rédige une procédure de sauvegarde et de reprise d'activité (PRA/PCA).",
        "Mets en place un système de détection d'intrusion basique (IDS/IPS).",
        "Explique les mécanismes de chiffrement de bout en bout (E2EE).",
        "Conçois un plan de sensibilisation du personnel contre le phishing.",
        "Rédige un rapport d'incident type suite à une compromission.",
        "Audite la gestion des rôles et des privilèges (IAM).",
        "Établis une grille d'évaluation des vulnérabilités (CVSS)."
    ],
    "Ingénierie des IA & Prompts": [
        "Conçois un System Prompt robuste pour garantir le respect strict des consignes.",
        "Propose une architecture RAG avec Vector DB.",
        "Optimise ce prompt pour réduire les hallucinations du LLM.",
        "Mets en place une stratégie de Fine-Tuning efficace sur domaine spécifique.",
        "Conçois un système d'agents autonomes collaboratifs pour cette tâche.",
        "Établis un benchmark comparatif des performances de différents modèles.",
        "Rédige un mécanisme de chaînage de prompts (Prompt Chaining) complexe.",
        "Implémente une couche de garde-fous (Guardrails) pour filtrer les sorties toxiques.",
        "Optimise la gestion de la fenêtre de contexte pour un traitement longue durée.",
        "Crée un système de rétroaction (Feedback Loop) automatisé pour améliorer les réponses.",
        "Conçois un prompt orienté Few-Shot Learning ultra-précis.",
        "Rédige une structure d'extraction de données structurées (JSON mode).",
        "Mets en place une stratégie de découpage (Chunking) pour base documentaire.",
        "Optimise le ratio coût/performance des appels API LLM.",
        "Conçois un système de validation de la pertinence des réponses (Self-Correction).",
        "Rédige des instructions pour contraindre le style rédactionnel de l'IA.",
        "Implémente un cache de requêtes sémantiques pour réduire les latences.",
        "Conçois un assistant spécialisé en classification de tickets support.",
        "Rédige une stratégie d'évaluation automatisée des LLM (LLM-as-a-judge).",
        "Optimise l'utilisation des tokens pour un agent conversationnel."
    ],
    "Architecture Logicielle & Cloud": [
        "Conçois une architecture microservices hautement disponible.",
        "Propose une stratégie de migration d'un monolithe vers le Cloud.",
        "Rédige un plan de scalabilité horizontale et verticale.",
        "Mets en place un système de répartition de charge (Load Balancing).",
        "Conçois un pipeline CI/CD robuste avec GitHub Actions.",
        "Établis une stratégie de supervision et d'alerting (Monitoring/Logging).",
        "Rédige les spécifications d'un event-driven architecture avec Kafka.",
        "Optimise les coûts d'infrastructure Cloud (FinOps).",
        "Mets en place une stratégie de conteneurisation avancée avec Kubernetes.",
        "Conçois un système de stockage distribué résilient.",
        "Rédige une politique de gestion des pannes (Fault Tolerance).",
        "Propose une architecture serverless pour réduire la maintenance.",
        "Établis un plan de reprise après sinistre multi-région.",
        "Conçois un système d'API Gateway sécurisé et rate-limité.",
        "Rédige les bonnes pratiques de versioning d'API.",
        "Optimise la latence réseau globale d'une application distribuée.",
        "Mets en place une stratégie de déploiement Blue/Green ou Canary.",
        "Conçois un registre de services et de découverte dynamique.",
        "Rédige un cahier des charges d'architecture technique (DAT).",
        "Audite une architecture existante pour détecter les points de blocage."
    ],
    "Management & Gestion de Projet": [
        "Rédige une note de cadrage de projet structurée (Project Charter).",
        "Établis un diagramme de Gantt textuel des jalons clés.",
        "Conçois un plan de gestion des risques du projet.",
        "Rédige les user stories selon la méthodologie Agile (Scrum/Kanban).",
        "Prépare un ordre du jour type pour une réunion de pilotage efficace.",
        "Établis une matrice RACI pour clarifier les rôles et responsabilités.",
        "Rédige un compte-rendu de réunion synthétique et orienté actions.",
        "Conçois un plan de communication interne et externe.",
        "Mets en place des indicateurs de performance (KPIs) de suivi de projet.",
        "Rédige un cahier des charges fonctionnel (CDCF).",
        "Établis une stratégie de gestion du changement (Change Management).",
        "Conçois un processus de recette et de validation client (UAT).",
        "Rédige une estimation budgétaire prévisionnelle détaillée.",
        "Prépare un plan de gestion des parties prenantes.",
        "Établis un processus de résolution des conflits d'équipe.",
        "Rédige un bilan de fin de projet (Post-Mortem / Retrospective).",
        "Conçois un tableau de bord de suivi des livrables.",
        "Rédige une procédure de gestion des demandes de modification (Change Request).",
        "Établis un plan d'allocation des ressources humaines.",
        "Conçois un cadre de gouvernance de projet."
    ],
    "Marketing, SEO & Rédaction Web": [
        "Rédige une stratégie éditoriale complète pour un blog tech.",
        "Optimise ce texte pour le référencement naturel (SEO) avec balises adaptées.",
        "Conçois une campagne d'e-mailing percutante (Cold Outreach).",
        "Rédige une page de vente persuasive selon la méthode AIDA.",
        "Génère 10 idées de publications engageantes pour les réseaux sociaux.",
        "Rédige une balise Title et une Meta Description optimisées.",
        "Conçois un plan de stratégie de contenu (Content Marketing) sur 3 mois.",
