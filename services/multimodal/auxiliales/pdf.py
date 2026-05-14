try:
    import pdfplumber
except ImportError:
    pdfplumber = None


def extrair_texto_pdf(pdf_path: str) -> str:
    """Extrai texto de PDF via pdfplumber."""
    if not pdfplumber:
        print("[MULTIMODAL]  pdfplumber não instalado.")
        return ""
    texto = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for pagina in pdf.pages:
                texto += (pagina.extract_text() or "") + "\n"
    except Exception as e:
        print(f"[MULTIMODAL]  Erro PDF: {e}")
    return texto.strip()