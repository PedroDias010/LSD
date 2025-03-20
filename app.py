from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def home():
    return {"message": "pedro dias"}

@app.get('/teste')
def home():
    return {"message": "almoço"}



