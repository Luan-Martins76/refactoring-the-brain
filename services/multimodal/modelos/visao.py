from services.config_ollama import OLLAMA_URL, MODELO_VISAO

import requests
import base64

def call_llm_visao(imagem_path: str, prompt: str) -> str:
    """
    Chama o modelo de visão (llava) via Ollama com a imagem em base64.
    Retorna a descrição gerada ou string vazia se falhar.
    """
    try:
        with open(imagem_path, "rb") as f:
            imagem_b64 = base64.b64encode(f.read()).decode("utf-8")

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODELO_VISAO,
                "prompt": prompt,
                "images": [imagem_b64],
                "stream": False,
                "options": {"temperature": 0.2},
                "keep_alive": 0,  # descarrega apos uso pra nao brigar com gemma/mistral/llava/modelo dos codigos que esqueci comop escreve.
            },
            timeout=180,
        )
        
        response.raise_for_status()
        resultado = response.json().get("response", "").strip()
        print(f"[VISAO]  descrição gerada ({len(resultado)} chars): '{resultado[:80]}'")
        return resultado
        
    except Exception as e:
        print(f"[VISAO]  ERRO no modelo: {e}")
        return ""