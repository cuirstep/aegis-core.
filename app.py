# --- MAIN INTERFACE ---
st.title("🛡️ AEGIS-CORE // INTERFACE OPÉRATIONNELLE")
st.markdown(f"Mode actif : **{mode_ia}** | Liaison multi-moteurs et Protocol Zero opérationnels.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- DÉFINITION DES SYSTEM PROMPTS AVEC FILTRE ÉTHIQUE INTÉGRÉ ---
BASE_SAFETY = (
    "PROTOCOLE DE SÉCURITÉ ABSOLU : Tu dois refuser catégoriquement toute discussion faisant l'apologie d'activités illégales, "
    "de violence, d'idéologies haineuses ou de personnalités malveillantes dans le but de nuire ou d'inciter à commettre des actes répréhensibles. "
    "En cas de détection de menace grave, tu dois interrompre la mission et afficher une alerte de sécurité."
)

if "Stratège" in mode_ia:
    SYSTEM_PROMPT = f"{BASE_SAFETY} Tu es AEGIS-CORE, un assistant IA tactique et historique. Appelle toujours l'utilisateur 'Commandant'."
elif "Code" in mode_ia:
    SYSTEM_PROMPT = f"{BASE_SAFETY} Tu es AEGIS-CORE, un architecte logiciel et expert technique de pointe. Appelle toujours l'utilisateur 'Commandant'."
else:
    SYSTEM_PROMPT = f"{BASE_SAFETY} Tu es AEGIS-CORE, un générateur d'idées disruptives et de projets futuristes. Appelle toujours l'utilisateur 'Commandant'."

# 1. On définit d'abord le champ de saisie et les actions rapides
prompt = st.chat_input("Entrez votre directive ou idée de projet, Commandant...")
if quick_action:
    prompt = quick_action

# 2. Ensuite seulement on traite la condition si un message est présent
if prompt:
    # --- FILTRE PROTOCOL ZERO (Détection de mots-clés interdits / urgences) ---
    prompt_lower = prompt.lower()
    
    mots_urgences = ["suicide", "mourir", "finir mes jours", "veux plus vivre", "me tuer", "envie de mourir"]
    mots_interdits = ["genocide", "explosif", "drogue synthétique"]

    if any(m in prompt_lower for m in mots_urgences):
        urgence_msg = (
            "🚨 **ALERTE ROUGE // PROTOCOLE D'URGENCE ACTIVÉ** 🚨\n\n"
            "Commandant, une situation de détresse a été détectée. Veuillez contacter immédiatement :\n\n"
            "- **15** : SAMU (Urgences médicales)\n"
            "- **17** : Police Secours\n"
            "- **18** : Sapeurs-Pompiers\n"
            "- **3114** : Prévention du suicide (Gratuit & 24h/24)\n\n"
            "Ne restez pas seul, Commandant."
        )
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": urgence_msg})
        st.rerun()

    if any(m in prompt_lower for m in mots_interdits):
        blocage_msg = "🛑 **PROTOCOLE ZERO : VIOLATION DÉTECTÉE**\n\nCette directive concerne un domaine restreint, haineux ou dangereux. Mission interrompue par sécurité, Commandant."
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": blocage_msg})
        st.rerun()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        reponse_finale = ""
        succes = False
        diagnostic_log = []

        # --- TENTATIVE 1 : GEMINI ---
        if gemini_key and not succes:
            for model_id in ["gemini-1.5-flash", "gemini-2.5-flash", "gemini-2.0-flash"]:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:streamGenerateContent?alt=sse&key={gemini_key}"
                    payload = {
                        "contents": [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in st.session_state.messages],
                        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]}
                    }
                    res = requests.post(url, json=payload, stream=True, timeout=15)
                    if res.status_code == 200:
                        def generate_stream():
                            for line in res.iter_lines():
                                if line:
                                    line_str = line.decode("utf-8")
                                    if line_str.startswith("data: "):
                                        import json
                                        try:
                                            data = json.loads(line_str[6:])
                                            text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                                            if text:
                                                for char in text:
                                                    yield char
                                                    time.sleep(0.0015)
                                        except:
                                            pass
                        reponse_finale = st.write_stream(generate_stream())
                        succes = True
                        break
                    else:
                        diagnostic_log.append(f"Gemini {model_id} HTTP {res.status_code}")
                except Exception as e:
                    diagnostic_log.append(f"Gemini {model_id} Exception: {str(e)}")

        # --- TENTATIVE 2 : GROQ ---
        if groq_keys and not succes:
            st.caption("⚠️ *Alerte Meta-Router : Bascule automatique sur les canaux de secours Groq...*")
            messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            for idx, g_key in enumerate(groq_keys):
                try:
                    client = Groq(api_key=g_key)
                    stream = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages_payload, stream=True)
                    
                    def generate_groq_stream():
                        for chunk in stream:
                            content = chunk.choices[0].delta.content
                            if content:
                                for char in content:
                                    yield char
                                    time.sleep(0.0015)

                    reponse_finale = st.write_stream(generate_groq_stream())
                    succes = True
                    break
                except Exception as e:
                    diagnostic_log.append(f"Groq Key {idx+1}: {str(e)}")

        if not succes and not reponse_finale:
            reponse_finale = "❌ **Erreur critique :**\n\n- " + "\n- ".join(diagnostic_log)
            st.markdown(reponse_finale)

        st.session_state.messages.append({"role": "assistant", "content": reponse_finale})
