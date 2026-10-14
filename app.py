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

# --- INJECTION CSS (MASQUAGE TOTAL DES AVATARS USER & ASSISTANT) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Masquer l'avatar de l'utilisateur ET de l'assistant */
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

# --- BANQUE COMPLÈTE : 10 THÈMES X 20 PROMPTS (200 PROMPTS AU TOTAL) ---
MATRICE_PROMPTS = {
    "🎓 Pédagogie, Quiz & Résumés": [
        "Génère un Quiz interactif de 5 questions à choix multiples basé sur notre dernière discussion.",
        "Rédige une fiche de synthèse pédagogique claire et structurée du projet en cours.",
        "Conçois un plan de formation étape par étape pour maîtriser ce sujet de A à Z.",
        "Génère une fiche de révision rapide sous forme de carte mentale textuelle.",
        "Explique ce concept comme si j'avais 10 ans.",
        "Rédige un résumé exécutif en 5 points clés.",
        "Crée une étude de cas pratique basée sur notre échange.",
        "Conçois un questionnaire Vrai/Faux avec explications détaillées.",
        "Synthétise les erreurs courantes à éviter sur ce sujet.",
        "Rédige un lexique des 10 termes fondamentaux à connaître.",
        "Propose un exercice d'application directe avec son corrigé.",
        "Crée un guide de démarrage rapide (Quickstart) synthétique.",
        "Dresse une comparaison Avant/Après pour illustrer le concept.",
        "Rédige une FAQ de 5 questions fréquemment posées sur ce thème.",
        "Crée un schéma textuel expliquant le flux de travail étape par étape.",
        "Rédige un aide-mémoire (Cheat Sheet) au format Markdown.",
        "Propose 3 métaphores simples pour expliquer cette notion complexe.",
        "Crée un plan de révision étalé sur 7 jours.",
        "Synthétise les points d'attention cruciaux à retenir absolument.",
        "Rédige une grille d'auto-évaluation des compétences sur ce sujet."
    ],
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
        "Rédige une synthèse sur l'utilisation du Reinforcement Learning en finance."
    ],
    "🤖 Ingénierie des IA & Prompts": [
        "Conçois un System Prompt robuste pour garantir le respect strict des consignes.",
        "Explique la technique du Few-Shot Prompting pour améliorer la précision des LLM.",
        "Propose une architecture RAG (Retrieval-Augmented Generation) avec Vector DB.",
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
        "Rédige un prompt d'auto-correction permettant à l'IA d'auditer sa propre réponse.",
        "Propose une architecture de mémoire à long terme pour agents conversationnels.",
        "Explique le concept d'IA explicable (XAI) et d'interprétabilité des modèles.",
        "Rédige un benchmark des performances relatives des modèles Open-Source vs Propriétaires."
    ],
    "🕹️ GameDev & Moteurs Virtuels": [
        "Rédige le cahier des charges de Game Design (GDD) pour un jeu d'action tactique.",
        "Explique la gestion de la physique et des collisions sous Unreal Engine 5.",
        "Propose un script C# modulaire pour la gestion des déplacements du joueur sous Unity.",
        "Conçois un système d'inventaire flexible et sauvegardable sous Unity.",
        "Explique le système de Nanite et Lumen sous Unreal Engine 5.",
        "Rédige la structure d'une machine à états finis (FSM) pour l'IA ennemie.",
        "Propose une méthode d'optimisation de rendu pour maintenir 60 FPS constants.",
        "Conçois un arbre de compétences (Skill Tree) interconnecté pour un RPG.",
        "Explique la génération procédurale de terrains à l'aide de bruits de Perlin.",
        "Rédige un shader de matériau d'eau réaliste (Shader Graph / HLSL).",
        "Conçois un système de dialogue interactif à choix multiples.",
        "Explique l'intégration du multijoueur synchrone (Photon/Netcode for GameObjects).",
        "Rédige un plan d'équilibrage des armes et dégâts pour un jeu de tir.",
        "Propose un système de quêtes dynamique avec suivi d'objectifs.",
        "Explique le Sound Design réactif et l'intégration d'FMOD/Wwise.",
        "Conçois une boucle de gameplay (Core Gameplay Loop) engageante.",
        "Rédige un guide d'intégration d'animations avec Animator / Control Rig.",
        "Explique la gestion de l'éclairage dynamique vs Baking de Lightmaps.",
        "Propose une méthodologie de Level Design pour guider naturellement le joueur.",
        "Rédige un plan de portage d'un projet de PC vers consoles/mobile."
    ]
}

# --- MULTI-SESSIONS ---
if "sessions" not in st.session_state:
    st.session_state["sessions"] = {"Discussion 1": []}
if "session_active" not in st.session_state:
    st.session_state["session_active"] = "Discussion 1"

# --- SIDEBAR ÉPURÉE ---
quick_action = None

with st.sidebar:
    if os.path.exists("Gemini_Generated_Image_tuss9ltuss9ltuss.png"):
        st.image("Gemini_Generated_Image_tuss9ltuss9ltuss.png", use_container_width=True)
    
    st.markdown("### 💬 MULTI-SESSIONS")
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
    # HORLOGE TEMPS RÉEL (SYNCHRONISÉE)
    st.markdown("### 🌐 HORLOGE & TEMPS RÉEL")
    heure_actuelle = datetime.now().strftime("%H:%M:%S")
    st.markdown(f"⏰ **{heure_actuelle}** (Heure locale)")

    st.markdown("---")
    st.markdown("### 🛡️ AEGIS-CORE // MATRICE (200 PROMPTS)")
    theme_choisi = st.selectbox("Sélectionnez le domaine :", list(MATRICE_PROMPTS.keys()))
    prompt_selectionne = st.selectbox("Choisissez une commande :", MATRICE_PROMPTS[theme_choisi])
    
    if st.button("🚀 Injecter le prompt"):
        quick_action = prompt_selectionne

# --- SYSTEM PROMPT SIMPLE & EFFECTIF ---
SYSTEM_PROMPT = (
    "Tu es AEGIS-CORE, un système d'IA souverain développé par le Commandant. "
    "Tu es ultra-performant, direct et rigoureux. "
    "Si tu émets une hypothèse ou une déduction, étiquette-la OBLIGATOIREMENT par '[⚠️ HYPOTHÈSE / DÉDUCTION]'."
)

# --- INTERFACE PRINCIPALE ---
col_logo, col_title = st.columns([0.08, 0.92])
with col_logo:
    if os.path.exists("Gemini_Generated_Image_tuss9ltuss9ltuss.png"):
        st.image("Gemini_Generated_Image_tuss9ltuss9ltuss.png", width=45)
    else:
        st.markdown("🛡️")
with col_title:
    st.markdown(f"### AEGIS-CORE // {st.session_state['session_active'].upper()}")
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
        with st.expander("✏️ Modifier votre dernière directive envoyée"):
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

        messages_actuels.append({"role": "assistant", "content": reponse_finale})
