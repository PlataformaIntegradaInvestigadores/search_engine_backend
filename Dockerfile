FROM python:3.11-slim-bookworm

# Optimizaciones de Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema (build-essential para compilar librerías de ML si es necesario)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8001

# Para producción, se recomienda usar gunicorn o uvicorn en lugar de runserver
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001", "--noreload"]

