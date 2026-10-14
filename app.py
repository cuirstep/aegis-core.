import streamlit as st
import os
import time
import base64
from groq import Groq
import google.generativeai as genai

st.set_page_config(
    page_title="AEGIS-CORE // BETA", 
    page_icon="assets/aegis_logo.png" if os.path.exists("assets/aegis_logo.png") else "🛡️", 
    layout="wide"
)

# --- GESTION DE L'ANIMATION BÊTA EN SESSION ---
if "intro_affichee" not in st.session_state:
    st.session_state["intro_affichee"] = False

# --- INJECTION CSS & ANIMATION ÉPHÉMÈRE ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# Lancer l'animation uniquement la première fois
if not st.session_state["intro_affichee"]:
    st.markdown("""
        <style>
        @keyframes brumeIntro {
            0% { opacity: 0; filter: blur(20px); transform: scale(1.1); }
            50% { opacity: 1; filter: blur(2px); transform: scale(1); }
            100% { opacity: 0; filter: blur(10px); transform: scale(0.95); }
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
            animation: brumeIntro 2.8s ease-in-out forwards;
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
            <div class="intro-sub">// PROTOCOLE BÊTA INITIALISÉ //</div>
        </div>
        
        <audio autoplay style="display:none;">
            <source src="https://www.myinstants.com/media/sounds/metal-gear-solid-alert-sound.mp3" type="audio/mpeg">
        </audio>
    """, unsafe_allow_html=True)
    
    time.sleep(2.8)
    st.session_state["intro_affichee"] = True
    st.rerun()

# --- FONCTIONS UTILITAIRES ---
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

# --- MATRICE INTÉGRALE : 20 THÈMES X 20 PROMPTS ---
MATRICE_PROMPTS = {
    "🎓 Pédagogie, Quiz & Résumés": [
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
        "Dresse une comparaison Avant/Apres pour illustrer le concept.",
        "Redige une FAQ de 5 questions frequemment posees sur ce theme.",
        "Cree un schema textuel expliquant le flux de travail étape par étape.",
        "Redige un aide-memoire au format Markdown.",
        "Propose 3 metaphores simples pour expliquer cette notion complexe.",
        "Cree un plan de revision etale sur 7 jours.",
        "Synthetise les points d'attention cruciaux a retenir absolument.",
        "Redige une grille d'auto-evaluation des competences sur ce sujet."
    ],
    "🛡️ Stratégie & Géopolitique": [
        "Analyse les equilibres geopolitiques actuels avec une precision tactique.",
        "Evalue les risques strategiques d'un conflit technologique global.",
        "Dresse une cartographie des dependances en matieres premieres critiques.",
        "Simule une reponse strategique face a une cyberattaque etatique.",
        "Analyse l'impact de la souverainete numerique sur l'economie europeenne.",
        "Redige une note de synthese sur la doctrine de defense spatiale.",
        "Examine les implications de la militarisation de l'IA.",
        "Analyse l'evolution des doctrines de dissuasion moderne.",
        "Dresse un bilan des vulnerabilites des infrastructures critiques navales.",
        "Evalue les strategies de resilience de la chaine d'approvisionnement globale.",
        "Analyse les enjeux strategiques des cables sous-marins de telecommunication.",
        "Propose un plan d'action pour securiser les donnees sensibles d'un Etat.",
        "Redige un scenario de gestion de crise face a une panne electrique majeure.",
        "Analyse les strategies de souverainete alimentaire d'une nation insulaire.",
        "Evalue l'impact des monnaies numeriques de banque centrale sur le commerce international.",
        "Propose une grille d'analyse des alliances geopolitiques emergentes.",
        "Redige un rapport d'evaluation des menaces hybrides et disinformation.",
        "Analyse la geopolitique des semi-conducteurs en Asie-Pacifique.",
        "Examine le role de l'intelligence artificielle dans la surveillance des frontieres.",
        "Redige une doctrine de reponse rapide pour un poste de commandement."
    ],
    "💻 Développement & Code": [
        "Donne-moi une structure propre et modulaire pour un projet Python professionnel.",
        "Optimise un algorithme Python pour reduire la complexite temporelle.",
        "Concois une architecture REST API scalable avec FastAPI.",
        "Propose un schema de base de donnees PostgreSQL pour un systeme multi-tenant.",
        "Redige un script de CI/CD complet avec GitHub Actions.",
        "Analyse et refactore ce bloc de code pour ameliorer la lisibilite.",
        "Concois un microservice en Go haute performance.",
        "Redige des tests unitaires complets avec Pytest pour un module critique.",
        "Propose une architecture microservices basee sur des evenements (Kafka).",
        "Redige un script Dockerfile optimise et multi-stage build.",
        "Explique et implemente le pattern Singleton et Factory en Python.",
        "Concois une strategie de gestion des erreurs et logging centralise.",
        "Cree une classe Python abstraite pour gerer divers moteurs de base de donnees.",
        "Optimise une requete SQL complexe avec des index appropries.",
        "Redige un script Web Scraping robuste avec gestion des proxies et retries.",
        "Implemente un systeme de cache Redis pour accelerer les requetes d'API.",
        "Explique les meilleures pratiques de securite pour prevenir l'injection SQL et XSS.",
        "Redige une documentation Swagger/OpenAPI claire pour un service Web.",
        "Analyse les goulots d'etranglement de memoire dans une application Python.",
        "Propose une migration propre d'un monolithe vers une architecture serverless."
    ],
    "🚀 Entrepreneuriat & SaaS": [
        "Propose une idee de micro-SaaS B2B a fort potentiel avec un budget reduit.",
        "Dresse un plan d'acquisition client cible pour un outil SaaS de niche.",
        "Redige le Pitch Deck complet de 10 slides pour presenter un projet IA.",
        "Calcule et structure les metriques cles (LTV, CAC, MRR, Churn) d'un SaaS.",
        "Propose une strategie de pricing optimale.",
        "Redige le script d'une video explicative de 60 secondes pour un produit Tech.",
        "Analyse la concurrence et identifie un ocean bleu dans le secteur de la EdTech.",
        "Propose un plan de lancement Product Hunt étape par étape.",
        "Redige la sequence d'emails de bienvenue automatisee.",
        "Structure un cahier des charges MVP pour une application mobile.",
        "Analyse les canaux d'acquisition les plus rentables pour une marketplace B2C.",
        "Redige la landing page ideale.",
        "Concois une strategie de Growth Hacking.",
        "Identifie les risques juridiques cles lors de la creation d'une startup tech.",
        "Redige une proposition commerciale irresistible.",
        "Propose une grille d'evaluation pour recruter les 5 premiers employes cles.",
        "Concois un plan de gestion des retours clients pour reduire le Churn.",
        "Definis les jalons operationnels des 6 premiers mois d'un projet tech.",
        "Redige un modele d'Executive Summary clair.",
        "Structure un plan d'expansion internationale pour un service SaaS."
    ],
    "🧠 Analyse & Diagnostic Technique": [
        "Identifie la cause racine d'une panne systeme recurrente.",
        "Audite la securite d'une infrastructure Cloud AWS/GCP.",
        "Analyse la consommation memoire d'une application conteneurisee.",
        "Propose une metodologie de benchmark d'un modele de LLM.",
        "Dresse une grille d'analyse comparative entre architectures Monolithe et Serverless.",
        "Diagnostique des fuites de memoire dans un code C++/Python.",
        "Evalue les performances reseau d'une architecture distribuee.",
        "Analyse les journaux d'erreurs pour detecter une anomalie.",
        "Diagnostique les ralentissements d'un cluster Kubernetes.",
        "Audite le niveau de conformite RGPD."
    ],
    "🎨 Création de Contenu & Design": [
        "Redige un script de video court captivant des les 3 premieres secondes.",
        "Concois la charte editoriale complete d'une marque de technologie.",
        "Propose un guide UI/UX pour creer un tableau de bord lisible.",
        "Redige une serie de 5 posts LinkedIn viraux sur l'avenir du travail.",
        "Concois la structure d'une newsletter hebdomadaire specialisee dans la Tech."
    ],
    "🔒 Cybersécurité & Protocoles": [
        "Redige une politique de securite des systemes d'information.",
        "Explique la mise en place d'une architecture Zero Trust.",
        "Concois un protocole de reponse rapide a une attaque Ransomware.",
        "Audite la robustesse d'un systeme d'authentification MFA.",
        "Explique les etapes d'un test d'intrusion sur une application Web."
    ],
    "📊 Data Science & Finance": [
        "Propose un modele de prediction du Churn base sur le Machine Learning.",
        "Explique le fonctionnement de l'analyse en composantes principales.",
        "Concois un pipeline ETL propre en Python avec Pandas et SQLAlchemy.",
        "Redige une analyse financière detaillee d'un bilan d'entreprise.",
        "Propose un modele d'evaluation d'options financières."
    ],
    "🤖 Ingénierie des IA & Prompts":
