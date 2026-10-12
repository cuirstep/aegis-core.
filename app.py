with st.chat_message("assistant"):
        reponse_finale = ""
        succes = False
        diagnostic_log = []

        # --- TENTATIVE 1 : GEMINI (via SDK officiel avec le nouveau modèle standard) ---
        if gemini_key and not succes:
            for model_name in ["gemini-3.8-flash", "gemini-1.5-flash"]:
                try:
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction=SYSTEM_PROMPT
                    )
                    chat_history = []
                    for m in st.session_state.messages[:-1]:
                        role = "user" if m["role"] == "user" else "model"
                        chat_history.append({"role": role, "parts": [m["content"]]})
                    
                    chat = model.start_chat(history=chat_history)
                    response = chat.send_message(prompt, stream=True)

                    def generate_gemini_sdk_stream():
                        for chunk in response:
                            if chunk.text:
                                for char in chunk.text:
                                    yield char
                                    time.sleep(0.0015)

                    reponse_finale = st.write_stream(generate_gemini_sdk_stream())
                    succes = True
                    break
                except Exception as e:
                    diagnostic_log.append(f"Gemini SDK {model_name}: {str(e)}")

        # --- TENTATIVE 2 : ROTATION GROQ (Modèles actuels mis à jour) ---
        if groq_keys and not succes:
            st.caption("⚠️ *Alerte Meta-Router : Bascule automatique sur les canaux de secours Groq...*")
            messages_payload = [{"role": "system", "content": SYSTEM_PROMPT}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            
            for idx, g_key in enumerate(groq_keys):
                for groq_model in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
                    try:
                        client = Groq(api_key=g_key)
                        stream = client.chat.completions.create(
                            model=groq_model, 
                            messages=messages_payload, 
                            stream=True
                        )
                        
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
                        diagnostic_log.append(f"Groq Key {idx+1} ({groq_model}): {str(e)}")
                if succes:
                    break

        if not succes and not reponse_finale:
            reponse_finale = "❌ **Erreur critique du Meta-Router :**\n\n- " + "\n- ".join(diagnostic_log)
            st.markdown(reponse_finale)

        st.session_state.messages.append({"role": "assistant", "content": reponse_finale})
