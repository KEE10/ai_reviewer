# Builder
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip setuptools wheel poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install --only main --no-root

COPY . .

# Run
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.cache/pypoetry/virtualenvs /opt/venv_cache

RUN cp -r /opt/venv_cache/*/. /opt/venv && rm -rf /opt/venv_cache

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY --from=builder /app/domain ./domain
COPY --from=builder /app/shared ./shared
COPY --from=builder /app/main.py .
COPY --from=builder /app/config.py .

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app /opt/venv && \
    chmod -R u+x /opt/venv/bin/

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health').read()" || exit 1

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]