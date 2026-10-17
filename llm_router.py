import os
import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

def route_and_generate(messages, model="llama-3.1-8b-instant"):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
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
                    import json
                    obj = json.loads(json_str)
                    delta = obj['choices'][0]['delta'].get('content', '')
                    if delta:
                        yield delta
                except Exception:
                    pass
