from fastapi import FastAPI

app = FastAPI()

@app.get('/teste')
def read_root():
    return {'message': 'Olá Mundo!'}