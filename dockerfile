FROM python:latest

WORKDIR /LSD

COPY requirements.txt .

RUN pip install uvicorn

RUN pip install --no-cache-dir -r requirements.txts

COPY . .

EXPOSE 8000

 CMD [ "uvicorn app:application --host 0.0.0.0 --port 8000" ]