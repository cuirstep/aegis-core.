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
        "Rédige un article de blog approfondi de 1000 mots sur ce sujet.",
        "Établis un profil type de client idéal (Buyer Persona).",
        "Rédige une proposition commerciale attractive et sur-mesure.",
        "Conçois une campagne publicitaire ciblée (Google Ads / Meta Ads).",
        "Rédige une newsletter hebdomadaire engageante et rythmée.",
        "Analyse l'angle marketing idéal pour lancer un nouveau produit.",
        "Rédige un communiqué de presse professionnel.",
        "Conçois une stratégie de netlinking et d'acquisition de liens.",
        "Rédige des accroches (hooks) virales pour formats courts (Shorts/Reels).",
        "Établis un plan d'optimisation du taux de conversion (CRO).",
        "Rédige une FAQ marketing pour lever les freins à l'achat.",
        "Conçois un script de présentation produit orienté bénéfices clients.",
        "Rédige une stratégie de fidélisation client."
    ],
    "Stratégie d'Entreprise & Innovation": [
        "Réalise une matrice SWOT détaillée pour ce projet.",
        "Conçois un Business Model Canvas complet et structuré.",
        "Rédige un executive summary percutant pour des investisseurs.",
        "Établis une analyse concurrentielle sectorielle.",
        "Conçois une stratégie d'innovation ouverte (Open Innovation).",
        "Rédige une proposition de valeur unique (UVP).",
        "Établis un plan de diversification des sources de revenus.",
        "Conçois une stratégie d'implantation sur un nouveau marché.",
        "Rédige un plan de développement stratégique à 3 ans.",
        "Établis une analyse PESTEL des facteurs macro-environnementaux.",
        "Conçois un programme intrapreneuriat pour stimuler l'innovation.",
        "Rédige une stratégie de partenariat et d'alliance stratégique.",
        "Établis un plan de réduction des coûts opérationnels.",
        "Conçois un modèle de gouvernance d'entreprise éthique.",
        "Rédige une analyse d'opportunité de fusion-acquisition (M&A).",
        "Établis une stratégie de transformation digitale globale.",
        "Conçois un plan de gestion de crise institutionnelle.",
        "Rédige une politique RSE (Responsabilité Sociétale des Entreprises).",
        "Établis un tableau de bord prospectif (Balanced Scorecard).",
        "Conçois un atelier de design thinking pour l'idéation."
    ],
    "Finances & Comptabilité": [
        "Rédige un compte de résultat prévisionnel simplifié.",
        "Conçois un plan de trésorerie mensuel sur 12 mois.",
        "Explique les indicateurs clés de rentabilité (ROI, EBITDA, VAN, TRI).",
        "Rédige une analyse financière d'un bilan comptable.",
        "Établis un seuil de rentabilité (Point mort) détaillé.",
        "Conçois une politique de contrôle de gestion interne.",
        "Rédige un dossier de demande de financement bancaire.",
        "Établis une stratégie d'optimisation de la structure de capital.",
        "Conçois un tableau d'amortissement d'emprunt.",
        "Rédige une note d'analyse des risques financiers.",
        "Établis un budget prévisionnel par département.",
        "Conçois un processus de validation des notes de frais.",
        "Rédige une politique de gestion du fonds de roulement (BFR).",
        "Établis un rapport d'audit financier préliminaire.",
        "Conçois un modèle d'évaluation de startup (Valo).",
        "Rédige une procédure de facturation et de recouvrement.",
        "Établis un plan d'investissement pluriannuel.",
        "Conçois une stratégie de couverture des risques de change.",
        "Rédige un résumé des obligations fiscales et sociales.",
        "Établis un diagnostic de santé financière d'entreprise."
    ],
    "Ressources Humaines & Management": [
        "Rédige une offre d'emploi attractive et inclusive.",
        "Conçois un parcours d'intégration (Onboarding) structuré.",
        "Établis une grille de compétences et d'évaluation des performances.",
        "Rédige un plan de formation professionnelle continue.",
        "Conçois une stratégie de marque employeur (Employer Branding).",
        "Rédige un règlement intérieur d'entreprise.",
        "Établis un processus de recrutement et d'entretien structuré.",
        "Conçois un plan de prévention des risques psychosociaux (RPS).",
        "Rédige une politique de télétravail et de flexibilité.",
        "Établis un questionnaire de satisfaction et d'engagement collaborateur.",
        "Conçois un système de rémunération variable et d'avantages.",
        "Rédige une procédure de gestion des entretiens annuels.",
        "Établis un plan de gestion des talents et de succession.",
        "Conçois une stratégie de cohésion d'équipe (Team Building).",
        "Rédige un guide de résolution des désaccords sociaux.",
        "Établis un bilan social prévisionnel.",
        "Conçois un programme de mentorat interne.",
        "Rédige une politique de diversité et d'inclusion.",
        "Établis un plan de reconversion ou d'évolution de carrière.",
        "Conçois un cadre de dialogue social constructif."
    ],
    "Droit, Contrats & Conformité": [
        "Rédige un modèle de contrat de prestation de services solide.",
        "Conçois une politique de confidentialité conforme au RGPD.",
        "Rédige des conditions générales de vente (CGV) e-commerce.",
        "Établis une clause de propriété intellectuelle et de cession de droits.",
        "Rédige un accord de non-divulgation (NDA) équilibré.",
        "Conçois une mise en demeure formelle pour impayé.",
        "Rédige une politique de cookies et de traçage web.",
        "Établis un contrat de travail type (CDI/CDD) conforme.",
        "Conçois un accord de partenariat commercial.",
        "Rédige une note de synthèse sur une réglementation spécifique.",
        "Établis une grille de conformité réglementaire (Compliance).",
        "Rédige un contrat de licence de logiciel (EULA).",
        "Conçois une procédure de signalement interne (Whistleblowing).",
        "Rédige une clause de non-concurrence valide.",
        "Établis un protocole d'accord transactionnel.",
        "Rédige un mémorandum juridique sur un point précis.",
        "Conçois une politique de protection des données internes.",
        "Rédige un contrat de sous-traitance informatique.",
        "Établis une analyse d'impact relative à la protection des données (AIPD).",
        "Rédige des conditions générales d'utilisation (CGU) d'application."
    ],
    "Sciences de Données & Data Science": [
        "Conçois un pipeline complet de nettoyage et de préparation de données.",
        "Explique comment choisir entre régression linéaire et forêts aléatoires.",
        "Rédige une méthodologie d'évaluation de modèle de machine learning.",
        "Établis une stratégie de traitement des valeurs manquantes et aberrantes.",
        "Conçois un modèle de classification de séries temporelles.",
        "Rédige un guide d'interprétabilité des modèles (SHAP / LIME).",
        "Établis une architecture de traitement Big Data avec PySpark.",
        "Conçois un système de recommandation basé sur le filtrage collaboratif.",
        "Rédige une stratégie de réduction de dimensionnalité (PCA / t-SNE).",
        "Établis un protocole de test A/B statistique rigoureux.",
        "Conçois un modèle de détection d'anomalies en temps réel.",
        "Rédige les spécifications d'un lac de données (Data Lake).",
        "Établis une gouvernance des données d'entreprise (Data Governance).",
        "Conçois un script d'analyse exploratoire de données (EDA) automatisé.",
        "Rédige une stratégie d'équilibrage des classes déséquilibrées (SMOTE).",
        "Établis un processus de validation croisée robuste.",
        "Conçois un indicateur de performance prédictif métier.",
        "Rédige une documentation de modèle (Model Card).",
        "Établis un plan de suivi des dérives de modèles (Data Drift).",
        "Conçois un système d'ingénierie des caractéristiques (Feature Engineering)."
    ],
    "Design UX/UI & Ergonomie": [
        "Conçois les wireframes textuels d'une application mobile moderne.",
        "Établis un parcours utilisateur (User Journey) détaillé.",
        "Rédige une grille d'évaluation ergonomique d'interface (Heuristiques de Nielsen).",
        "Conçois une architecture de l'information (Navigation) intuitive.",
        "Rédige un cahier des charges de design system.",
        "Établis un protocole de tests utilisateurs qualitatifs.",
        "Conçois une stratégie d'accessibilité numérique (Normes RGAA/WCAG).",
        "Rédige les spécifications des micro-interactions et animations.",
        "Établis un processus de refonte d'interface basé sur les retours utilisateurs.",
        "Conçois un formulaire d'inscription optimisé et sans friction.",
        "Rédige les principes directeurs d'une charte graphique.",
        "Établis une matrice de priorisation des fonctionnalités (MoSCoW).",
        "Conçois un tableau de bord (Dashboard) épuré et lisible.",
        "Rédige des personas utilisateurs complets et réalistes.",
        "Établis une stratégie de design centré utilisateur (DCU).",
        "Conçois une expérience de page d'erreur (404) engageante.",
        "Rédige une structure de navigation par fil d'Ariane.",
        "Établis un benchmark d'ergonomie concurrentielle.",
        "Conçois un système de retours visuels (Feedback States) clair.",
        "Rédige un guide de bonnes pratiques d'écriture UX (UX Writing)."
    ],
    "Création de Contenu & Média": [
        "Conçois le scénario complet d'une vidéo YouTube explicative de 5 minutes.",
        "Rédige un script de podcast immersif avec indications sonores.",
        "Génère une structure de storyboard pour un module e-learning.",
        "Rédige un communiqué narratif de lancement de produit.",
        "Conçois un plan de cours vidéo séquentiel.",
        "Rédige une critique constructive de scénario.",
        "Établis un guide de ton et de voix éditoriale.",
        "Conçois un concept d'émission interactive.",
        "Rédige une biographie professionnelle percutante.",
        "Établis un plan de production de contenu multimédia.",
        "Conçois des questions d'interview percutantes pour un invité.",
        "Rédige un synopsis de court-métrage de science-fiction.",
        "Établis une stratégie de syndication de contenu.",
        "Conçois un format de newsletter audio originale.",
        "Rédige une description de chaîne optimisée pour le référencement.",
        "Établis un calendrier de diffusion multi-plateforme.",
        "Conçois une stratégie de narration immersive (Storytelling).",
        "Rédige un argumentaire de vente en format vidéo courte.",
        "Établis un processus de validation des livrables artistiques.",
        "Conçois un kit de communication pour influenceurs."
    ],
    "Recherche & Analyse Académique": [
        "Rédige une revue de littérature structurée sur ce sujet de recherche.",
        "Conçois une problématique de recherche originale et rigoureuse.",
        "Établis un protocole méthodologique de recherche qualitative.",
        "Rédige un résumé académique (Abstract) normé.",
        "Conçois un plan détaillé de thèse ou de mémoire universitaire.",
        "Établis une grille d'analyse bibliographique critique.",
        "Rédige une note de synthèse méthodologique.",
        "Conçois un cadre théorique conceptuel.",
        "Rédige une discussion critique des résultats d'étude.",
        "Établis un plan de valorisation scientifique (publication/colloque).",
        "Conçois un protocole d'enquête par questionnaire scientifique.",
        "Rédige une analyse épistémologique d'un concept.",
        "Établis une stratégie de collecte de données primaires et secondaires.",
        "Conçois un modèle d'analyse statistique inférentielle.",
        "Rédige une introduction de papier de recherche percutante.",
        "Établis un code éthique de recherche scientifique.",
        "Conçois un plan de gestion des données de recherche (DMP).",
        "Rédige une évaluation critique des biais de recherche.",
        "Établis une cartographie des courants de pensée du domaine.",
        "Conçois un séminaire de restitution de travaux de recherche."
    ],
    "Développement Personnel & Productivité": [
        "Conçois un plan de gestion du temps selon la méthode Pomodoro et Time Blocking.",
        "Établis une routine matinale optimisée pour l'efficacité.",
        "Rédige un bilan de compétences personnel et professionnel.",
        "Conçois un système d'objectifs SMART à court et long terme.",
        "Rédige une stratégie de lutte contre la procrastination.",
        "Établis un plan de développement de l'intelligence émotionnelle.",
        "Conçois un journal de bord de gratitude et de réussite.",
        "Rédige une routine de déconnexion vespérale pour un meilleur sommeil.",
        "Établis un plan d'amélioration de la prise de parole en public.",
        "Conçois un système d'organisation personnelle (GTD - Getting Things Done).",
        "Rédige une stratégie de gestion du stress et de l'anxiété.",
        "Établis un plan de lecture active pour enrichir ses connaissances.",
        "Conçois un exercice de cartographie des valeurs personnelles.",
        "Rédige un plan de négociation salariale argumenté.",
        "Établis une stratégie de renforcement de la confiance en soi.",
        "Conçois un cadre de prise de décision rapide face au doute.",
        "Rédige un journal de bord des erreurs constructives (Post-Mortem personnel).",
        "Établis un plan d'équilibre entre vie professionnelle et personnelle.",
        "Conçois un atelier d'autocoaching hebdomadaire.",
        "Rédige une vision de vie inspirante à 5 ans."
    ],
    "Santé, Bien-être & Nutrition": [
        "Conçois un plan de menus équilibrés de la semaine.",
        "Établis un programme d'entraînement physique adapté à domicile.",
        "Rédige un guide des bonnes pratiques d'hygiène de sommeil.",
        "Conçois une routine d'étirements et de mobilité articulaire.",
        "Rédige une analyse des bienfaits de la cohérence cardiaque.",
        "Établis un plan de suivi de l'hydratation quotidienne.",
        "Conçois un programme de reprise progressive du sport.",
        "Rédige une liste de courses intelligente et saine.",
        "Établis une stratégie de gestion de la fatigue chronique.",
        "Conçois un espace de méditation et de relaxation chez soi.",
        "Rédige un guide de prévention des troubles musculo-squelettiques (TMS).",
        "Établis un programme de marche active quotidienne.",
        "Conçois une routine de respiration anti-stress.",
        "Rédige un bilan des apports nutritionnels essentiels.",
        "Établis un plan d'ergonomie du poste de travail pour la santé.",
        "Conçois un carnet de suivi du bien-être général.",
        "Rédige une sélection d'infusions et de plantes apaisantes.",
        "Établis un programme de renforcement de la sangle abdominale.",
        "Conçois une stratégie de transition vers une alimentation consciente.",
        "Rédige un protocole de récupération post-effort."
    ],
    "Logistique & Supply Chain": [
        "Conçois un modèle d'optimisation de la gestion des stocks (ABC / Wilson).",
        "Établis un plan de transport et de distribution multi-modal.",
        "Rédige une procédure de gestion des retours clients (Reverse Logistics).",
        "Conçois un plan de réduction des délais de livraison (Lead Time).",
        "Établis une stratégie d'atténuation des risques de rupture d'approvisionnement.",
        "Rédige un cahier des charges pour un système WMS (Warehouse Management System).",
        "Conçois un plan d'optimisation de l'espace d'entrepôt (Slotting).",
        "Établis un indicateur de performance de taux de service client (OTIF).",
        "Rédige une procédure de contrôle qualité à la réception des marchandises.",
        "Conçois une stratégie d'achats durables et responsables.",
        "Établis un plan de gestion des stocks de sécurité.",
        "Rédige un contrat-cadre fournisseurs de transport.",
        "Conçois un système de traçabilité des lots de production.",
        "Établis un diagnostic de performance logistique globale.",
        "Rédige un plan de continuité d'activité de la chaîne logistique.",
        "Conçois une stratégie de cross-docking efficace.",
        "Établis un modèle de prévision de la demande (Forecasting).",
        "Rédige une procédure d'inventaire physique tournant.",
        "Conçois un plan de réduction de l'empreinte carbone transport.",
        "Établis un cadre de gouvernance des relations fournisseurs."
    ],
    "Support Client & Expérience (CX)": [
        "Rédige une macro de réponse polie et empathique pour un client mécontent.",
        "Conçois une grille d'évaluation de la qualité du support client.",
        "Établis un processus de gestion des réclamations complexes (Escalade).",
        "Rédige un guide de bonnes pratiques pour le chat en direct.",
        "Conçois un système de calcul du score de satisfaction (CSAT / NPS).",
        "Rédige une base de connaissances claire et intuitive pour les clients.",
        "Établis une stratégie de réduction du temps de première réponse (FRT).",
        "Conçois un programme de fidélisation client axé sur l'expérience.",
        "Rédige une procédure de remboursement et de compensation équitable.",
        "Établis un plan de formation aux techniques de communication bienveillante.",
        "Conçois un parcours client omnicanal fluide.",
        "Rédige un modèle d'enquête de 
