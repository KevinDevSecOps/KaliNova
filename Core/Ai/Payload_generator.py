import openai  # Usar API de GPT-4o o local (Ollama)

def generate_evasive_payload(cve: str) -> str:
    prompt = f"""Genera código Python3 para explotar {cve} con:
    - Ofuscación XOR  
    - Bypass de Sandbox  
    - Formato Base64  
    """
    response = openai.ChatCompletion.create(model="gpt-4", messages=[{"role": "user", "content": prompt}])
    return response.choices[0].message.content
