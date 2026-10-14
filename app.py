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

# --- BANQUE DE PROMPTS COMPLÈTE (10 THÈMES X 20 PROMPTS) ---
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
        "Identifie la cause racine d'une panne système récurrente.",
        "Audite la sécurité d'une infrastructure Cloud AWS/GCP.",
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
    "🎓 Pédagogie & Recherche Scientifique": [
        "Explique le fonctionnement des réseaux de neurones Transformers simplement.",
        "Rédige une synthèse de la théorie de la relativité générale.",
        "Propose un plan de cours complet de 10 semaines sur la physique quantique.",
        "Synthétise les dernières avancées sur le stockage d'énergie par batteries solide.",
        "Explique la différence entre l'informatique classique et quantique.",
        "Dresse un panorama des méthodologies de recherche en sciences cognitives.",
        "Explique les mécanismes de l'édition génique via CRISPR-Cas9.",
        "Rédige une fiche de révision claire sur le second principe de la thermodynamique.",
        "Synthétise l'histoire de la conquête spatiale et ses grandes étapes.",
        "Explique le paradoxe de Fermi et les hypothèses associées.",
        "Conçois un guide pédagogique pour apprendre l'algèbre linéaire pas à pas.",
        "Synthétise l'impact du changement climatique sur les courants océaniques.",
        "Explique les fondements mathématiques de l'algorithme PageRank.",
        "Dresse un état de l'art sur la fusion nucléaire contrôlée (ITER).",
        "Rédige un résumé didactique sur les neurotransmetteurs et la mémoire.",
        "Explique la théorie des jeux et le concept d'Équilibre de Nash.",
        "Rédige un projet de recherche sur la bio-inspiration en ingénierie.",
        "Explique la cryptographie asymétrique RSA avec un exemple concret.",
        "Synthétise l'évolution de la théorie de l'évolution depuis Darwin.",
        "Conçois un questionnaire de validation des connaissances scientifiques."
    ],
    "🎨 Création de Contenu & Design": [
        "Rédige un script de vidéo court (Reels/TikTok) captivant dès les 3 premières secondes.",
        "Conçois la charte éditoriale complète d'une marque de technologie.",
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
        "Rédige une politique de sécurité des systèmes d'information (PSSI).",
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
    "📊 Data Science & Intelligence Financière": [
        "Propose un modèle de prédiction du Churn basé sur le Machine Learning.",
        "Explique le fonctionnement de l'analyse en composantes principales (ACP).",
        "Conçois un pipeline ETL propre en Python avec Pandas et SQLAlchemy.",
        "Rédige une analyse financière détaillée d'un bilan d'entreprise.",
        "Propose un modèle d'évaluation d'options financières (Black-Scholes).",
        "Explique la construction d'un portefeuille d'investissement diversifié.",
