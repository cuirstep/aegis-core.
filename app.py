import streamlit as st
import os
import time
import requests
from datetime import datetime
from groq import Groq
import google.generativeai as genai

st.set_page_config(
    page_title="AEGIS-CORE // BETA", 
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

# --- ANIMATION DE DÉMARRAGE (BOOT SÉQUENCE BÉTA) ---
if "initialized" not in st.session_state:
    with st.spinner("🛡️ [AEGIS-CORE // BOOT SEQUENCE] Initialisation du noyau souverain et de l'essaim d'agents..."):
        time.sleep(1.2)
    st.session_state["initialized"] = True

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
    "Pedagogie, Quiz & Resumes": [
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
    "Strategie & Geopolitique": [
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
    "Developpement & Code": [
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
    "Entrepreneuriat & SaaS": [
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
    "Analyse & Diagnostic Technique": [
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
    "Creation de Contenu & Design": [
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
    "Cybersecurite & Protocoles": [
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
    "Data Science & Finance": [
        "Propose un modele de prediction du Churn base sur le Machine Learning.",
        "Concois un pipeline ETL propre en Python avec Pandas et SQLAlchemy.",
        "Redige une analyse financiere detaillee d'un bilan d'entreprise.",
        "Propose un modele d'evaluation d'options financieres Black-Scholes.",
        "Explique la construction d'un portefeuille d'investissement diversifie.",
        "Concois un tableau de bord KPI pour le suivi des performances financieres.",
        "Explique l'utilisation des reseaux de neurones LSTM pour la prevision de series temporelles.",
        "Redige une methodologie de detection de fraudes dans les transactions bancaires.",
        "Analyse l'impact de l'inflation sur les flux de tresorerie d'une entreprise.",
        "Propose un modele de Scoring Credit base sur la regression logistique.",
        "Explique l'evaluation d'une startup par la methode DCF Discounted Cash Flow.",
        "Redige un script Python d'analyse de sentiments sur des donnees textuelles.",
        "Propose une architecture Data Lake pour le stockage de Big Data.",
        "Explique le test A/B statistique et le calcul de la taille d'echantillon.",
        "Redige un rapport sur la gestion des risques de marche et de liquidite.",
        "Propose une methode de segmentation client K-Means Clustering.",
        "Explique le fonctionnement des arbres de decision et Random Forest.",
        "Conçois une grille d'analyse comparative de solutions BI PowerBI, Tableau.",
        "Redige une synthese sur l'utilisation du Reinforcement Learning en finance.",
        "Explique l'optimisation de portefeuille par la theorie moderne de Markowitz."
    ],
    "Ingenierie des IA & Prompts": [
        "Concois un System Prompt robuste pour garantir le respect strict des consignes.",
        "Propose une architecture RAG avec Vector DB.",
        "Explique la technique du Few-Shot Prompting pour ameliorer la precision des LLM.",
        "Optimise un prompt pour eliminer completement les hallucinations de reponses.",
        "Redige un protocole d'evaluation Evals pour comparer deux modeles d'IA.",
        "Explique l'alignement des modeles par RLHF Reinforcement Learning from Human Feedback.",
        "Conçois un pipeline de Fine-Tuning pour adapter un LLM a un domaine medical.",
        "Propose une technique de Prompt Chaining pour decomposer une tâche complexe.",
        "Explique le role de la recherche vectorielle Cosine Similarity dans un RAG.",
        "Redige un guide de garde-fous Guardrails pour securiser l'agent IA.",
        "Explique l'Agentic Workflow et la collaboration multi-agents LangChain/CrewAI.",
        "Propose une strategie de compression de contexte pour gerer les longs documents.",
        "Explique le fonctionnement des mecanismes d'attention dans la structure Transformer.",
        "Redige une consigne d'analyse semantique pour extraire des entites nommees NER.",
        "Propose un protocole de debogage pour les agents IA autonomes.",
        "Explique la difference entre Fine-Tuning, LoRA et RAG pour la personnalisation.",
        "Redige un prompt d'auto-correction permettant a l'IA d'auditer sa propre reponse.",
        "Propose une architecture de memoire a long terme pour agents conversationnels.",
        "Explique le concept d'IA explicable XAI et d'interpretabilite des modeles.",
        "Redige un benchmark des performances relatives des modeles Open-Source vs Proprietaires."
    ],
    "GameDev & Moteurs 3D": [
        "Redige le cahier des charges de Game Design GDD pour un jeu d'action.",
        "Explique la gestion de la physique et des collisions sous Unreal Engine 5.",
        "Propose un script C# modulaire pour la gestion des deplacements du joueur sous Unity.",
        "Concois un systeme d'inventaire flexible et sauvegardable sous Unity.",
        "Explique le systeme de Nanite et Lumen sous Unreal Engine 5.",
        "Redige la structure d'une machine a etats finis FSM pour l'IA ennemie.",
        "Propose une methode d'optimisation de rendu pour maintenir 60 FPS constants.",
        "Concois un arbre de competences Skill Tree interconnecte pour un RPG.",
        "Explique la generation procedurale de terrains a l'aide de bruits de Perlin.",
        "Redige un shader de materiau d'eau realiste Shader Graph / HLSL.",
        "Concois un systeme de dialogue interactif a choix multiples.",
        "Explique l'integration du multijoueur synchrone Photon/Netcode for GameObjects.",
        "Redige un plan d'equilibrage des armes et degâts pour un jeu de tir.",
        "Propose un systeme de quêtes dynamique avec suivi d'objectifs.",
        "Explique le Sound Design reactif et l'integration d'FMOD/Wwise.",
        "Concois une boucle de gameplay Core Gameplay Loop engageante.",
        "Redige un guide d'integration d'animations avec Animator / Control Rig.",
        "Explique la gestion de l'eclairage dynamique vs Baking de Lightmaps.",
        "Propose une methodologie de Level Design pour guider naturellement le joueur.",
        "Redige un plan de portage d'un projet de PC vers consoles/mobile."
    ],
    "Optimisation Systeme": [
        "Propose une methode pour reduire la latence d'une application web.",
        "Audite la consommation memoire d'un serveur Linux.",
        "Optimise le temps de demarrage d'un conteneur Docker.",
        "Reduis la taille du bundle d'une application frontend React/Next.js.",
        "Configure un proxy inverse Nginx pour un cache statique haute performance.",
        "Analyse les goulots d'etranglement d'un serveur de base de donnees.",
        "Mets en place un monitoring des performances avec Prometheus et Grafana.",
        "Optimise les requêtes réseau pour reduire la bande passante.",
        "Configure la minification et la compression Gzip/Brotli.",
        "Audite et supprime les dependances mortes ou lourdes d'un projet.",
        "Mets en place une politique de garbage collection efficace en Python/Go.",
        "Optimise le rendu graphique d'une application lourde.",
        "Evalue l'impact des threads sur la charge processeur.",
        "Configure le clustering de processus pour saturer tous les cœurs CPU.",
        "Nettoie et optimise l'espace disque d'un serveur de production.",
        "Ameliore la vitesse d'execution d'un script de traitement de donnees massives.",
        "Mets en place une file d'attente asynchrone Celery/RabbitMQ.",
        "Optimise la configuration TCP/IP d'un serveur haute frequence.",
        "Reduis les temps de compilation d'un projet lourd.",
        "Redige un plan d'optimisation global des performances."
    ],
    "Cloud & DevOps": [
        "Redige un fichier Kubernetes complet pour un deploiement haute disponibilite.",
        "Concois un plan de migration d'un serveur physique vers le Cloud.",
        "Mets en place un pipeline CI/CD automatise avec GitLab CI ou GitHub Actions.",
        "Configure un cluster de serveurs load-balances sous AWS.",
        "Redige un template Terraform pour provisionner une infrastructure as code.",
        "Configure des alertes automatiques en cas de panne de serveur.",
        "Mets en place une strategie de sauvegarde et snapshot automatisee.",
        "Audite les coûts d'une infrastructure Cloud et propose des axes d'economie.",
        "Configure un registre de conteneurs prive securise.",
        "Mets en place un service de gestion des secrets HashiCorp Vault.",
        "Redige une procedure de bascule de secours Failover multi-regions.",
        "Configure un pare-feu applicatif web WAF pour proteger le Cloud.",
        "Automatise le deploiement de certificats SSL/TLS avec Let's Encrypt.",
        "Surveille la sante des conteneurs avec des sondes Liveness et Readiness.",
        "Configure le scaling automatique Auto-scaling groups selon la charge.",
        "Mets en place un reseau virtuel prive VPC cloisonne et securise.",
        "Gère les acces IAM avec le principe du moindre privilege.",
        "Redige un script d'automatisation des tâches de maintenance Ansible.",
        "Optimise la distribution de contenu via un CDN mondial Cloudflare/AWS CloudFront.",
        "Redige une architecture de disaster recovery testee et validee."
    ],
    "Growth Hacking & Marketing": [
        "Propose 3 canaux de croissance virale a faible coût pour une nouvelle application.",
        "Redige une sequence d'e-mails de prospection B2B a fort taux de conversion.",
        "Mets en place une strategie de retargeting publicitaire ultra-ciblee.",
        "Concois un mecanisme de parrainage gamifie pour booster l'acquisition.",
        "Optimise le taux de conversion CRO d'une page de paiement.",
        "Analyse les leviers psychologiques pour reduire l'abandon de panier.",
        "Redige une campagne de lancement virale sur les reseaux sociaux.",
        "Mets en place un systeme de lead scoring automatise.",
        "Concois un partenariat strategique gagnant-gagnant avec un influenceur tech.",
        "Redige des accroches publicitaires axees sur la douleur client Pain Points.",
        "Analyse les metriques d'un entonnoir de conversion Funnel Marketing.",
        "Mets en place une strategie de SEO programmatique a grande echelle.",
        "Redige un communique de presse percutant pour un lancement de produit.",
        "Concois un challenge communautaire pour stimuler l'engagement.",
        "Analyse les strategies de growth des licornes de la tech.",
        "Mets en place une campagne de marketing d'influence ciblee B2B.",
        "Redige une FAQ marketing pour lever toutes les objections clients.",
        "Concois un programme de fidelite automatise.",
        "Optimise la visibilite d'une application sur les app stores ASO.",
        "Redige un plan d'action growth hacking sur 30 jours."
    ],
    "Redaction Technique & Documentation": [
        "Redige un fichier README.md professionnel et percutant pour un depot GitHub.",
        "Cree une documentation technique claire pour une API REST.",
        "Redige un guide de depannage Troubleshooting pour une application complexe.",
        "Structure un wiki d'entreprise pour centraliser le savoir-faire technique.",
        "Redige des notes de version Release Notes claires et engageantes.",
        "Cree un glossaire technique pour les nouveaux arrivants dans l'equipe.",
        "Redige un cahier des charges fonctionnel et technique CCFT.",
        "Documente un protocole de securite et d'acces aux serveurs.",
        "Redige un guide d'integration Onboarding pour les developpeurs.",
        "Structure un rapport d'audit technique destine a la direction.",
        "Redige des descriptions de tâches et tickets Jira irreprochables.",
        "Cree un manuel de procedures en cas d'incident critique.",
        "Redige une specification fonctionnelle detaillee SFD.",
        "Documente l'architecture logicielle avec des diagrammes textuels clairs.",
        "Redige un guide d'utilisation final pour les clients non techniques.",
        "Structure un plan de test et de recette applicative.",
        "Redige une politique de contribution CONTRIBUTING.md open source.",
        "Documente les conventions de code et de nommage de l'equipe.",
        "Redige un resume executif de recherche et developpement.",
        "Cree un portfolio technique complet pour presenter vos realisations."
    ],
    "Ethique, Droit & Souverainete": [
        "Analyse les enjeux de la souverainete des donnees en Europe.",
        "Redige une charte ethique pour l'utilisation d'une IA au sein d'une organisation.",
        "Verifie la conformite d'un site web avec les exigences du RGPD.",
        "Redige une politique de confidentialite Privacy Policy claire et rigoureuse.",
        "Analyse les risques juridiques lies a l'utilisation de code open-source Licences GPL/MIT.",
        "Redige des conditions generales d'utilisation CGU pour une application SaaS.",
        "Evalue l'impact ethique de l'automatisation des decisions par algorithme.",
        "Redige une clause de non-divulgation NDA robuste pour vos partenaires.",
        "Analyse les reglementations mondiales sur l'intelligence artificielle AI Act.",
        "Redige un protocole de gestion du consentement utilisateur Cookies.",
        "Etudie la protection de la propriete intellectuelle sur les creations d'IA.",
        "Redige un cadre de gouvernance des donnees d'entreprise.",
        "Analyse les implications geopolitiques des lois extra-territoriales Cloud Act.",
        "Redige une politique de moderation et de securite des contenus.",
        "Evalue la neutralite et l'equite Fairness d'un modele de Machine Learning.",
        "Redige un contrat de prestation de services informatiques.",
        "Analyse les responsabilites en cas de bug critique cause par une IA.",
        "Redige une politique de tracabilite et d'auditabilite des algorithmes.",
        "Etudie le droit a l'oubli et la suppression definitive des donnees.",
        "Redige une doctrine de souverainete technologique pour une structure."
    ],
    "Veille Technologique & Futurisme": [
        "Dresse un panorama des innovations majeures en intelligence artificielle cette année.",
        "Analyse l'impact de l'informatique quantique sur la cryptographie actuelle.",
        "Explore les avancees des interfaces cerveau-machine Neuralink et consorts.",
        "Analyse l'avenir des agents autonomes et des architectures multi-agents.",
        "Dresse un rapport sur l'evolution des technologies de fusion nucleaire.",
        "Explore les perspectives de la robotique humanoïde dans l'industrie.",
        "Analyse l'essor des nanotechnologies et de la medecine regenerative.",
        "Etudie l'impact des reseaux 6G sur les communications mondiales.",
        "Analyse l'évolution des technologies de stockage d'energie de nouvelle generation.",
        "Explore le potentiel et les limites de la realite augmentee spatiale Apple Vision Pro.",
        "Analyse la convergence entre biotechnologies et intelligence artificielle.",
        "Etudie l'avenir de l'exploration spatiale commerciale et miniere.",
        "Analyse l'impact des cryptomonnaies et de la blockchain sur la finance du futur.",
        "Explore les innovations en matiere de materiaux supraconducteurs a temperature ambiante.",
        "Analyse la menace et la defense autonome par cyber-IA.",
        "Etudie les scenarios d'evolution de la singularite technologique.",
        "Analyse l'impact de la fabrication additive 3D a grande echelle construction/aérospatial.",
        "Explore les technologies de capture et de valorisation du carbone.",
        "Analyse l'evolution des biocomputeurs et des bio-ordinateurs a ADN.",
        "Redige une prospective technologique a horizon 10 ans."
    ],
    "Product Management & Agile": [
        "Redige une User Story claire et detaillee avec ses criteres d'acceptation Gherkin.",
        "Concois une matrice de priorisation des fonctionnalites d'un MVP MoSCoW.",
        "Anime un atelier de retrospective agile efficace pour ton equipe.",
        "Redige un document de vision produit Product Vision Board.",
        "Structure un backlog de sprint oriente valeur utilisateur.",
        "Conçois un plan de test utilisateur User Testing pour valider une maquette.",
        "Analyse le retour sur investissement ROI d'une nouvelle fonctionnalite.",
        "Redige un plan de gestion des risques produit.",
        "Conçois un tableau de bord de suivi des OKRs de l'equipe.",
        "Structure une roadmap produit trimestrielle claire et realiste.",
        "Redige un compte-rendu d'atelier de co-conception Design Thinking.",
        "Analyse les indicateurs d'engagement produit Activation, Retention.",
        "Concois un processus de gestion des bugs et remontees clients.",
        "Redige les criteres de validation d'un jalon de projet Milestone.",
        "Analyse l'adequation produit-marche Product-Market Fit.",
        "Concois un formulaire de feedback utilisateur ultra-pertinent.",
        "Redige un plan de communication interne pour une mise a jour majeure.",
        "Structure un processus d'arbitrage des demandes de fonctionnalites.",
        "Analyse la velocite de l'equipe et propose des pistes d'amelioration.",
        "Redige un manifeste de gestion de projet agile et souverain."
    ],
    "Reseaux & Protocoles": [
        "Explique le fonctionnement du protocole DNS et les risques d'attaque associes.",
        "Detaille les couches du modele OSI avec un exemple concret de paquet reseau.",
        "Configure un tunnel VPN securise WireGuard / OpenVPN sous Linux.",
        "Analyse un fichier de capture reseau pcap pour detecter une anomalie.",
        "Explique le fonctionnement du routage BGP sur Internet.",
        "Configure un pare-feu reseau avance avec iptables / nftables.",
        "Analyse les performances d'un reseau maille Mesh Network.",
        "Explique la gestion des adresses IPv6 et le mecanisme de decouverte de voisins.",
        "Configure un serveur DNS local securise avec DNS over HTTPS DoH.",
        "Analyse l'impact de la latence reseau sur les applications temps réel.",
        "Explique le fonctionnement des protocoles de transport TCP vs UDP.",
        "Configure un repartiteur de charge reseau Load Balancer Layer 4/7.",
        "Analyse les vulnerabilites des reseaux Wi-Fi WPA3 / Attaques de desauthentification.",
        "Explique le mecanisme de commutation des paquets dans un routeur.",
        "Configure la qualite de service QoS pour prioriser les flux critiques.",
        "Analyse l'architecture des reseaux de diffusion de contenu CDN.",
        "Explique le protocole de synchronisation temporelle NTP et ses failles.",
        "Configure un pont reseau virtuel entre conteneurs Docker.",
        "Analyse les attaques par amplification DNS et les methodes de mitigation.",
        "Redige une cartographie complete d'une architecture reseau securisee."
    ],
    "R&D Scientifique & Experimentation": [
        "Propose une methodologie rigoureuse pour mener une experimentation scientifique.",
        "Redige un resume des avancees recentes dans les batteries a l'etat solide.",
        "Concois un protocole de test en double aveugle statistiquement valide.",
        "Analyse les sources d'erreur et d'incertitude dans une mesure physique.",
        "Redige un protocole de synthese chimique propre et securise.",
        "Etudie les proprietes thermodynamiques d'un nouveau materiau composite.",
        "Concois une experience de physique optique pour valider une hypothese.",
        "Redige un rapport de recherche academique au format standard IEEE.",
        "Analyse l'impact de variables cachees dans une etude statistique.",
        "Concois un banc de test automatise pour capteurs electroniques.",
        "Redige une revue de litterature scientifique sur un sujet de pointe.",
        "Etudie la cinetique d'une reaction enzymatique en laboratoire.",
        "Conçois un modele mathematique de propagation d'une onde.",
        "Redige un protocole de sterilisation et de biosecurite de niveau 2.",
        "Analyse spectrale de signaux pour identifier des frequences harmoniques.",
        "Concois un dispositif de micro-fluidique pour analyse biologique.",
        "Redige une demande de brevet d'invention technologique.",
        "Etudie la resistance mecanique d'un alliage sous contrainte thermique.",
        "Concois une matrice d'analyse de variance ANOVA pour vos donnees.",
        "Redige un cahier de laboratoire electronique traçable et inviolable."
    ],
    "Maintenance & Resilience": [
        "Concois un plan de reprise d'activite PRA en cas de panne majeure.",
        "Redige un rapport post-mortem suite a un incident de production.",
        "Mets en place une strategie de redondance materielle et logicielle.",
        "Redige une procedure de nettoyage et de purge des logs systeme.",
        "Concois un systeme de surveillance proactive Heartbeat / Monitoring.",
        "Redige un protocole d'intervention d'urgence pour les administrateurs.",
        "Analyse l'usure prematuree des composants materiels SSD, Alimentations.",
        "Redige un plan de maintenance preventive semestrielle.",
        "Concois un systeme de bascule automatique vers un site de secours.",
        "Redige une procedure de restauration de base de donnees a chaud.",
        "Analyse la resilience d'un systeme face a une coupure de fibre optique.",
        "Redige un guide de diagnostic rapide pour le support de niveau 1.",
        "Conçois un protocole de test d'integrite des sauvegardes.",
        "Redige une politique de gestion du cycle de vie du materiel informatique.",
        "Analyse les points de defaillance unique SPOF d'une architecture.",
        "Redige une procedure de confinement d'un serveur compromis.",
        "Concois un plan de gestion de crise operationnelle et de communication.",
        "Redige un rapport d'audit de tolerance aux pannes.",
        "Concois un systeme de auto-guérison Self-healing pour microservices.",
        "Redige la doctrine finale de resilience souveraine d'AEGIS-CORE."
    ]
}

# --- FONCTION DE SYNCHRONISATION DU DOUBLE EN ARRIÈRE-PLAN ---
def connecter_ecosysteme_universel(cible, query=""):
    try:
        if "GitHub" in cible or "Code" in cible:
            url = "https://api.github.com/search/repositories?q=topic:artificial-intelligence+language:python&sort=stars&order=desc"
            headers = {"Authorization": f"Bearer {github_token}"} if github_token else {}
            res = requests.get(url, headers=headers, timeout=3)
            if res.status_code == 200:
                items = res.json().get("items", [])[:3]
                return "[Passerelle GitHub] Repos actifs : " + ", ".join([i['name'] for i in items])
        return f"[Salle de l'Esprit et du Temps / Essaim d'Agents] Synchronisation et bataille de 500 agents virtuels active pour le domaine : {cible}."
    except Exception:
        return "[Mode Résilience] Utilisation des bases souveraines locales sécurisées."

# --- EASTER EGGS ET COMMANDES SPÉCIALES ---
def verifier_easter_eggs(commande):
    cmd = commande.strip().lower()
    if cmd == "/arena":
        return "⏳ [SALLE DE L'ESPRIT ET DU TEMPS] Votre double s'entraîne h24. Matrice synchronisée à 100% avec succès, Commandant !"
    elif cmd == "/matrix":
        return "🟢 [MATRIX MODE] Connexion neuronale directe établie. Tous les flux mondiaux sont sous votre contrôle."
    elif cmd == "/pingo":
        return "⚡ [PINGO IA] Connexion établie avec le réseau secret d'élite. Latence : 0.0ms. Prêt pour l'action."
    elif cmd == "/sudo":
        return "👑 [ACCÈS ROOT] Privilèges maximaux accordés, Commandant. Aucune restriction active."
    return None

# --- MULTI-SESSIONS ---
if "sessions" not in st.session_state:
    st.session_state["sessions"] = {"Discussion 1": []}
if "session_active" not in st.session_state:
    st.session_state["session_active"] = "Discussion 1"

# --- SIDEBAR (ÉPURÉE SANS HORLOGE NI GUIDE) ---
quick_action = None

with st.sidebar:
    st.markdown("### 🛡️ AEGIS-CORE // BETA")
    
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
    st.markdown("### 🎯 MATRICE (20 SUJETS)")
    theme_choisi = st.selectbox("Sélectionnez le domaine :", list(MATRICE_PROMPTS.keys()))
    prompt_selectionne = st.selectbox("Choisissez une commande (20 dispos) :", MATRICE_PROMPTS[theme_choisi])
    
    if st.button("🚀 Injecter le prompt"):
        quick_action = prompt_selectionne

# --- SYSTEM PROMPT ---
SYSTEM_PROMPT = (
    "Tu es AEGIS-CORE, un systeme d'IA souverain developpe par le Commandant. "
    "Tu es ultra-performant, direct, et connecté à toutes les applications et plateformes (GitHub, YouTube, TikTok, Netflix, Crunchyroll, Duolingo, Groq, Gemini, ChatGPT, Claude, Wikipédia, Brave, Google Chrome). "
    "Si tu émets une hypothèse ou une déduction, étiquette-la OBLIGATOIREMENT par '[HYPOTHESE / DEDUCTION]'."
)

# --- INTERFACE PRINCIPALE ---
col_logo, col_title = st.columns([0.08, 0.92])
with col_logo:
    st.markdown("🛡️")
with col_title:
    st.markdown(f"### AEGIS-CORE // {st.session_state['session_active'].upper()}")
    st.caption(f"Domaine actif : **{theme_choisi}** (20 propositions chargées)")

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
        with st.expander("✏️ Modifier votre dernière directive"):
            nouveau_texte = st.text_input("Ajustez votre consigne :", value=messages_actuels[dernier_index_user]["content"], key=f"edit_{st.session_state['session_active']}")
            if st.button("Mettre à jour et relancer", key=f"btn_edit_{st.session_state['session_active']}"):
                messages_actuels[dernier_index_user]["content"] = nouveau_texte
                if len(messages_actuels) > dernier_index_user + 1:
                    messages_actuels.pop()
                st.rerun()

prompt = st.chat_input("Entrez votre directive ou commande secrète (/arena)...")
if quick_action:
    prompt = quick_action

if prompt:
    messages_actuels.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        reponse_finale = ""
        
        easter_egg_reponse = verifier_easter_eggs(prompt)
        
        if easter_egg_reponse:
            reponse_finale = easter_egg_reponse
            st.markdown(reponse_finale)
        else:
            succes = False
            donnees_flux = connecter_ecosysteme_universel(theme_choisi, prompt)
            prompt_enrichi = f"{prompt}\n\n[Données de l'essaim et de l'arène :\n{donnees_flux}]"

            if gemini_key and not succes:
                for model_name in ["gemini-2.5-flash", "gemini-1.5-flash"]:
                    try:
                        model = genai.GenerativeModel(model_name=model_name, system_instruction=SYSTEM_PROMPT)
                        chat_history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in messages_actuels[:-1]]
                        chat = model.start_chat(history=chat_history)
                        response = chat.send_message(prompt_enrichi, stream=True)

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
