import requests

OLLAMA_URL = "http://localhost:11434/api/generate" 
REQUEST_TIMEOUT_SECONDS = 180
MEMORY_TIMEOUT_SECONDS  = 180  

#  Papéis dos modelos
MODELO_MEMORIA   = "mistral-nemo:12b"   # Responsável por resumir o histórico 
MODELO_RESPOSTA  = "gemma3:4b"          # Responsável por responder ao usuário
MODELO_VISAO     = "llava-llama3"       # Responsável por interpretar imagens
MODELO_CODIGO = "qwen2.5-coder:7b"      # Especialista em código

EXTENSOES_CODIGO = {
    "py", "js", "ts", "jsx", "tsx", "java", "c", "cpp", "cs",
    "go", "rs", "php", "rb", "kt", "swift", "sh", "sql",
    "html", "css", "json", "yaml", "yml", "toml", "xml", "md",
}         

HISTORICO_MEMORIA_MAX  = 20  
RESUMO_MINIMO_MSGS     = 4   


def call_llm(model, prompt, temperature=0.3, timeout=REQUEST_TIMEOUT_SECONDS, keep_alive=True, system=None): 
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
        "keep_alive": -1 if keep_alive else 0,
    }
    if system:
        payload["system"] = system
    response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
    response.raise_for_status()
    result = response.json()
    return result.get("response", "")