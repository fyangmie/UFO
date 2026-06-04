FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=7860
ENV UFO_BACKEND_PORT=8000
ENV UFO_BACKEND_URL=http://127.0.0.1:8000

COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x scripts/start_cloud.sh

EXPOSE 7860

CMD ["bash", "scripts/start_cloud.sh"]
