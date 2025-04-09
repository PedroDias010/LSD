from fastapi import FastAPI, UploadFile, File, HTTPException
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv
import json
import io
import PyPDF2

# Carrega variáveis de ambiente
load_dotenv()

# Configurações
app = FastAPI()     

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

ALLOWED_TYPES = {"image/jpeg", "image/png", "application/pdf"}


 #Extrai texto de um PDF
def extract_pdf(pdf_data):
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_data))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        raise Exception(f"Erro ao extrair texto do PDF: {str(e)}")

@app.post("/extract-data/")
async def extract_data(file: UploadFile = File(...)):
    # Extrai dados de uma imagem ou PDF e retorna em JSON

    # Verifica tipo de arquivo
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Apenas PNG, JPEG ou PDF são permitidos")

    # Lê o arquivo
    try:
        file_data = await file.read()
        
        # Prompt base para o Gemini
        prompt = """
        Analise o conteúdo fornecido e extraia os seguintes dados em formato JSON:
        - CNPJ (formato XX.XXX.XXX/XXXX-XX)
        - CEP (formato XXXXX-XXX)
        - Data de emissão (formato DD/MM/AAAA HH:MM:SS)
        - Valor total (formato R$ X,XX)
        Retorne apenas o JSON com os dados ou valores vazios se não encontrados.
        """

        # Processa de acordo com o tipo de arquivo
        if file.content_type == "application/pdf":
            # Processa PDF
            text = extract_pdf(file_data)
            response = model.generate_content([prompt, text])
        else:
            # Processa imagem
            img = Image.open(io.BytesIO(file_data))
            response = model.generate_content([prompt, img])

        print(response.text)
        return {response.text}


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
    