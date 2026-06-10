FROM python:3.11-slim

RUN useradd -m -u 1000 user

USER user

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOME=/home/user
ENV PATH=/home/user/.local/bin:$PATH
ENV PORT=7860
ENV UFO_BACKEND_PORT=8000
ENV UFO_BACKEND_URL=http://127.0.0.1:8000

WORKDIR $HOME/app

COPY --chown=user:user requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY --chown=user:user . .

RUN chmod +x scripts/start_cloud.sh

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=5s --start-period=45s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:7860/', timeout=3)" || exit 1

CMD ["bash", "scripts/start_cloud.sh"]
