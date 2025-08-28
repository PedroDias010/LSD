import pdfplumber
import io

def extract_pdf(file_data):
    """
    Extrai texto de um arquivo PDF.
    
    Args:
        file_data (bytes): Conteúdo do arquivo PDF em bytes.
    
    Returns:
        str: Texto extraído do PDF ou None se houver erro.
    """
    try:
        with pdfplumber.open(io.BytesIO(file_data)) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
            return text.strip()
    except Exception as e:
        print(f"Erro ao extrair texto do PDF: {e}")
        return None