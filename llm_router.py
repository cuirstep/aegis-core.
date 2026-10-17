import os
import requests
import json
import streamlit as st

def route_and_generate(*args, **kwargs):
    # Récupération de toutes les clés disponibles (1 à 5)
    keys = []
    for i in range(1, 6):
        try:
            k = st.secrets.get(f"GROQ_API_KEY_{i}", "")
            if k:
                keys.append(k)
        except Exception:
            pass
        
        env_k = os.environ.get(f"GROQ_API_KEY_{i}", "")
        if env_k and env_k not in keys:
            keys.append(env_k)
            
    # Fallback clé unique si aucune numérotée n'est trouvée
    single_key = os.environ.get("GROQ_API_KEY", "")
    if single_key and single_key not in keys:
        keys.append(single_key)
        
    if not keys:
        yield "Erreur : Aucune clé API Groq n'a été trouvée dans vos secrets Streamlit."
        return

    prompt = kwargs.get("prompt", args[0] if args else "")
    if prompt is None:
        prompt = ""
    prompt = str(prompt).strip()
    if not prompt:
        prompt = "Bonjour"

    system_prompt = kwargs.get("system_prompt", "")
    history = kwargs.get("history", [])
    
    # Liste des modèles valides à tester en cascade
    models_to_try = [
        kwargs.get("model", "llama-3.1-8b-instant"),
        "openai/gpt-oss-20b",
        "llama-3.3-70b-versatile"
    ]
    
    if history is None:
        history = []
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": str(system_prompt)})
    
    for msg in history:
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            content = msg.get("content")
            if content is not None and str(content).strip():
                messages.append({"role": msg["role"], "content": str(content)})
        
    messages.append({"role": "user", "content": prompt})

    url = "https://api.groq.com/openai/v1/chat/completions"
    
    success = False
    response = None
    
    # Boucle de secours croisée (Clés x Modèles)
    for key in keys:
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        for model in models_to_try:
            data = {
                "model": model,
                "messages": messages,
                "stream": True
            }
            try:
                resp = requests.post(url, json=data, headers=headers, stream=True, timeout=10)
                if resp.status_code == 200:
                    response = resp
                    success = True
                    break
            except Exception:
                continue
        if success:
            break

    if not success or response is None:
        yield "Erreur API Groq : Toutes les clés et tous les modèles ont échoué. Vérifiez vos secrets."
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
