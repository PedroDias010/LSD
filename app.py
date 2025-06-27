from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv
import json
import io
from pypdf import PdfReader
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import time
from LSD.models import ExtractedData, table_registry
import uvicorn
from contextlib import asynccontextmanager

load_dotenv()

app = FastAPI()

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

ALLOWED_TYPES = {"image/jpeg", "image/png", "application/pdf"}

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "mydatabase")
DB_USER = os.getenv("DB_USER", "myuser")
DB_PASS = os.getenv("DB_PASS", "mypassword")
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"

engine = None
SessionLocal = None

def create_engine_with_retry(url, max_attempts=5, delay=5):
    for attempt in range(max_attempts):
        try:
            engine = create_engine(url, echo=True)
            engine.connect()
            return engine
        except OperationalError as e:
            if attempt < max_attempts - 1:
                print(f"Tentativa {attempt + 1} falhou: {e}. Tentando novamente em {delay}s...")
                time.sleep(delay)
            else:
                raise Exception(f"Falha ao conectar ao banco após {max_attempts} tentativas: {2}")

def init_db_engine():
    global engine, SessionLocal
    if engine is None:
        engine = create_engine_with_retry(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine

def init_db():
    table_registry.metadata.create_all(init_db_engine())

def get_db():
    init_db_engine()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root(db: get_db = Depends(get_db)):
    result = db.execute("SELECT 1 AS number").fetchone()
    return {"message": "Conexão com PostgreSQL OK", "result": {"number": result[0]}}

def extract_pdf(pdf_data):
    try:
        pdf_reader = PdfReader(io.BytesIO(pdf_data))
        if not pdf_reader.pages:
            return ""
        text = ""
        for page in pdf_reader.pages:
            extracted_text = page.extract_text() or ""
            text += extracted_text
        return text
    except Exception as e:
        raise Exception(f"Erro ao extrair texto do PDF: {str(e)}")

@app.post("/extract-data/")
async def extract_data(file: UploadFile = File(...), db: get_db = Depends(get_db)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Apenas PNG, JPEG ou PDF são permitidos")
    try:
        file_data = await file.read()
        prompt = """
        Analise o conteúdo fornecido e extraia os seguintes dados em formato JSON:
        - CNPJ (formato XX.XXX.XXX/XXXX-XX)
        - CEP (formato XXXXX-XXX)
        - Data de emissão (formato DD/MM/AAAA HH:MM:SS)
        - Valor total (formato R$ X,XX)
        Retorne apenas o JSON com os dados ou valores vazios se não encontrados.
        """
        if file.content_type == "application/pdf":
            text = extract_pdf(file_data)
            if not text:
                raise HTTPException(status_code=400, detail="PDF inválido ou sem conteúdo extraível")
            response = model.generate_content([prompt, text])
        else:
            try:
                img = Image.open(io.BytesIO(file_data))
                img.close()
                response = model.generate_content([prompt, img])
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Arquivo de imagem inválido: {str(e)}")
        cleaned_response = response.text.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:].strip()
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3].strip()
        try:
            json_response = json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Erro ao parsear resposta do Gemini: {str(e)}")
        try:
            new_data = ExtractedData(
                cnpj=json_response.get("CNPJ", ""),
                cep=json_response.get("CEP", ""),
                data_emissao=json_response.get("Data de emissão", ""),
                valor_total=json_response.get("Valor total", "")
            )
            db.add(new_data)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Erro ao salvar no banco: {str(e)}")
        return json_response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
    
    
    
    
    
    
    
    
    
    