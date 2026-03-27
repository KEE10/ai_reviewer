# # Builder
# FROM python:3.11-slim AS builder

# WORKDIR /app

# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     && rm -rf /var/lib/apt/lists/*

# RUN pip install --no-cache-dir --upgrade pip setuptools wheel
# RUN pip install --no-cache-dir poetry

# COPY pyproject.toml poetry.lock extract_venv.py ./

# RUN poetry install --only main --no-root

# # Work around due to poetry bug creating a virtualenv, open issue: https://github.com/python-poetry/poetry/issues/6459
# # extract the created virtualenv by poetry and copy it to /opt/venv
# # TODO: move this script outside of dockerfile for better lisibility
# # RUN python -c "import os, shutil; cache_dir = '/root/.cache/pypoetry/virtualenvs'; venvs = [d for d in os.listdir(cache_dir) if os.path.isdir(os.path.join(cache_dir, d))]; src = os.path.join(cache_dir, venvs[0]) if venvs else None; src and shutil.copytree(src, '/opt/venv')"
# RUN ls -la /root/.cache/pypoetry/virtualenvs/ || echo "No virtualenvs found"
# RUN poetry show || echo "Poetry show failed"
# # COPY extract_venv ./
# RUN python -m extract_venv
# # Debug: Check if venv was created
# RUN ls -la /opt/venv/bin/ || echo "venv/bin not found"
# RUN which uvicorn || echo "uvicorn not found in PATH"

# COPY . .

# # Run
# FROM python:3.11-slim

# WORKDIR /app

# RUN apt-get update && apt-get install -y --no-install-recommends \
#     ca-certificates \
#     && rm -rf /var/lib/apt/lists/*

# COPY --from=builder /opt/venv /opt/venv
# RUN ls -la /opt/venv/bin/uvicorn
# RUN chmod +x /opt/venv/bin/uvicorn
# ENV PATH="/opt/venv/bin:$PATH" \
#     PYTHONUNBUFFERED=1 \
#     PYTHONDONTWRITEBYTECODE=1

# COPY --from=builder /app/domain ./domain
# COPY --from=builder /app/shared ./shared
# COPY --from=builder /app/main.py .
# COPY --from=builder /app/config.py .

# RUN useradd -m -u 1000 appuser && \
#     chown -R appuser:appuser /app /opt/venv && \
#     chmod -R u+x /opt/venv/bin/

# USER appuser

# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health').read()" || exit 1

# EXPOSE 8000

# CMD ["/opt/venv/bin/python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# Builder
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip setuptools wheel poetry

COPY pyproject.toml poetry.lock ./

# Simple approach: just install with poetry
RUN poetry install --only main --no-root

COPY . .

# Run
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire /root/.cache/pypoetry/virtualenvs directory
COPY --from=builder /root/.cache/pypoetry/virtualenvs /opt/venv_cache

# Find and copy the venv (simpler, no Python script needed)
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