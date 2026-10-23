FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8080

WORKDIR /app

RUN useradd --uid 10001 --user-group --no-create-home --shell /usr/sbin/nologin appuser

COPY --chown=10001:10001 app/ ./app/

USER 10001:10001

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=2)"]

CMD ["python", "app/server.py"]
