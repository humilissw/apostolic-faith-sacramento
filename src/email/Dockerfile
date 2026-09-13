# ---- Build stage ----
FROM python:3.14-bookworm AS builder

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml README.md ./
RUN uv pip install --system -r pyproject.toml --no-cache

COPY . .

# ---- Production stage ----
FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && mkdir -p /app/security_keys /app/data \
    && chown -R appuser:appuser /app/security_keys /app/data
USER appuser

EXPOSE 8100
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8100"]
