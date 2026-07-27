# CareerCompass AI — Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

# database/ is bind-mounted via docker-compose in development so career.db persists
# outside the container. Created here too so the path exists on first boot.
RUN mkdir -p /app/database

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
