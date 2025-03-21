from http import HTTPStatus

from fastapi import FastAPI

from .schemas import Message  


app = FastAPI()

@app.get('/', status_code=HTTPStatus.OK, response_model=message)
def home():
    return {"message": "pedro dias"}







