# Dockerfile für goldanker_commands

FROM python:3.11-slim

# Arbeitsverzeichnis im Container
WORKDIR /app

# requirements.txt kopieren und Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projektdateien kopieren
COPY . .

# Port angeben (optional)
EXPOSE 8000

# Startbefehl für Uvicorn (FastAPI Server)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
