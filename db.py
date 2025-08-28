from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from config import DATABASE_URL
from models import table_registry
import time

def create_engine_with_retry(url, max_attempts=5, delay=5):
    print(f"DATABASE_URL: {url}")
    print(f"DATABASE_URL bytes: {url.encode('utf-8', errors='replace')}")
    
    for attempt in range(max_attempts):
        try:
            engine = create_engine(url, echo=True)
            with engine.connect() as conn:
                print("Conexão com o banco de dados estabelecida com sucesso!")
            return engine
        except OperationalError as e:
            if "database \"myextracao\" does not exist" in str(e):
                raise Exception("Banco de dados 'myextracao' não existe. Crie o banco com: psql -h localhost -U postgres -d postgres -c 'CREATE DATABASE myextracao;'")
            if "password authentication failed" in str(e):
                raise Exception("Falha na autenticação. Verifique o usuário e a senha no arquivo .env ou redefina a senha do PostgreSQL.")
            if "permission denied" in str(e):
                raise Exception("Permissão negada. Conceda permissões com: psql -h localhost -U postgres -d postgres -c 'GRANT ALL PRIVILEGES ON DATABASE myextracao TO userextracao;'")
            if attempt < max_attempts - 1:
                print(f"Tentativa {attempt + 1} falhou: {e}. Tentando novamente em {delay}s...")
                time.sleep(delay)
            else:
                raise Exception(f"Falha ao conectar ao banco após {max_attempts} tentativas: {e}")
        except Exception as e:
            if "UnicodeDecodeError" in str(e):
                raise Exception("Erro de codificação na conexão com o banco. Verifique se o arquivo .env está em UTF-8 e se a senha não contém caracteres especiais.")
            raise

# Criar engine com retry
engine = create_engine_with_retry(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    try:
        table_registry.metadata.create_all(engine)
        print("Tabelas criadas com sucesso!")
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")
        raise

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()