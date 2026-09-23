FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_PROJECT_ENVIRONMENT=/opt/venv PATH=/opt/venv/bin:$PATH
RUN pip install --no-cache-dir uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY alembic.ini ./
COPY backend ./backend
COPY simulator ./simulator
COPY contracts ./contracts
EXPOSE 8000
# Migrations (all module branches) -> demo seed -> API
CMD ["sh", "-c", "alembic upgrade heads && python -m backend.seed && uvicorn backend.core.app:create_app --factory --host 0.0.0.0 --port 8000"]
