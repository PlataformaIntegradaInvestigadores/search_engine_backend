FROM python:3.11-bookworm

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["python", "manage.py", "runserver", "0.0.0.0:8001", "--noreload"]

