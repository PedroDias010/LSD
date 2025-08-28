from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import google.generativeai as genai 
from PIL import Image
import io
import json
from config import GEMINI_API_KEY, gemini_client
from models import ExtractedData
from db import get_db
from pdf import extract_pdf
from sqlalchemy.orm import Session
import logging

# Configurar logging
logger = logging.getLogger(__name__)

ALLOWED_TYPES = {"image/jpeg", "image/png", "application/pdf"}

router = APIRouter()

@router.get("/", tags=["root"])
def read_root(db: Session = Depends(get_db)):
    try:
        result = db.execute("SELECT 1 AS number").fetchone()
        return {"message": "Conexão com PostgreSQL OK", "result": {"number": result[0]}}
    except Exception as e:
        logger.error(f"Erro na conexão com o banco: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro na conexão com o banco")

@router.post("/extract-data", tags=["extract"])
async def extract_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Apenas PNG, JPEG ou PDF são permitidos")
    
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="API Key do Gemini não configurada")
    
    try:
        file_data = await file.read()
        
        # Validar se o arquivo não está vazio
        if len(file_data) == 0:
            raise HTTPException(status_code=400, detail="Arquivo vazio")
        
        prompt = """
        Analise o conteúdo fornecido e extraia os seguintes dados em formato JSON:
        - CNPJ (formato XX.XXX.XXX/XXXX-XX)
        - CEP (formato XXXXX-XXX)
        - Data de emissão (formato DD/MM/AAAA HH:MM:SS)
        - Valor total (formato R$ X,XX)
        Retorne apenas o JSON com os dados ou valores vazios se não encontrados.
        """
        
        try:
            # Usar o cliente já configurado do config.py
            if gemini_client is None:
                raise HTTPException(status_code=500, detail="Serviço Gemini não disponível")
            
            if file.content_type == "application/pdf":
                text = extract_pdf(file_data)
                if not text:
                    raise HTTPException(status_code=400, detail="PDF inválido ou sem conteúdo extraível")
                
                response = gemini_client.generate_content(prompt + "\n\n" + text)
                
            else:
                # Para imagens, usar contexto seguro
                with Image.open(io.BytesIO(file_data)) as img:
                    # Verificar se é uma imagem válida
                    img.verify()
                
                # Reabrir para processamento
                with Image.open(io.BytesIO(file_data)) as img:
                    # Processar imagem com Gemini
                    response = gemini_client.generate_content([
                        prompt,
                        {"mime_type": file.content_type, "data": file_data}
                    ])
                    
        except Exception as e:
            logger.error(f"Erro no processamento do Gemini: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")
        
        # Processar resposta
        cleaned_response = response.text.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:].strip()
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3].strip()
        
        try:
            json_response = json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            logger.error(f"JSON inválido do Gemini: {cleaned_response}")
            raise HTTPException(status_code=500, detail="Resposta do Gemini em formato inválido")
        
        # Salvar no banco
        try:
            new_data = ExtractedData(
                cnpj=json_response.get("CNPJ", ""),
                cep=json_response.get("CEP", ""),
                data_emissao=json_response.get("Data de emissão", ""),
                valor_total=json_response.get("Valor total", "")
            )
            db.add(new_data)
            db.commit()
            db.refresh(new_data)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao salvar no banco: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro ao salvar dados")
        
        return json_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro interno: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno no servidor")