import os
import streamlit as st
from groq import Groq
import google.generativeai as genai
import requests
import json

def route_and_generate(prompt, system_prompt="", provider="auto", model_name="", history=None):
    """
    Routeur ultra-rapide optimisé pour l'instantanéité via Groq (Llama-3.1-8b-instant).
    """
    if history is None:
        history = []

    erreurs = []

    # --- 1. PRIORITÉ RAPIDITÉ EXTRÊME : GROQ (LLAMA-3.1-8B-INSTANT) ---
    if provider == "groq" or provider == "auto":
        groq_key = st.secrets.get("GROQ_API_KEY_1", st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", "")))
        if groq_key:
            try:
                client = Groq(api_key=groq_key)
                m_name = model_name if model_name else "llama-3.1-8b-instant"
                messages_payload = [{"role": "system", "content": system_prompt}] + history
                
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
                erreurs.append(f"Groq Fast Error: {e}")

    # --- 2. FALLBACK SECONDAIRE : GOOGLE GEMINI ---
    if provider == "gemini" or provider == "auto":
        gemini_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
        if gemini_key:
            try:
                genai.configure(api_key=gemini_key)
                m_name = model_name if model_name else "gemini-3.8-flash"
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

    # --- 3. FOURNISSEUR OLLAMA (Local PC uniquement) ---
    if provider == "ollama":
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
            erreurs.append(f"Ollama Error: {e}")

    yield f"Erreur de réponse. Détails : {erreurs}"
