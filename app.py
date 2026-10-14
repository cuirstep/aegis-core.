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
    "💻 Développement & Code": [
        "Donne-moi une structure propre et modulaire pour un projet Python professionnel.",
        "Optimise un algorithme Python pour reduire la complexite temporelle.",
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
        "Propose une idee de micro-SaaS B2B a fort potentiel avec un budget reduit.",
        "Dresse un plan d'acquisition client cible pour un outil SaaS de niche.",
        "Redige le Pitch Deck complet de 10 slides pour presenter un projet IA.",
        "Calcule et structure les metriques cles (LTV, CAC, MRR, Churn) d'un SaaS.",
        "Propose une strategie de pricing optimale.",
        "Rédige le script d'une vidéo explicative de 60 secondes pour un produit Tech.",
        "Analyse la concurrence et identifie un océan bleu dans le secteur de la EdTech.",
        "Propose un plan de lancement Product Hunt étape par étape.",
        "Rédige la séquence d'emails de bienvenue automatisée pour convertir les utilisateurs gratuits.",
        "Structure un cahier des charges MVP pour une application mobile.",
        "Analyse les canaux d'acquisition les plus rentables pour une marketplace B2C.",
        "Rédige la landing page idéale (titre, sous-titres, CTA, preuve sociale).",
        "Conçois une stratégie de Growth Hacking basée sur le programme de parrainage.",
        "Identifie les risques juridiques clés lors de la création d'une startup tech.",
        "Rédige une proposition commerciale irrésistible pour un contrat d'entreprise.",
        "Propose une grille d'évaluation pour recruter les 5 premiers employés clés.",
        "Conçois un plan de gestion des retours clients pour réduire le Churn.",
        "Définis les jalons opérationnels des 6 premiers mois d'un projet tech.",
        "Rédige un modèle d'Executive Summary clair pour des partenaires financiers.",
        "Structure un plan d'expansion internationale pour un service SaaS."
    ],
    "🧠 Analyse & Diagnostic Technique": [
        "Identifie la cause racine d'une panne systeme recurrente.",
        "Audite la securite d'une infrastructure Cloud AWS/GCP.",
        "Analyse la consommation mémoire d'une application conteneurisée.",
        "Propose une méthodologie de benchmark d'un modèle de LLM.",
        "Dresse une grille d'analyse comparative entre architectures Monolithe et Serverless.",
        "Diagnostique des fuites de mémoire dans un code C++/Python.",
        "Évalue les performances réseau d'une architecture distribuée.",
        "Analyse les journaux d'erreurs (logs) pour détecter une anomalie silencieuse.",
        "Diagnostique les ralentissements d'un cluster Kubernetes.",
        "Audite le niveau de conformité RGPD d'un système de collecte de données.",
        "Diagnostique l'impact d'une latence d'API sur l'expérience utilisateur.",
        "Propose un plan de reprise d'activité (PRA) après un crash serveur.",
        "Audite l'exposition des secrets/clés API dans les dépôts de code.",
        "Diagnostique un problème de concurrence (Deadlock) dans un système multi-thread.",
        "Évalue l'efficacité du système de sauvegarde des données.",
        "Propose un protocole de test de charge (Stress Testing) avec Locust.",
        "Analyse les faiblesses d'un protocole d'authentification OAuth2/JWT.",
        "Diagnostique les failles de configuration d'un serveur Web Nginx.",
        "Évalue le coût global de possession (TCO) d'une migration Cloud.",
        "Rédige un rapport de post-mortem d'incident technique."
    ],
    "🎨 Création de Contenu & Design": [
        "Redige un script de video court captivant des les 3 premieres secondes.",
        "Concois la charte editoriale complete d'une marque de technologie.",
        "Propose un guide UI/UX pour créer un tableau de bord lisible et sombre.",
        "Rédige une série de 5 posts LinkedIn viraux sur l'avenir du travail.",
        "Conçois la structure d'une newsletter hebdomadaire spécialisée dans la Tech.",
        "Propose un concept de packaging innovant et éco-responsable.",
        "Rédige le manifeste d'une marque dédiée à la souveraineté numérique.",
        "Structure un guide de style UI pour la typographie et les couleurs.",
        "Rédige 10 accroches publicitaires percutantes pour un produit premium.",
        "Propose un wireframe textuel complet pour l'écran d'accueil d'une app.",
        "Rédige un article de blog SEO de 1500 mots sur la cybersécurité.",
        "Conçois un plan de communication d'urgence en cas de bad buzz.",
        "Propose une identité visuelle complète (couleurs, polices, moodboard).",
        "Rédige le script d'un épisode de podcast de 20 minutes sur l'IA.",
        "Crée une stratégie de Storytelling autour de l'histoire du fondateur.",
        "Rédige la description optimisée d'un produit pour une boutique e-commerce.",
        "Propose un système d'icônes et de composants design sous Figma.",
        "Rédige une étude de cas client détaillée pour prouver la valeur du produit.",
        "Conçois un guide micro-copywriting (textes de boutons, tooltips, erreurs).",
        "Propose un calendrier éditorial pour 30 jours de publications multi-canaux."
    ],
    "🔒 Cybersécurité & Protocoles": [
        "Redige une politique de securite des systemes d'information (PSSI).",
        "Explique la mise en place d'une architecture Zero Trust.",
        "Conçois un protocole de réponse rapide à une attaque Ransomware.",
        "Audite la robustesse d'un système d'authentification MFA.",
        "Explique les étapes d'un test d'intrusion (Pentest) sur une application Web.",
        "Rédige un guide de bonnes pratiques contre le Phishing pour les employés.",
        "Analyse le protocole TLS 1.3 et ses améliorations de sécurité.",
        "Propose une stratégie de chiffrement des données au repos et en transit.",
        "Explique l'exploitation et la mitigation des failles OWASP Top 10.",
        "Rédige un script de détection d'intrusion basé sur l'analyse des logs.",
        "Explique le fonctionnement d'un Honeypot et son intérêt défensif.",
        "Audite la sécurité de la gestion des identités et des accès (IAM).",
        "Propose un plan de durcissement (Hardening) pour un système Linux.",
        "Explique le rôle du SIEM dans le centre d'opérations de sécurité (SOC).",
        "Rédige un guide pour sécuriser les API REST contre les attaques par déni de service (DDoS).",
        "Explique le concept de cryptographie post-quantique et ses enjeux.",
        "Analyse la sécurité des conteneurs Kubernetes en production.",
        "Propose un protocole de gestion sécurisée des clés de chiffrement (KMS).",
        "Examine les vulnérabilités de sécurité liées aux appareils IoT.",
        "Rédige une procédure d'analyse forensique après une fuite de données."
    ],
    "📊 Data Science & Finance": [
        "Propose un modele de prediction du Churn base sur le Machine Learning.",
        "Concois un pipeline ETL propre en Python avec Pandas et SQLAlchemy.",
        "Rédige une analyse financière détaillée d'un bilan d'entreprise.",
        "Propose un modèle d'évaluation d'options financières (Black-Scholes).",
        "Explique la construction d'un portefeuille d'investissement diversifié.",
        "Conçois un tableau de bord KPI pour le suivi des performances financières.",
        "Explique l'utilisation des réseaux de neurones LSTM pour la prévision de séries temporelles.",
        "Rédige une méthodologie de détection de fraudes dans les transactions bancaires.",
        "Analyse l'impact de l'inflation sur les flux de trésorerie d'une entreprise.",
        "Propose un modèle de Scoring Crédit basé sur la régression logistique.",
        "Explique l'évaluation d'une startup par la méthode DCF (Discounted Cash Flow).",
        "Rédige un script Python d'analyse de sentiments sur des données textuelles.",
        "Propose une architecture Data Lake pour le stockage de Big Data.",
        "Explique le test A/B statistique et le calcul de la taille d'échantillon.",
        "Rédige un rapport sur la gestion des risques de marché et de liquidité.",
        "Propose une méthode de segmentation client (K-Means Clustering).",
        "Explique le fonctionnement des arbres de décision et Random Forest.",
        "Conçois une grille d'analyse comparative de solutions BI (PowerBI, Tableau).",
        "Rédige une synthèse sur l'utilisation du Reinforcement Learning en finance.",
        "Explique l'optimisation de portefeuille par la théorie moderne de Markowitz."
    ],
    "🤖 Ingénierie des IA & Prompts": [
        "Concois un System Prompt robuste pour garantir le respect strict des consignes.",
        "Propose une architecture RAG avec Vector DB.",
        "Explique la technique du Few-Shot Prompting pour améliorer la précision des LLM.",
        "Optimise un prompt pour éliminer complètement les hallucinations de réponses.",
        "Rédige un protocole d'évaluation (Evals) pour comparer deux modèles d'IA.",
        "Explique l'alignement des modèles par RLHF (Reinforcement Learning from Human Feedback).",
        "Conçois un pipeline de Fine-Tuning pour adapter un LLM à un domaine médical.",
        "Propose une technique de Prompt Chaining pour décomposer une tâche complexe.",
        "Explique le rôle de la recherche vectorielle (Cosine Similarity) dans un RAG.",
        "Rédige un guide de garde-fous (Guardrails) pour sécuriser l'agent IA.",
        "Explique l'Agentic Workflow et la collaboration multi-agents (LangChain/CrewAI).",
        "Propose une stratégie de compression de contexte pour gérer les longs documents.",
        "Explique le fonctionnement des mécanismes d'attention dans la structure Transformer.",
        "Rédige une consigne d'analyse sémantique pour extraire des entités nommées (NER).",
        "Propose un protocole de débogage pour les agents IA autonomes.",
        "Explique la différence entre Fine-Tuning, LoRA et RAG pour la personnalisation.",
        "
