from fastapi import FastAPI, UploadFile, HTTPException

app = FastAPI()

@app.post("/extract/")
def extract_fields(image: UploadFile | None = None):
    if not image:
        raise HTTPException(status_code=400, detail="Nenhuma imagem enviada")
    return {"status": "Imagem recebida", "filename": image.filename, "fields": {}}

@app.get("/extract/")
def get_extract_info():
    return {"message": "Use POST para enviar uma imagem"}