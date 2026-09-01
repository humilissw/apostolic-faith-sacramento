# ---- Build stage ----
FROM python:3.12-slim AS builder

RUN pip install --no-cache-dir poetry==2.2.1

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md && poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi --no-root

COPY . .

# ---- Production stage ----
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . .

# Ensure a self-signed localhost TLS cert exists for HTTPS-only serving. If the
# build context already carries security_keys/cert.pem + key.pem they are used
# as-is; otherwise generate one so a fresh clone builds and runs out of the box.
RUN mkdir -p /app/security_keys \
    && if [ ! -f /app/security_keys/cert.pem ] || [ ! -f /app/security_keys/key.pem ]; then \
        openssl req -x509 -newkey rsa:4096 \
            -keyout /app/security_keys/key.pem \
            -out /app/security_keys/cert.pem \
            -sha256 -days 3650 -nodes \
            -subj "/CN=localhost" \
            -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"; \
        fi \
    && chmod 600 /app/security_keys/key.pem

RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app/security_keys
USER appuser

# BFF serves HTTPS only (no plain HTTP). Port 8002 avoids the backend (8000)
# and health-edge (8001).
EXPOSE 8002

CMD ["python", "-m", "app"]
