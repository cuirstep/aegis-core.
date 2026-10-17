import os
import requests
import json
import streamlit as st

def route_and_generate(*args, **kwargs):
    # Récupération de la clé Groq depuis les secrets Streamlit
    groq_api_key = ""
    try:
        groq_api_key = st.secrets.get("GROQ_API_KEY_1", "")
    except Exception:
        pass
    
    if not groq_api_key:
        groq_api_key = os.environ.get("GROQ_API_KEY_1", os.environ.get("GROQ_API_KEY", ""))

    prompt = kwargs.get("prompt", args[0] if args else "")
    system_prompt = kwargs.get("system_prompt", "")
    history = kwargs.get("history", [])
    model = kwargs.get("model", "llama-3.1-8b-instant")
    
    if history is None:
        history = []
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    for msg in history:
        messages.append(msg)
        
    messages.append({"role": "user", "content": prompt})

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": messages,
        "stream": True
    }
    
    response = requests.post(url, json=data, headers=headers, stream=True)
    if response.status_code != 200:
        yield f"Erreur API Groq: {response.status_code} - {response.text}"
        return

    for line in response.iter_lines():
        if line:
            line_decoded = line.decode('utf-8')
            if line_decoded.startswith('data: '):
                json_str = line_decoded[6:]
                if json_str.strip() == '[DONE]':
                    break
                try:
                    obj = json.loads(json_str)
                    delta = obj['choices'][0]['delta'].get('content', '')
                    if delta:
                        yield delta
                except Exception:
                    pass
