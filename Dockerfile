# Multi-stage build for the FastAPI backend.
# Stage 1: install deps into a slim venv-like layout.
# Stage 2: copy code + venv into a runtime image as a non-root user.

FROM python:3.11-slim AS builder

# OpenCV / Pillow want libgl + libglib; install once, copy from builder to runtime.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt ./
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Runtime-only system libs (OpenCV needs libgl; Postgres driver needs libpq).
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN groupadd --system app && useradd --system --gid app --create-home --home-dir /app app

WORKDIR /app

# Copy the prebuilt venv from the builder
COPY --from=builder /install /usr/local

# Copy application code
COPY --chown=app:app app ./app
COPY --chown=app:app alembic ./alembic
COPY --chown=app:app alembic.ini ./alembic.ini
COPY --chown=app:app start.sh ./start.sh
RUN chmod +x ./start.sh

# Local-upload fallback lives on a mounted volume in production
RUN mkdir -p /app/uploads && chown -R app:app /app

USER app

EXPOSE 8000

# Healthcheck — pings the liveness route every 30s.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request,sys; \
sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health', timeout=3).status == 200 else 1)"

CMD ["./start.sh"]
