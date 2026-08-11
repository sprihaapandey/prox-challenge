# Multi-stage build. The Claude Agent SDK drives the Claude Code CLI (a Node
# binary) as a subprocess, so the runtime image needs both Python and Node —
# there's no way around that dependency, see README's "Why a CLI dependency?"

# --- Stage 1: build the frontend static assets -----------------------------
FROM node:22-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# --- Stage 2: runtime --------------------------------------------------------
FROM python:3.12-slim
WORKDIR /app

# Node, for the Claude Agent SDK's CLI subprocess
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/package.json backend/package-lock.json backend/
RUN cd backend && npm ci --omit=dev

COPY backend/ backend/
COPY data/ data/
COPY --from=frontend-build /app/frontend/dist frontend/dist

# The Claude Code CLI refuses to run with --dangerously-skip-permissions as
# root/sudo (a safety guard) — Cloud Run and most container platforms run as
# root by default, so a dedicated non-root user is required, not optional.
RUN useradd --create-home --shell /bin/bash appuser && chown -R appuser:appuser /app
USER appuser

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "backend.main:app", "--app-dir", ".", "--host", "0.0.0.0", "--port", "8000"]
