# Backend image. Build context = repo root (needs the uv workspace files, backend/ and contracts/):
#   docker build -f backend/Dockerfile .
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_PROJECT_ENVIRONMENT=/opt/venv PATH=/opt/venv/bin:$PATH \
    ARGUS_CONTRACTS_DIR=/srv/contracts
RUN pip install --no-cache-dir uv
WORKDIR /srv
COPY pyproject.toml uv.lock ./
COPY backend/pyproject.toml backend/pyproject.toml
RUN mkdir -p backend/app && touch backend/app/__init__.py \
 && uv sync --frozen --no-dev --no-install-workspace
COPY backend backend
COPY contracts contracts
RUN uv sync --frozen --no-dev
EXPOSE 8000
# Migrations -> demo seed -> API
CMD ["sh", "-c", "alembic -c backend/alembic.ini upgrade head && python -m app.seed && uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000"]
