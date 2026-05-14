try:
    import easyocr
    _ocr_reader = easyocr.Reader(['pt'], gpu=False)
except ImportError:
    _ocr_reader = None


def ocr_imagem(imagem_path: str) -> str:
    """Extrai texto de imagem via EasyOCR."""
    if not _ocr_reader:
        print("[MULTIMODAL]  EasyOCR não instalado.")
        return ""
    try:
        resultado = _ocr_reader.readtext(imagem_path, detail=0)
        return "\n".join(resultado).strip()
    except Exception as e:
        print(f"[MULTIMODAL]  Erro OCR: {e}")
        return ""
    

def texto_valido(texto: str) -> bool:
    """Heurística simples: texto com pelo menos 30 chars e espaços."""
    if not texto:
        return False
    texto = texto.strip()
    return len(texto) >= 30 and " " in texto