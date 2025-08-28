from dotenv import load_dotenv
import os
import google.generativeai as genai

# Forçar codificação UTF-8 ao carregar variáveis de ambiente
load_dotenv(encoding='utf-8')

# Configurações do banco de dados
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "myextracao")
DB_USER = os.getenv("DB_USER", "userextracao")
DB_PASS = os.getenv("DB_PASS", "extracao")
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"

# Configuração do Google Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")



genai.configure(api_key=GEMINI_API_KEY)
gemini_client = genai.GenerativeModel('gemini-2.5-flash')
