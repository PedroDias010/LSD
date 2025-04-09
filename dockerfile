FROM python:latest

WORKDIR /LSD

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

 CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]