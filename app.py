import streamlit as st
import os
import time
import requests
from datetime import datetime
from groq import Groq
import google.generativeai as genai

st.set_page_config(
    page_title="AEGIS-CORE // OS", 
    page_icon="🛡️", 
    layout="wide"
)

# --- INJECTION CSS ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp { background-color: #0e1117; color: #ffffff; }
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

# --- MATRICE INTÉGRALE : 20 SUJETS X 20 PROMPTS ---
MATRICE_PROMPTS = {
    "🎓 Pédagogie, Quiz & Résumés": [
        "Genere un Quiz interactif de 5 questions a choix multiples base sur notre derniere discussion.",
        "Redige une fiche de synthese pedagogique claire et structuree du projet en cours.",
        "Concois un plan de formation etape par etape pour maitriser ce sujet de A à Z.",
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
        "Cree un schema textuel expliquant le flux de travail etape par etape.",
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
        "Analyse les enjeux strategiques des câbles sous-marins de telecommunication.",
        "Propose un plan d'action pour securiser les donnees sensibles d'un Etat.",
        "Redige un scenario de gestion de crise face a une panne electrique majeure.",
        "Analyse les strategies de souverainete alimentaire d'une nation insulaire.",
        "Evalue l'impact des monnaies numeriques de banque centrale sur le commerce international.",
        "Propose une grille d'analyse des alliances geopolitiques emergentes.",
        "Redige un rapport d'evaluation des menaces hybrides et desinformation.",
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
        "Propose une architecture microservices basee sur des evenements Kafka.",
        "Redige un script Dockerfile optimise et multi-stage build.",
        "Explique et implemente le pattern Singleton et Factory en Python.",
        "Concois une strategie de gestion des erreurs et logging centralise.",
        "Cree une classe Python abstraite pour gerer divers moteurs de base de donnees.",
        "Optimise une requete SQL complexe avec des index appropries.",
        "Redige un script Web Scraping robuste avec gestion des proxies et retries.",
        "Implemente un systeme de cache Redis pour accelerer les requêtes d'API.",
        "Explique les meilleures pratiques de securite pour prevenir l'injection SQL et XSS.",
        "Redige une documentation Swagger/OpenAPI claire pour un service Web.",
        "Analyse les goulots d'etranglement de memoire dans une application Python.",
        "Propose une migration propre d'un monolithe vers une architecture serverless."
    ],
    "🚀 Entrepreneuriat & SaaS": [
        "Propose une idee de micro-SaaS B2B a fort potentiel avec un budget reduit.",
        "Dresse un plan d'acquisition client cible pour un outil SaaS de niche.",
        "Redige le Pitch Deck complet de 10 slides pour presenter un projet IA.",
        "Calcule et structure les metriques cles LTV, CAC, MRR, Churn d'un SaaS.",
        "Propose une strategie de pricing optimale.",
        "Redige le script d'une video explicative de 60 secondes pour un produit Tech.",
        "Analyse la concurrence et identifie un ocean bleu dans le secteur de la EdTech.",
        "Propose un plan de lancement Product Hunt etape par etape.",
        "Redige la sequence d'emails de bienvenue automatisee pour convertir les utilisateurs gratuits.",
        "Structure un cahier des charges MVP pour une application mobile.",
        "Analyse les canaux d'acquisition les plus rentables pour une marketplace B2C.",
        "Redige la landing page ideale titre, sous-titres, CTA, preuve sociale.",
        "Concois une strategie de Growth Hacking basee sur le programme de parrainage.",
        "Identifie les risques juridiques cles lors de la creation d'une startup tech.",
        "Redige une proposition commerciale irresistible pour un contrat d'entreprise.",
        "Propose une grille d'evaluation pour recruter les 5 premiers employes cles.",
        "Concois un plan de gestion des retours clients pour reduire le Churn.",
        "Definis les jalons operationnels des 6 premiers mois d'un projet tech.",
        "Redige un modele d'Executive Summary clair pour des partenaires financiers.",
        "Structure un plan d'expansion internationale pour un service SaaS."
    ],
    "🧠 Analyse & Diagnostic Technique": [
        "Identifie la cause racine d'une panne systeme recurrente.",
        "Audite la securite d'une infrastructure Cloud AWS/GCP.",
        "Analyse la consommation memoire d'une application conteneurisee.",
        "Propose une methodologie de benchmark d'un modele de LLM.",
        "Dresse une grille d'analyse comparative entre architectures Monolithe et Serverless.",
        "Diagnostique des fuites de memoire dans un code C++/Python.",
        "Evalue les performances réseau d'une architecture distribuee.",
        "Analyse les journaux d'erreurs pour detecter une anomalie silencieuse.",
        "Diagnostique les ralentissements d'un cluster Kubernetes.",
        "Audite le niveau de conformite RGPD d'un systeme de collecte de donnees.",
        "Diagnostique l'impact d'une latence d'API sur l'experience utilisateur.",
        "Propose un plan de reprise d'activite apres un crash serveur.",
        "Audite l'exposition des secrets/cles API dans les depots de code.",
        "Diagnostique un probleme de concurrence Deadlock dans un systeme multi-thread.",
        "Evalue l'efficacite du systeme de sauvegarde des donnees.",
        "Propose un protocole de test de charge Stress Testing avec Locust.",
        "Analyse les faiblesses d'un protocole d'authentification OAuth2/JWT.",
        "Diagnostique les failles de configuration d'un serveur Web Nginx.",
        "Evalue le coût global de possession d'une migration Cloud.",
        "Redige un rapport de post-mortem d'incident technique."
    ],
    "🎨 Création de Contenu & Design": [
        "Redige un script de video court captivant des les 3 premieres secondes.",
        "Concois la charte editoriale complete d'une marque de technologie.",
        "Propose un guide UI/UX pour creer un tableau de bord lisible et sombre.",
        "Redige une serie de 5 posts LinkedIn viraux sur l'avenir du travail.",
        "Concois la structure d'une newsletter hebdomadaire specialisee dans la Tech.",
        "Propose un concept de packaging innovant et eco-responsable.",
        "Redige le manifeste d'une marque dediee a la souverainete numerique.",
        "Structure un guide de style UI pour la typographie et les couleurs.",
        "Redige 10 accroches publicitaires percutantes pour un produit premium.",
        "Propose un wireframe textuel complet pour l'ecran d'accueil d'une app.",
        "Redige un article de blog SEO de 1500 mots sur la cybersecurite.",
        "Concois un plan de communication d'urgence en cas de bad buzz.",
        "Propose une identite visuelle complete couleurs, polices, moodboard.",
        "Redige le script d'un episode de podcast de 20 minutes sur l'IA.",
        "Cree une strategie de Storytelling autour de l'histoire du fondateur.",
        "Redige la description optimisee d'un produit pour une boutique e-commerce.",
        "Propose un systeme d'icones et de composants design sous Figma.",
        "Redige une etude de cas client detaillee pour prouver la valeur du produit.",
        "Concois un guide micro-copywriting textes de boutons, tooltips, erreurs.",
        "Propose un calendrier editorial pour 30 jours de publications multi-canaux."
    ],
    "🔒 Cybersécurité & Protocoles": [
        "Redige une politique de securite des systemes d'information PSSI.",
        "Explique la mise en place d'une architecture Zero Trust.",
        "Concois un protocole de reponse rapide a une attaque Ransomware.",
        "Audite la robustesse d'un systeme d'authentification MFA.",
        "Explique les etapes d'un test d'intrusion Pentest sur une application Web.",
        "Redige un guide de bonnes pratiques contre le Phishing pour les employes.",
        "Analyse le protocole TLS 1.3 et ses ameliorations de securite.",
        "Propose une strategie de chiffrement des donnees au repos et en transit.",
        "Explique l'exploitation et la mitigation des failles OWASP Top 10.",
        "Redige un script de detection d'intrusion base sur l'analyse des logs.",
        "Explique le fonctionnement d'un Honeypot et son interêt defensif.",
        "Audite la securite de la gestion des identites et des acces IAM.",
        "Propose un plan de durcissement Hardening pour un systeme Linux.",
        "Explique le role du SIEM dans le centre d'operations de securite SOC.",
        "Redige un guide pour securiser les API REST contre les attaques par deni de service DDoS.",
        "Explique le concept de cryptographie post-quantique et ses enjeux.",
        "Analyse la securite des conteneurs Kubernetes en production.",
        "Propose un protocole de gestion securisee des cles de chiffrement KMS.",
        "Examine les vulnerabilites de securite liees aux appareils IoT.",
        "Redige une procedure d'analyse forensique après une fuite de donnees."
    ],
    "📊 Data Science & Finance
