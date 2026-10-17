import os
import streamlit as st
from groq import Groq
import google.generativeai as genai
# Import optionnel pour OpenAI / Anthropic si les packages sont installés
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import anthropic
except ImportError:
    anthropic = None

import requests  # Pour communiquer avec Ollama en local

def route_and_generate(prompt, system_prompt="", provider="auto", model_name="", history=None):
    """
    Route la requête vers le LLM sélectionné ou applique un fallback intelligent.
    Providers supportés : 'gemini', 'groq', 'openai', 'claude', 'ollama', 'auto'
    """
    if history is None:
        history = []

    reponse_texte = ""
    erreurs = []

    # --- 1. FOURNISSEUR : GOOGLE GEMINI ---
    if provider == "gemini" or (provider == "auto" and not reponse_texte):
        gemini_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
        if gemini_key:
            try:
                genai.configure(api_key=gemini_key)
                m_name = model_name if model_name else "gemini-1.5-flash"
                model = genai.GenerativeModel(model_name=m_name, system_instruction=system_prompt)
                
                chat_history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in history[:-1]]
                chat = model.start_chat(history=chat_history)
                response = chat.send_message(prompt, stream=True)
                
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
                return
            except Exception as e:
                erreurs.append(f"Gemini Error: {e}")

    # --- 2. FOURNISSEUR : GROQ (Llama / Mixtral) ---
    if provider == "groq" or (provider == "auto" and not reponse_texte):
        groq_key = st.secrets.get("GROQ_API_KEY_1", st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", "")))
        if groq_key:
            try:
                client = Groq(api_key=groq_key)
                m_name = model_name if model_name else "llama-3.3-70b-versatile"
                messages_payload = [{"role": "system", "content": system_prompt}] + history
                
                stream = client.chat.completions.create(
                    model=m_name,
                    messages=messages_payload,
                    stream=True
                )
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
                return
            except Exception as e:
                erreurs.append(f"Groq Error: {e}")

    # --- 3. FOURNISSEUR : OLLAMA (Modèles locaux sur le PC) ---
    if provider == "ollama" or (provider == "auto" and not reponse_texte):
        try:
            m_name = model_name if model_name else "llama3"
            url = "http://localhost:11434/api/chat"
            payload = {
                "model": m_name,
                "messages": [{"role": "system", "content": system_prompt}] + history,
                "stream": True
            }
            response = requests.post(url, json=payload, stream=True, timeout=5)
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        body = json.loads(line.decode("utf-8"))
                        content = body.get("message", {}).get("content", "")
                        if content:
                            yield content
                return
        except Exception as e:
            erreurs.append(f"Ollama Local Error (Vérifiez si Ollama tourne sur le PC): {e}")

    # Si aucun fournisseur n'a répondu
    yield f"Erreur critique du routeur LLM. Aucun canal distant ou local n'a pu répondre. Détails : {erreurs}"
