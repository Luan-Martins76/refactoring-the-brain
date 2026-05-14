try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None

    
def extrair_texto_docx(docx_path: str) -> str:
    """Extrai texto de arquivo Word (.docx)."""
    if not DocxDocument:
        print("[MULTIMODAL]  python-docx não instalado.")
        return ""
    try:
        doc = DocxDocument(docx_path)
        return "\n".join([p.text for p in doc.paragraphs]).strip()
    except Exception as e:
        print(f"[MULTIMODAL]  Erro DOCX: {e}")
        return ""