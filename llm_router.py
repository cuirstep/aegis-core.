import os
import streamlit as st
from groq import Groq
import google.generativeai as genai

def route_and_generate(prompt, system_prompt="", provider="auto", model_name="", history=None):
    """
    Routeur ultra-rapide corrigé et sécurisé.
    """
    if history is None:
        history = []

    erreurs = []

    # Filtrer l'historique pour éviter les messages vides (Correction de l'erreur Gemini)
    valid_history = [m for m in history if m.get("content", "").strip() != ""]

    # --- 1. GROQ (Modèle stable : llama3-8b-8192) ---
    if provider == "groq" or provider == "auto":
        groq_key = st.secrets.get("GROQ_API_KEY_1", st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", "")))
        if groq_key:
            try:
                client = Groq(api_key=groq_key)
               m_name = model_name if model_name else "llama-3.1-8b-instant"
                messages_payload = [{"role": "system", "content": system_prompt}] + valid_history
                
                stream = client.chat.completions.create(
                    model=m_name,
                    messages=messages_payload,
                    stream=True,
                    temperature=0.3
                )
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
                return
            except Exception as e:
                erreurs.append(f"Groq Error: {e}")

    # --- 2. GOOGLE GEMINI (Secours) ---
    if provider == "gemini" or provider == "auto":
        gemini_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
        if gemini_key:
            try:
                genai.configure(api_key=gemini_key)
                m_name = model_name if model_name else "gemini-1.5-flash"
                model = genai.GenerativeModel(model_name=m_name, system_instruction=system_prompt)
                
                chat_history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in valid_history[:-1]]
                chat = model.start_chat(history=chat_history)
                response = chat.send_message(prompt, stream=True)
                
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
                return
            except Exception as e:
                erreurs.append(f"Gemini Error: {e}")

    yield f"Erreur de routeur. Détails : {erreurs}"
