import subprocess
import time
import requests

def garantir_ollama_rodando():
    """
    acabei me deparando com O erro WinError 100611 impossibilitando resposta dos modelos, 
    isso é simplesmente quando o ollama não ta carregado...
    isso garante que ele acorde
    """
    try:
        requests.get("http://localhost:11434", timeout=2)
    except requests.exceptions.ConnectionError:
        print("[OLLAMA] Não está rodando, iniciando...")
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW  
        )
        time.sleep(3)  
        print("[OLLAMA] Iniciado.")