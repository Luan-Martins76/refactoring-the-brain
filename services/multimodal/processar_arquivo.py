from services.multimodal.auxiliales.docx import extrair_texto_docx
from services.multimodal.auxiliales.ocr import ocr_imagem, texto_valido
from services.multimodal.auxiliales.pdf import extrair_texto_pdf
from services.multimodal.modelos.visao import call_llm_visao 
from services.multimodal.modelos.call_codigo import analisar_codigo
from services.config_ollama import EXTENSOES_CODIGO

import mimetypes
import os

def processar_arquivo(caminho_arquivo: str, mensagem_usuario: str = "", mime_hint: str = None) -> str:
    """
    Processa o arquivo enviado pelo usuário e retorna um bloco de contexto
    pronto pra ser injetado no prompt principal.
    """
    mime, _ = mimetypes.guess_type(caminho_arquivo)
    mime = mime_hint or mime or ""  # ← prioriza o mime vindo do Flask
    print(f"[MULTIMODAL] Processando arquivo: {os.path.basename(caminho_arquivo)} | mime: {mime}")

    # 🖼️ IMAGENS
    if mime.startswith("image"):
        texto_ocr = ocr_imagem(caminho_arquivo)
        if texto_valido(texto_ocr):
            print("[MULTIMODAL]  OCR com sucesso")
            return f"O usuário enviou uma imagem com texto.\n\nConteúdo extraído:\n{texto_ocr}\n\nPergunta do usuário:\n{mensagem_usuario}"

        # fallback: modelo de visão
        print("[MULTIMODAL] OCR insuficiente, usando modelo de visão...")
        descricao = call_llm_visao(
            caminho_arquivo,
            prompt="Analise a imagem enviada por um aluno. Extraia textos visíveis, datas, horários, nomes de disciplinas e locais. Se não houver texto relevante, descreva brevemente o que há na imagem."
        )
        if descricao:
            return f"O usuário enviou uma imagem.\n\nDescrição:\n{descricao}\n\nPergunta do usuário:\n{mensagem_usuario}"
        return f"O usuário enviou uma imagem, mas não foi possível interpretá-la.\n\nPergunta do usuário:\n{mensagem_usuario}"

    #  PDF
    elif mime == "application/pdf":
        texto = extrair_texto_pdf(caminho_arquivo)
        if texto_valido(texto):
            return f"O usuário enviou um PDF.\n\nConteúdo:\n{texto}\n\nPergunta do usuário:\n{mensagem_usuario}"

        # fallback OCR: converte páginas pra imagem primeiro
        try:
            from pdf2image import convert_from_path
            imagens = convert_from_path(caminho_arquivo)
            textos_ocr = []
            for img in imagens:
                import tempfile
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    img.save(tmp.name)
                    t = ocr_imagem(tmp.name)
                    os.unlink(tmp.name)
                    if t:
                        textos_ocr.append(t)
            texto_ocr = "\n".join(textos_ocr)
            if texto_valido(texto_ocr):
                return f"O usuário enviou um PDF escaneado.\n\nConteúdo via OCR:\n{texto_ocr}\n\nPergunta do usuário:\n{mensagem_usuario}"
        except ImportError:
            print("[MULTIMODAL] ⚠️ pdf2image não instalado, OCR em PDF indisponível.")

        return f"O usuário enviou um PDF, mas não foi possível extrair texto.\n\nPergunta do usuário:\n{mensagem_usuario}"

    #  DOCX
    elif "wordprocessingml" in mime:
        texto = extrair_texto_docx(caminho_arquivo)
        if texto_valido(texto):  
            return f"O usuário enviou um documento Word.\n\nConteúdo:\n{texto}\n\nPergunta do usuário:\n{mensagem_usuario}"
        return f"O usuário enviou um documento Word, mas não foi possível extrair texto.\n\nPergunta do usuário:\n{mensagem_usuario}"
    
     # 💻 CÓDIGO-FONTE 
    elif any(caminho_arquivo.endswith(f".{ext}") for ext in EXTENSOES_CODIGO):
        analise = analisar_codigo(caminho_arquivo, mensagem_usuario=mensagem_usuario)
        if analise:
            contexto_str = (
                f"O usuário enviou um arquivo de código: `{os.path.basename(caminho_arquivo)}`\n\n"
                f"ANÁLISE TÉCNICA ESTRUTURADA (JSON gerado pelo qwen-coder — use para embasar sua resposta, não reproduza o JSON bruto):\n{analise}\n\n"
                f"Pergunta do usuário:\n{mensagem_usuario}"
            )
            return contexto_str, analise 
        try:
            with open(caminho_arquivo, "r", encoding="utf-8", errors="replace") as f:
                conteudo = f.read()
            return (
                f"O usuário enviou um arquivo de código: `{os.path.basename(caminho_arquivo)}`\n\nConteúdo:\n{conteudo[:4000]}\n\nPergunta do usuário:\n{mensagem_usuario}",
                None
            )
        except Exception as e:
            print(f"[CODIGO] ❌ Fallback falhou: {e}")
            return f"O usuário enviou um código, mas não foi possível processá-lo.\n\nPergunta do usuário:\n{mensagem_usuario}", None
            
    # TXT
    elif mime.startswith("text"):
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                texto = f.read()
            return f"O usuário enviou um arquivo de texto.\n\nConteúdo:\n{texto}\n\nPergunta do usuário:\n{mensagem_usuario}"
        except Exception as e:
            print(f"[MULTIMODAL] ❌ Erro lendo TXT: {e}")

    # fallback
    return f"O usuário enviou um arquivo não suportado: {os.path.basename(caminho_arquivo)}\n\nPergunta do usuário:\n{mensagem_usuario}"